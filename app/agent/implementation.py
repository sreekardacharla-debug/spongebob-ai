import json

from app.llm.service import ModelService
from app.security.identity import Identity
from app.tools.filesystem import FileSystemTool


identity = Identity(user_id="owner", principal="owner")
model_service = ModelService(identity=identity)


def _extract_json(text: str) -> dict:
    """
    Extract a JSON object from the model response.
    """

    text = text.strip()

    # Remove Markdown code fences if the model adds them.
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

        json_text = text[start:end + 1]

        try:
            return json.loads(json_text)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Model returned malformed JSON."
            ) from exc


def _validate_operations(data: dict) -> list[dict]:
    """
    Validate operations returned by the model.

    Currently supported:
    - create_file
    - update_file
    - create_directory
    """

    if not isinstance(data, dict):
        raise ValueError(
            "Implementation response must be a JSON object."
        )

    operations = data.get("operations")

    if not isinstance(operations, list):
        raise ValueError(
            "Implementation response must contain an operations list."
        )

    validated = []

    for operation in operations:

        if not isinstance(operation, dict):
            raise ValueError(
                "Each operation must be an object."
            )

        action = operation.get("action")
        path = operation.get("path")

        if action not in {
            "create_file",
            "update_file",
            "create_directory",
        }:
            raise ValueError(
                f"Unsupported filesystem action: {action}"
            )

        if not isinstance(path, str) or not path.strip():
            raise ValueError(
                "Every operation must contain a valid path."
            )

        # Reject absolute paths.
        if path.startswith("/") or path.startswith("\\"):
            raise ValueError(
                f"Absolute paths are not allowed: {path}"
            )

        # Reject Windows drive paths such as C:\...
        if len(path) >= 2 and path[1] == ":":
            raise ValueError(
                f"Absolute paths are not allowed: {path}"
            )

        if action in {
            "create_file",
            "update_file",
        }:

            content = operation.get("content")

            if not isinstance(content, str):
                raise ValueError(
                    f"{action} requires string content: {path}"
                )

            validated.append(
                {
                    "action": action,
                    "path": path,
                    "content": content,
                }
            )

        else:

            validated.append(
                {
                    "action": action,
                    "path": path,
                }
            )

    return validated


def _build_prompt(
    architecture_plan: dict,
    project_context: dict,
    environment_context: dict,
) -> str:
    """
    Ask the model to convert the architecture plan
    into concrete filesystem operations.
    """

    plan_json = json.dumps(
        architecture_plan,
        indent=2,
    )

    project_json = json.dumps(
        project_context,
        indent=2,
    )

    environment_json = json.dumps(
        environment_context,
        indent=2,
    )

    return f"""
You are the implementation agent for SpongeBob AI.

Your job is to convert the supplied architecture plan
into concrete filesystem operations.

You DO NOT execute commands yourself.

You ONLY return a structured implementation plan.

ARCHITECTURE PLAN:
{plan_json}

==================================================
CURRENT PROJECT CONTEXT
==================================================

{project_json}

==================================================
CURRENT ENVIRONMENT CONTEXT
==================================================

{environment_json}

==================================================
OUTPUT FORMAT
==================================================

Return ONLY one valid JSON object.

The JSON must have this structure:

{{
  "operations": [
    {{
      "action": "create_file",
      "path": "relative/path/to/file",
      "content": "complete file content"
    }},
    {{
      "action": "update_file",
      "path": "relative/path/to/existing/file",
      "content": "complete new file content"
    }},
    {{
      "action": "create_directory",
      "path": "relative/path"
    }}
  ]
}}

==================================================
OPERATION RULES
==================================================

1. Only use these actions:

   - create_file
   - update_file
   - create_directory

2. Use create_file when a new file needs to be created.

3. Use update_file when an existing file needs to be modified.

4. Use create_directory when a new directory needs to be created.

5. All paths must be relative paths.

6. Never use absolute paths.

7. Respect the CURRENT PROJECT CONTEXT.

   - Treat detected frameworks, languages, build tools, and existing files as important environment facts.
   - Prefer extending the existing project rather than replacing its technology stack.
   - Do not replace an existing framework or project structure unless the architecture plan explicitly requires it.
   - Do not recreate an existing file as create_file.
   - Use update_file when an existing file needs to change.
   - Modify the smallest reasonable set of existing files.
   - Do not rewrite unrelated files.
   - Do not introduce new dependencies unless they are required by the architecture plan.
   - Do not invent technologies, services, databases, or configuration that are absent from the architecture plan and project context.

8. Respect the CURRENT ENVIRONMENT CONTEXT.

   - Do not assume a runtime, package manager, CLI tool, database, or other tool is installed unless the environment context indicates it.
   - If setup is required because a required tool is unavailable, follow the architecture plan's environment decisions.
   - Keep implementation compatible with the detected environment.

9. When the architecture plan conflicts with the current project:

   - Prefer the architecture plan for the requested feature.
   - Preserve unrelated existing project structure.
   - Make the minimum necessary changes to reconcile the conflict.
   - Do not silently rebuild the entire project.

10. Never use:

   - delete_file
   - delete_directory
   - move
   - copy
   - shell commands
   - terminal commands

8. Create complete file contents.

9. Do not create snippets or partial files.

10. Implement the architecture plan faithfully.

11. Create every file listed in files_to_create.

12. Only modify files that are listed in files_to_modify
    or are clearly required by the architecture plan.

13. Do not create unrelated files.

14. Do not invent external services.

15. Do not invent dependencies that are not required
    by the architecture plan.

==================================================
JSON SAFETY RULES
==================================================

16. The entire response MUST be valid JSON.

17. The response MUST be directly parseable by:

    Python json.loads()

18. File content is a JSON string value.

19. Escape newline characters inside JSON string values
    as \\n.

20. Escape tab characters inside JSON string values
    as \\t.

21. Escape backslashes inside JSON string values
    as \\\\.

22. Escape double quotes inside JSON string values
    as \\".

23. Never place raw newline characters inside a JSON
    string value.

24. Never place unescaped double quotes inside a JSON
    string value.

25. Do not use Markdown code fences.

26. Do not add explanations before or after the JSON.

27. Return JSON only.

==================================================
ARCHITECTURE CONSISTENCY
==================================================

28. The implementation must match the architecture plan.

29. Do not silently change the architecture.

30. Do not add technologies that are not in the plan.

31. Do not add pages, components, services, databases,
    APIs, or dependencies that are not required.

32. Make sure every file in files_to_create is represented
    by an appropriate create_file operation.

33. Make sure every file in files_to_modify is represented
    by an appropriate update_file operation when modification
    is required.

34. Before returning the JSON, internally verify that:

    architecture plan
          ↔
    operations
          ↔
    files_to_create
          ↔
    files_to_modify

    all describe the same implementation.

==================================================
FINAL REQUIREMENT
==================================================

Return ONLY valid JSON.

No Markdown.

No explanations.

No code fences.

No comments outside JSON.

The response must be directly parseable using
Python json.loads().
""".strip()


def create_implementation_plan(
    architecture_plan: dict,
    project_context: dict,
    environment_context: dict,
) -> dict:
    """
    Ask the model for a structured implementation plan.
    """

    prompt = _build_prompt(
        architecture_plan,
        project_context,
        environment_context,
    )

    raw_result = model_service.generate(prompt)

    data = _extract_json(
        raw_result
    )

    operations = _validate_operations(
        data
    )

    return {
        "operations": operations,
    }


def execute_implementation(
    architecture_plan: dict,
    workspace: str,
    project_context: dict,
    environment_context: dict,
) -> tuple[list[dict], list[dict]]:
    """
    Generate and execute implementation operations.

    Returns:

        execution_results
        execution_errors
    """

    implementation = create_implementation_plan(
        architecture_plan,
        project_context,
        environment_context,
    )

    filesystem = FileSystemTool(
        workspace
    )

    results = []
    errors = []

    for operation in implementation["operations"]:

        action = operation["action"]
        path = operation["path"]

        try:

            if action == "create_file":

                # CREATE means the file must not already exist.
                try:
                    filesystem.read_file(path)

                    raise FileExistsError(
                        f"Cannot create file because it already exists: {path}"
                    )

                except FileNotFoundError:
                    pass

                filesystem.write_file(
                    path,
                    operation["content"],
                )

                results.append(
                    {
                        "action": action,
                        "path": path,
                        "success": True,
                    }
                )

            elif action == "update_file":

                # UPDATE means the file must already exist.
                try:
                    old_content = filesystem.read_file(
                        path
                    )

                except FileNotFoundError:
                    raise FileNotFoundError(
                        f"Cannot update missing file: {path}"
                    )

                new_content = operation["content"]

                filesystem.write_file(
                    path,
                    new_content,
                )

                if old_content == new_content:
                    raise ValueError(
                        f"Update produced no content change: {path}"
                    )

                results.append(
                    {
                        "action": action,
                        "path": path,
                        "success": True,
                    }
                )

            elif action == "create_directory":

                # CREATE DIRECTORY means the directory
                # must not already exist.
                target_exists = False

                try:
                    filesystem.list_directory(
                        path
                    )
                    target_exists = True

                except FileNotFoundError:
                    target_exists = False

                if target_exists:
                    raise FileExistsError(
                        f"Directory already exists: {path}"
                    )

                filesystem.create_directory(
                    path
                )

                results.append(
                    {
                        "action": action,
                        "path": path,
                        "success": True,
                    }
                )

        except Exception as exc:

            errors.append(
                {
                    "action": action,
                    "path": path,
                    "success": False,
                    "error": str(exc),
                }
            )

    return results, errors
