import json

from app.llm.router import ModelRouter


router = ModelRouter()


VALID_ACTIONS = {
    "ASK_USER",
    "INFER",
    "CHOOSE_FOR_USER",
    "INSPECT_ENVIRONMENT",
    "CONTINUE_PLANNING",
}


def analyze_requirements(
    user_input: str,
    project_type: str,
    current_requirements: dict,
    user_facts: dict | None = None,
    delegated_decisions: list | None = None,
    inferences: dict | None = None,
    unknowns: list | None = None,
    blocking_unknowns: list | None = None,
) -> dict:

    user_facts = user_facts or {}
    delegated_decisions = delegated_decisions or []
    inferences = inferences or {}
    unknowns = unknowns or []
    blocking_unknowns = blocking_unknowns or []

    prompt = f"""
You are the Goal and Decision Reasoner for SpongeBob AI.

Your job is to determine whether SpongeBob has enough information
to continue toward implementation.

You are NOT a questionnaire.

IMPORTANT:

1. Never invent something the user did not say and label it as a
   user requirement.

2. Separate information into:
   - USER_STATED
   - USER_DELEGATED
   - INFERRED
   - UNKNOWN

3. Technical decisions can usually be made by SpongeBob later.

4. Do not ask about frameworks, libraries, databases, architecture,
   styling, folder structure, or implementation details unless they
   are genuinely blocking progress.

5. Missing personal content does NOT automatically block technical
   planning.

   Example:
   "Build me a portfolio website."

   The user's name, biography, projects, images, etc. may be unknown,
   but SpongeBob can still design and scaffold the application using
   placeholders.

6. A missing item is BLOCKING only when SpongeBob cannot reasonably
   proceed toward the user's goal without it.

7. If the user explicitly delegates a decision to SpongeBob, mark it
   as USER_DELEGATED.

8. If SpongeBob can safely choose a technical decision itself,
   use CHOOSE_FOR_USER.

9. If the environment needs to be inspected before deciding something,
   use INSPECT_ENVIRONMENT.

10. If something can be derived safely from existing information,
    use INFER.

11. If there are no genuinely blocking unknowns, use
    CONTINUE_PLANNING.

12. If a genuinely user-specific decision is required and cannot be
    reasonably deferred, use ASK_USER.

13. The fields MUST be logically consistent.

    If blocking_unknowns is not empty:
        requirements_complete MUST be false.

    If requirements_complete is false:
        action MUST NOT be CONTINUE_PLANNING unless the blocking
        unknown can actually be resolved by another action.

    If there are no blocking unknowns:
        requirements_complete should normally be true and action
        should normally be CONTINUE_PLANNING.

14. Do not add optional features such as blogs, testimonials,
    authentication, SEO, analytics, dark mode, etc. unless the user
    requests them or they become necessary for the goal.

USER REQUEST:
{user_input}

PROJECT TYPE:
{project_type}

CURRENT REQUIREMENTS:
{json.dumps(current_requirements, indent=2)}

KNOWN USER FACTS:
{json.dumps(user_facts, indent=2)}

DELEGATED DECISIONS:
{json.dumps(delegated_decisions, indent=2)}

PREVIOUS INFERENCES:
{json.dumps(inferences, indent=2)}

KNOWN UNKNOWNS:
{json.dumps(unknowns, indent=2)}

PREVIOUS BLOCKING UNKNOWNS:
{json.dumps(blocking_unknowns, indent=2)}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "goal": "",
    "user_facts": {{}},
    "delegated_decisions": [],
    "inferences": {{}},
    "unknowns": [],
    "blocking_unknowns": [],
    "action": "CONTINUE_PLANNING",
    "requirements_complete": true,
    "next_question": "",
    "requirements": {{}},
    "reasoning": ""
}}
"""

    raw_result = router.generate(prompt)

    try:
        result = json.loads(raw_result)
    except json.JSONDecodeError:
        raise ValueError(
            f"Qwen returned invalid JSON:\n{raw_result}"
        )

    action = result.get("action")

    if action not in VALID_ACTIONS:
        raise ValueError(
            f"Invalid action returned by Qwen: {action}"
        )

    requirements_complete = result.get("requirements_complete")

    if not isinstance(requirements_complete, bool):
        raise ValueError(
            "requirements_complete must be true or false"
        )

    next_question = result.get("next_question", "")

    if not isinstance(next_question, str):
        raise ValueError(
            "next_question must be a string"
        )

    final_blocking_unknowns = result.get(
        "blocking_unknowns",
        [],
    )

    # Enforce consistency between blocking unknowns and completeness.
    if final_blocking_unknowns:
        requirements_complete = False

        if action == "CONTINUE_PLANNING":
            action = "ASK_USER"

    else:
        requirements_complete = True

        if action == "ASK_USER":
            action = "CONTINUE_PLANNING"

            next_question = ""

    return {
        "goal": result.get("goal", ""),
        "user_facts": result.get(
            "user_facts",
            {},
        ),
        "delegated_decisions": result.get(
            "delegated_decisions",
            [],
        ),
        "inferences": result.get(
            "inferences",
            {},
        ),
        "unknowns": result.get(
            "unknowns",
            [],
        ),
        "blocking_unknowns": final_blocking_unknowns,
        "action": action,
        "requirements_complete": requirements_complete,
        "next_question": next_question,
        "requirements": result.get(
            "requirements",
            {},
        ),
        "reasoning": result.get(
            "reasoning",
            "",
        ),
    }