from pathlib import Path

from app.tools.filesystem import FileSystemTool


def execute_fix_plan(
    fix_plan: dict,
    diagnosis: dict,
    workspace: str,
) -> tuple[list[dict], list[dict]]:
    """
    Safely execute a fix plan.

    Only update_file operations are allowed.
    Only files identified by the diagnosis may be modified.
    """

    filesystem = FileSystemTool(workspace)

    results = []
    errors = []

    operations = fix_plan.get("operations")

    if not isinstance(operations, list):
        raise ValueError(
            "Fix plan must contain an operations list."
        )

    affected_files = set(
        diagnosis.get("files_affected", [])
    )

    for operation in operations:

        action = operation.get("action")
        path = operation.get("path")
        content = operation.get("content")

        try:
            # ----------------------------------------
            # ACTION CHECK
            # ----------------------------------------

            if action != "update_file":
                raise PermissionError(
                    "Fix executor only allows update_file."
                )

            # ----------------------------------------
            # PATH CHECK
            # ----------------------------------------

            if not isinstance(path, str) or not path.strip():
                raise ValueError(
                    "Fix operation requires a valid path."
                )

            if path not in affected_files:
                raise PermissionError(
                    f"File was not identified by diagnosis: {path}"
                )

            # ----------------------------------------
            # ABSOLUTE PATH CHECK
            # ----------------------------------------

            if path.startswith("/") or path.startswith("\\"):
                raise PermissionError(
                    f"Absolute paths are not allowed: {path}"
                )

            if len(path) >= 2 and path[1] == ":":
                raise PermissionError(
                    f"Absolute paths are not allowed: {path}"
                )

            # ----------------------------------------
            # CONTENT CHECK
            # ----------------------------------------

            if not isinstance(content, str):
                raise ValueError(
                    f"Fix content must be a string: {path}"
                )

            # ----------------------------------------
            # EXISTENCE CHECK
            # ----------------------------------------

            try:
                old_content = filesystem.read_file(path)

            except FileNotFoundError:
                raise FileNotFoundError(
                    f"Cannot fix missing file: {path}"
                )

            # ----------------------------------------
            # NO-OP CHECK
            # ----------------------------------------

            if old_content == content:
                raise ValueError(
                    f"Fix produced no content change: {path}"
                )

            # ----------------------------------------
            # EXECUTE UPDATE
            # ----------------------------------------

            filesystem.write_file(
                path,
                content,
            )

            results.append({
                "action": action,
                "path": path,
                "success": True,
            })

        except Exception as exc:

            errors.append({
                "action": action,
                "path": path,
                "success": False,
                "error": str(exc),
            })

    return results, errors
