import json

from app.llm.qwen import QwenProvider


qwen = QwenProvider()


ALLOWED_INTENTS = {
    "general_question",
    "create_project",
    "modify_project",
    "debug_project",
    "explain_code",
    "run_project",
    "other",
}

ALLOWED_PROJECT_TYPES = {
    "web_application",
    "portfolio",
    "ecommerce",
    "dashboard",
    "api",
    "ai_application",
    "data_application",
    "mobile_application",
    "desktop_application",
    "cli_application",
    "other",
    "none",
}


def understand_request(user_input: str) -> dict:
    prompt = f"""
You are the request-understanding component of SpongeBob AI.

Analyze the user's request and return ONLY valid JSON.

Determine:

1. intent
2. project_type
3. needs_requirements

Possible intents:
- general_question
- create_project
- modify_project
- debug_project
- explain_code
- run_project
- other

Possible project types:
- web_application
- portfolio
- ecommerce
- dashboard
- api
- ai_application
- data_application
- mobile_application
- desktop_application
- cli_application
- other
- none

needs_requirements must be true or false.

User request:
{user_input}

Return exactly:

{{
  "intent": "...",
  "project_type": "...",
  "needs_requirements": true
}}
"""

    raw_result = qwen.generate(prompt)

    try:
        result = json.loads(raw_result)
    except json.JSONDecodeError:
        raise ValueError(
            f"Qwen returned invalid JSON:\n{raw_result}"
        )

    intent = result.get("intent")
    project_type = result.get("project_type")
    needs_requirements = result.get("needs_requirements")

    if intent not in ALLOWED_INTENTS:
        raise ValueError(f"Invalid intent returned by Qwen: {intent}")

    if project_type not in ALLOWED_PROJECT_TYPES:
        raise ValueError(
            f"Invalid project_type returned by Qwen: {project_type}"
        )

    if not isinstance(needs_requirements, bool):
        raise ValueError(
            "needs_requirements must be true or false"
        )

    return {
        "intent": intent,
        "project_type": project_type,
        "needs_requirements": needs_requirements,
    }