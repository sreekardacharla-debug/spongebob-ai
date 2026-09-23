import json
import re

from app.llm.service import ModelService
from app.security.identity import Identity


identity = Identity(user_id="owner", principal="owner")
model_service = ModelService(identity=identity)


def _extract_json(raw_result: str) -> dict:
    """
    Extract a JSON object from the model response.
    """

    text = raw_result.strip()

    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            f"Planner did not return a JSON object:\n{raw_result}"
        )

    json_text = text[start:end + 1]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Planner returned malformed JSON.\n"
            f"JSON error: {exc}\n\n"
            f"Raw response:\n{raw_result}"
        ) from exc


def _validate_plan_consistency(result: dict) -> None:
    """
    Validate important consistency rules in the architecture plan.
    """

    summary = result.get("architecture_summary", "").lower()

    files = result.get("files_to_create", [])

    html_files = [
        file
        for file in files
        if isinstance(file, str)
        and file.lower().endswith(".html")
    ]

    says_single_page = "single-page" in summary
    says_multi_page = "multi-page" in summary

    if says_single_page and says_multi_page:
        raise ValueError(
            "Planner contradiction: architecture summary says both "
            "single-page and multi-page."
        )

    if says_single_page and len(html_files) > 1:
        raise ValueError(
            "Planner contradiction: plan says single-page but "
            "creates multiple HTML pages."
        )


def _validate_user_claims(
    result: dict,
    user_facts: dict,
    delegated_decisions: list,
) -> None:
    """
    Prevent the planner from inventing user preferences,
    permissions, capabilities, or decisions.
    """

    text_parts = [
        result.get("architecture_summary", ""),
        result.get("frontend", {}).get("reason", ""),
        result.get("backend", {}).get("reason", ""),
        result.get("database", {}).get("reason", ""),
        *result.get("agent_decisions", []),
        *result.get("assumptions", []),
    ]

    generated_text = " ".join(
        str(part) for part in text_parts
    ).lower()

    user_fact_text = json.dumps(
        user_facts,
        ensure_ascii=False,
    ).lower()

    delegated_text = json.dumps(
        delegated_decisions,
        ensure_ascii=False,
    ).lower()

    suspicious_patterns = [
        "the user prefers",
        "user prefers",
        "the user is comfortable",
        "user is comfortable",
        "the user permits",
        "user permits",
        "the user can host",
        "user can host",
        "the user wants",
        "user wants",
    ]

    for pattern in suspicious_patterns:
        if pattern in generated_text:
            if (
                pattern not in user_fact_text
                and pattern not in delegated_text
            ):
                raise ValueError(
                    "Planner invented an unsupported user claim: "
                    f"{pattern!r}"
                )


def create_architecture_plan(
    goal: str,
    project_type: str,
    requirements: dict,
    user_facts: dict,
    delegated_decisions: list,
    inferences: dict,
    project_context: dict,
    environment_context: dict,
) -> dict:

    prompt = f"""
You are the Architecture Planner for SpongeBob AI.

Your job is to create a practical implementation plan.

You DO NOT execute commands.
You DO NOT create or modify files.
You ONLY produce an architecture and implementation plan.

==================================================
CORE RULES
==================================================

1. Respect explicit user requirements.

2. Never claim that the user requested something they did not request.

3. Separate:
   - user requirements
   - agent decisions
   - assumptions
   - environment facts

4. Technical choices are agent decisions unless the user explicitly
   specified them.

5. Do not invent user preferences.

6. IMPORTANT:
   An empty user_facts object means the user's preferences are UNKNOWN.
   It does NOT mean the user has no preferences.


7. EXISTING PROJECT TECHNOLOGY:
   When CURRENT PROJECT contains detected technologies or frameworks,
   treat those detections as important environment facts.

   Prefer extending and integrating with an existing project technology
   instead of replacing it unnecessarily.

   Examples:
   - If an existing Vite frontend is detected, prefer using that frontend.
   - If an existing Spring Boot backend is detected, prefer extending it.
   - If an existing MySQL database is detected, prefer using MySQL.
   - If Maven is detected, prefer the existing Maven build system.
   - If PostgreSQL is detected, do not introduce MySQL without a concrete reason.

   Do not claim that the user selected an existing technology unless
   user_facts or delegated_decisions explicitly says so.

   If the agent chooses to keep or extend an existing technology,
   record that reasoning in agent_decisions.

8. ENVIRONMENT AWARENESS:
   Use ENVIRONMENT facts when selecting implementation tools.

   Do not assume that a tool, runtime, package manager, database,
   or command is installed merely because it is commonly used.

   If an important dependency is unavailable, record the required
   installation or setup in environment_decisions.

9. MINIMIZE UNNECESSARY REPLACEMENT:
   For an existing project, prefer modifying the smallest reasonable
   set of files needed to satisfy the requirements.

   Do not rebuild an existing application from scratch unless the
   requirements or project condition justify it.

10. TECHNOLOGY CONSISTENCY:
    Frontend, backend, database, dependencies, files, implementation
    steps, and validation_plan must describe one internally consistent
    architecture.

    Do not select technologies that conflict with detected project
    facts without explaining the reason in agent_decisions.

7. If a preference is unknown:
   - choose a reasonable default when the agent can safely do so,
   - use a delegated decision when the user gave SpongeBob permission
     to choose,
   - infer it only when the inference is justified,
   - or identify it as requiring the user.

8. Never claim that the user has no preference merely because no
   preference was provided.

9. Do not introduce unnecessary technologies.

10. Do not introduce a backend unless server-side functionality is
    actually needed.

11. Do not introduce a database unless persistent application data is
    actually needed.

12. Do not introduce Docker unless it provides a real benefit.

13. Do not introduce authentication unless required.

14. Do not introduce optional features merely because they are common.

15. Prefer the smallest architecture that can properly satisfy the goal.

16. Existing project files must be treated carefully.
    Do not declare existing infrastructure irrelevant unless there is
    clear evidence that it is unrelated.

17. If the user's requested application should be created separately
    from SpongeBob itself, explicitly explain why and identify the
    intended location.

18. Use environment facts to determine what is actually available.

19. Do not assume a technology is installed merely because it is common.

20. If a decision cannot safely be made yet, put it in
    environment_decisions instead of inventing an answer.

21. The implementation plan must be executable by a later tool agent.

22. The architecture_summary, implementation_steps, files_to_create,
    and agent_decisions must describe the SAME architecture.

23. Never describe an application as single-page if the plan creates
    multiple separate HTML pages.

24. Never describe an application as multi-page if the plan contains
    only one HTML page unless multiple pages are implemented through
    another explicitly described mechanism.

 delegated_decisions, or the original requirements.
 25. SINGLE-PAGE ENFORCEMENT:
    If architecture_summary describes the application as single-page,
    files_to_create must contain exactly ONE .html file.

26. MULTI-PAGE ENFORCEMENT:
    If architecture_summary describes the application as multi-page,
    multiple HTML pages are allowed.

27. Choose ONE architecture before generating the JSON.
    Do not mix single-page and multi-page designs.

28. If the project is a simple portfolio and the user did not explicitly
    request multiple pages, a single HTML page is an acceptable default.

29. The number and type of files in files_to_create must match the
    architecture_summary and implementation_steps.

30. Before returning JSON, internally verify:
    architecture_summary ↔ files_to_create ↔ implementation_steps
    all describe the same architecture.

31. If a technology or implementation choice is made by SpongeBob,
    record it under agent_decisions.

32. If information is simply missing, do not turn the missing
    information into a statement about the user.

==================================================
USER INFORMATION
==================================================

GOAL:
{goal}

PROJECT TYPE:
{project_type}

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

USER FACTS:
{json.dumps(user_facts, indent=2)}

DELEGATED DECISIONS:
{json.dumps(delegated_decisions, indent=2)}

INFERENCES:
{json.dumps(inferences, indent=2)}

==================================================
PROJECT / ENVIRONMENT FACTS
==================================================

CURRENT PROJECT:
{json.dumps(project_context, indent=2)}

ENVIRONMENT:
{json.dumps(environment_context, indent=2)}

==================================================
OUTPUT
==================================================

Return ONLY one valid JSON object.

Do not use Markdown.
Do not use code fences.
Do not put comments inside the JSON.
Do not use unescaped quotation marks inside JSON string values.

Use exactly this structure:

{{
    "architecture_summary": "",
    "frontend": {{
        "needed": false,
        "technology": "",
        "reason": ""
    }},
    "backend": {{
        "needed": false,
        "technology": "",
        "reason": ""
    }},
    "database": {{
        "needed": false,
        "technology": "",
        "reason": ""
    }},
    "dependencies": [],
    "files_to_create": [],
    "files_to_modify": [],
    "files_to_delete": [],
    "implementation_steps": [],
    "environment_decisions": [],
    "agent_decisions": [],
    "assumptions": [],
    "risks": [],
    "validation_plan": []
}}

==================================================
OUTPUT QUALITY RULES
==================================================

Every value must be valid JSON.

Do not invent requirements.

Do not invent user preferences.

Do not invent user permissions.

Do not invent user capabilities.

Do not invent user decisions.

An empty user_facts object means UNKNOWN.

An empty delegated_decisions list means that the user has not
delegated decisions.

If the agent chooses a technology because it is appropriate,
put that choice in agent_decisions.

If the agent makes an implementation assumption, put it in
assumptions without attributing that assumption to the user.

For example, this is INVALID:

"The user prefers simplicity and performance."

if no such preference exists in user_facts.

This is VALID:

"The agent selected a simple implementation because it is
sufficient for the current requirements."

This is INVALID:

"The user can host the site statically."

if the user has not said that.

This is VALID:

"Static hosting is an available deployment option, but the
user's hosting preference is unknown."

This is INVALID:

"The user permits creation outside the current project."

if the user has not explicitly granted that permission.

This is VALID:

"The intended application location has not been specified."

Keep user facts, delegated decisions, agent decisions, inferences,
unknowns, assumptions, and environment facts separate.

Keep the architecture internally consistent.

Do not use quotation marks inside JSON strings unless they are
properly escaped.
"""

    raw_result = model_service.generate(prompt)

    result = _extract_json(raw_result)

    _validate_plan_consistency(result)

    _validate_user_claims(
        result,
        user_facts,
        delegated_decisions,
    )

    required_keys = {
        "architecture_summary",
        "frontend",
        "backend",
        "database",
        "dependencies",
        "files_to_create",
        "files_to_modify",
        "files_to_delete",
        "implementation_steps",
        "environment_decisions",
        "agent_decisions",
        "assumptions",
        "risks",
        "validation_plan",
    }

    missing_keys = required_keys - result.keys()

    if missing_keys:
        raise ValueError(
            f"Planner response is missing keys: "
            f"{sorted(missing_keys)}"
        )

    return result
