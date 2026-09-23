import json

from app.llm.service import ModelService
from app.security.identity import Identity


identity = Identity(user_id="owner", principal="owner")
model_service = ModelService(identity=identity)


def _extract_json(text: str) -> dict:
    """
    Extract a JSON object from the model response.
    """

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.startswith("json"):
            text = text[4:].strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "Model did not return a valid JSON object."
            )

        try:
            return json.loads(
                text[start:end + 1]
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Model returned malformed JSON."
            ) from exc


def create_fix_plan(
    architecture_plan: dict,
    diagnosis: dict,
    project_context: dict,
) -> dict:
    """
    Ask the model to create a minimal fix plan.

    The model does not execute the fix.
    """

    prompt = f"""
You are the fix-planning agent for SpongeBob AI.

Your job is to convert a diagnosed software problem
into the smallest safe filesystem changes required
to fix the problem.

You DO NOT execute commands.

You DO NOT modify files.

You ONLY return a structured fix plan.

ARCHITECTURE PLAN:
{json.dumps(architecture_plan, indent=2)}

DIAGNOSIS:
{json.dumps(diagnosis, indent=2)}

PROJECT CONTEXT:
{json.dumps(project_context, indent=2)}

Return ONLY valid JSON.

Use exactly this structure:

{{
  "operations": [
    {{
      "action": "update_file",
      "path": "relative/path/to/file",
      "content": "complete new file content"
    }}
  ]
}}

Rules:

1. Only use update_file.

2. Only modify files identified by the diagnosis.

3. All paths must be relative paths.

4. Never use absolute paths.

5. Never use delete operations.

6. Never use shell commands.

7. Never invent files.

8. Never invent dependencies.

9. Preserve the existing architecture.

10. Make the smallest change necessary to fix
    the diagnosed problem.

11. The content field must contain the complete
    new file content, not a snippet.

12. Return JSON only.

13. Do not use Markdown.

14. Do not add explanations outside the JSON.
""".strip()

    raw_result = model_service.generate(prompt)

    data = _extract_json(raw_result)

    if not isinstance(data, dict):
        raise ValueError(
            "Fix plan must be a JSON object."
        )

    operations = data.get("operations")

    if not isinstance(operations, list):
        raise ValueError(
            "Fix plan must contain an operations list."
        )

    validated = []

    affected_files = set(
        diagnosis.get("files_affected", [])
    )

    for operation in operations:

        if not isinstance(operation, dict):
            raise ValueError(
                "Each fix operation must be an object."
            )

        action = operation.get("action")
        path = operation.get("path")
        content = operation.get("content")

        if action != "update_file":
            raise ValueError(
                "Fix planner may only use update_file."
            )

        if not isinstance(path, str) or not path.strip():
            raise ValueError(
                "Fix operation requires a valid path."
            )

        if path not in affected_files:
            raise ValueError(
                f"Fix planner attempted to modify "
                f"an undiagnosed file: {path}"
            )

        if path.startswith("/") or path.startswith("\\"):
            raise ValueError(
                f"Absolute paths are not allowed: {path}"
            )

        if len(path) >= 2 and path[1] == ":":
            raise ValueError(
                f"Absolute paths are not allowed: {path}"
            )

        if not isinstance(content, str):
            raise ValueError(
                f"Fix operation requires string content: {path}"
            )

        validated.append({
            "action": action,
            "path": path,
            "content": content,
        })

    return {
        "operations": validated,
    }
