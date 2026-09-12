from pathlib import Path


# Directories/files that should not be inspected recursively.
IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}


def inspect_project(project_root: str) -> dict:
    """
    Inspect the local project without modifying anything.

    Returns information about:
    - project root
    - files
    - directories
    - likely project types
    - important configuration files
    """

    root = Path(project_root).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Project root does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Project root is not a directory: {root}"
        )

    files = []
    directories = []

    for path in root.rglob("*"):
        relative = path.relative_to(root)

        # Skip anything inside ignored directories.
        if any(part in IGNORED_DIRECTORIES for part in relative.parts):
            continue

        if path.is_file():
            files.append(str(relative))

        elif path.is_dir():
            directories.append(str(relative))

    files.sort()
    directories.sort()

    important_files = {
        "package.json",
        "requirements.txt",
        "pyproject.toml",
        "Pipfile",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".env",
        ".gitignore",
        "README.md",
        "vite.config.js",
        "vite.config.ts",
        "next.config.js",
        "next.config.ts",
        "manage.py",
    }

    detected_files = sorted(
        file for file in files
        if Path(file).name in important_files
    )

    project_types = []

    if "package.json" in detected_files:
        project_types.append("javascript_or_node")

    if (
        "requirements.txt" in detected_files
        or "pyproject.toml" in detected_files
        or "Pipfile" in detected_files
        or "manage.py" in detected_files
    ):
        project_types.append("python")

    if (
        "vite.config.js" in detected_files
        or "vite.config.ts" in detected_files
    ):
        project_types.append("vite")

    if (
        "next.config.js" in detected_files
        or "next.config.ts" in detected_files
    ):
        project_types.append("nextjs")

    if "Dockerfile" in detected_files:
        project_types.append("docker")

    return {
        "project_root": str(root),
        "file_count": len(files),
        "directory_count": len(directories),
        "files": files,
        "directories": directories,
        "important_files": detected_files,
        "detected_project_types": project_types,
    }