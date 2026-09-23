from pathlib import Path


def validate_html_file(path: Path) -> tuple[bool, str]:
    """
    Perform basic validation on an HTML file.
    """

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False, "HTML file is not valid UTF-8 text."

    if not content.strip():
        return False, "HTML file is empty."

    content_lower = content.lower()

    if "<!doctype html>" not in content_lower:
        return False, "Missing <!DOCTYPE html>."

    if "<html" not in content_lower:
        return False, "Missing <html> element."

    if "<head" not in content_lower:
        return False, "Missing <head> element."

    if "<body" not in content_lower:
        return False, "Missing <body> element."

    if "</html>" not in content_lower:
        return False, "Missing closing </html> tag."

    return True, "Basic HTML structure is valid."


def validate_execution(
    project_root: str,
    execution_results: list[dict],
):
    """
    Validate implementation results at the filesystem
    and basic HTML-content level.
    """

    results = []
    validation_passed = True

    root = Path(project_root).resolve()

    for operation in execution_results:

        action = operation.get("action")
        path = operation.get("path")

        if not path:
            results.append({
                "success": False,
                "error": "Operation has no path.",
            })

            validation_passed = False
            continue

        target = (root / path).resolve()

        # Security check
        try:
            target.relative_to(root)

        except ValueError:
            results.append({
                "action": action,
                "path": path,
                "success": False,
                "error": "Path is outside project workspace.",
            })

            validation_passed = False
            continue

        # ----------------------------------------
        # FILE VALIDATION
        # ----------------------------------------

        if action in {
            "create_file",
            "update_file",
        }:

            valid = (
                target.exists()
                and target.is_file()
                and target.stat().st_size > 0
            )

            error = None

            if valid and target.suffix.lower() == ".html":
                valid, error = validate_html_file(target)

            results.append({
                "action": action,
                "path": path,
                "success": valid,
                "error": error,
            })

        # ----------------------------------------
        # DIRECTORY VALIDATION
        # ----------------------------------------

        elif action == "create_directory":

            valid = (
                target.exists()
                and target.is_dir()
            )

            results.append({
                "action": action,
                "path": path,
                "success": valid,
                "error": None if valid else "Directory does not exist.",
            })

        else:
            valid = False

            results.append({
                "action": action,
                "path": path,
                "success": False,
                "error": "Unsupported validation action.",
            })

        if not valid:
            validation_passed = False

    return results, validation_passed
