from pathlib import Path

from app.project.inspector import inspect_project


def test_inspect_project_detects_python_and_vite(tmp_path: Path):
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "vite.config.js").write_text("")
    (tmp_path / "requirements.txt").write_text("")

    result = inspect_project(str(tmp_path))

    assert result["file_count"] == 3
    assert "package.json" in result["important_files"]
    assert "vite.config.js" in result["important_files"]
    assert "requirements.txt" in result["important_files"]

    assert "javascript_or_node" in result["detected_project_types"]
    assert "python" in result["detected_project_types"]
    assert "vite" in result["detected_project_types"]


def test_inspector_ignores_node_modules_and_git(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "App.jsx").write_text("")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "hidden.js").write_text("")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hidden").write_text("")

    result = inspect_project(str(tmp_path))

    assert "src/App.jsx" in result["files"]
    assert "node_modules/hidden.js" not in result["files"]
    assert ".git/hidden" not in result["files"]


def test_inspector_detects_java_spring_maven_mysql(tmp_path: Path):
    (tmp_path / "pom.xml").write_text(
        "<project><dependencies>"
        "<dependency><groupId>org.springframework.boot</groupId>"
        "<artifactId>spring-boot-starter</artifactId></dependency>"
        "</dependencies></project>"
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "Application.java").write_text("")
    (tmp_path / "application.properties").write_text(
        "spring.datasource.url=jdbc:mysql://localhost:3306/test"
    )

    result = inspect_project(str(tmp_path))

    assert "java" in result["detected_project_types"]
    assert "spring_boot" in result["detected_project_types"]
    assert "maven" in result["detected_project_types"]
    assert "mysql" in result["detected_project_types"]
