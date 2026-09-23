from app.project.environment import inspect_environment


def test_inspect_environment_returns_expected_structure():
    result = inspect_environment()

    assert "operating_system" in result
    assert "os_version" in result
    assert "architecture" in result
    assert "python" in result
    assert "tools" in result
    assert "available_commands" in result

    assert "version" in result["python"]
    assert "executable" in result["python"]

    assert "git" in result["tools"]
    assert "node" in result["tools"]
    assert "npm" in result["tools"]
    assert "docker" in result["tools"]
