from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}


def inspect_project(project_root: str) -> dict:
    """
    Inspect the local project without modifying anything.

    Detects:
    - files and directories
    - JavaScript/Node projects
    - Python projects
    - Vite
    - Next.js
    - Java
    - Spring Boot
    - Maven
    - Gradle
    - MySQL
    - PostgreSQL
    - Docker
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

        if any(
            part in IGNORED_DIRECTORIES
            for part in relative.parts
        ):
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
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
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
        "application.properties",
        "application.yml",
        "application.yaml",
        "manage.py",
    }

    detected_files = sorted(
        file
        for file in files
        if Path(file).name in important_files
    )

    project_types = []

    file_names = {
        Path(file).name
        for file in files
    }

    file_suffixes = {
        Path(file).suffix.lower()
        for file in files
    }

    # JavaScript / Node
    if "package.json" in file_names:
        project_types.append("javascript_or_node")

    # Python
    if (
        "requirements.txt" in file_names
        or "pyproject.toml" in file_names
        or "Pipfile" in file_names
        or "manage.py" in file_names
        or ".py" in file_suffixes
    ):
        project_types.append("python")

    # Vite
    if (
        "vite.config.js" in file_names
        or "vite.config.ts" in file_names
    ):
        project_types.append("vite")

    # Next.js
    if (
        "next.config.js" in file_names
        or "next.config.ts" in file_names
    ):
        project_types.append("nextjs")

    # Java
    if ".java" in file_suffixes:
        project_types.append("java")

    # Maven
    if "pom.xml" in file_names:
        project_types.append("maven")

    # Gradle
    if (
        "build.gradle" in file_names
        or "build.gradle.kts" in file_names
    ):
        project_types.append("gradle")

    # Spring Boot
    spring_detected = False

    for file in files:
        path = root / file

        if path.name in {
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
            "application.properties",
            "application.yml",
            "application.yaml",
        }:
            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                ).lower()

                if (
                    "spring-boot" in content
                    or "springframework" in content
                    or "spring.datasource" in content
                ):
                    spring_detected = True

            except OSError:
                pass

    if spring_detected:
        project_types.append("spring_boot")

    # Database detection
    mysql_detected = False
    postgres_detected = False

    database_files = {
        "application.properties",
        "application.yml",
        "application.yaml",
        ".env",
        "docker-compose.yml",
        "docker-compose.yaml",
    }

    for file in files:
        path = root / file

        if path.name not in database_files:
            continue

        try:
            content = path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).lower()

            if (
                "mysql" in content
                or "jdbc:mysql" in content
            ):
                mysql_detected = True

            if (
                "postgres" in content
                or "postgresql" in content
                or "jdbc:postgresql" in content
            ):
                postgres_detected = True

        except OSError:
            pass

    if mysql_detected:
        project_types.append("mysql")

    if postgres_detected:
        project_types.append("postgresql")

    # Docker
    if (
        "Dockerfile" in file_names
        or "docker-compose.yml" in file_names
        or "docker-compose.yaml" in file_names
    ):
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
