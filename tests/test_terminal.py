from app.security.identity import Identity
from app.tools.terminal import TerminalTool


def owner_identity():
    return Identity(
        user_id="owner",
        principal="owner",
    )


def test_terminal_runs_command(tmp_path):
    terminal = TerminalTool(
        str(tmp_path),
        identity=owner_identity(),
        project_id="portfolio",
    )

    result = terminal.run("echo hello")

    assert result["success"] is True
    assert result["return_code"] == 0
    assert "hello" in result["stdout"]


def test_terminal_returns_failure(tmp_path):
    terminal = TerminalTool(
        str(tmp_path),
        identity=owner_identity(),
        project_id="portfolio",
    )

    result = terminal.run("false")

    assert result["success"] is False
    assert result["return_code"] != 0


def test_terminal_captures_stderr(tmp_path):
    terminal = TerminalTool(
        str(tmp_path),
        identity=owner_identity(),
        project_id="portfolio",
    )

    result = terminal.run(
        "echo error-message >&2"
    )

    assert "error-message" in result["stderr"]


def test_terminal_uses_project_workspace(tmp_path):
    terminal = TerminalTool(
        str(tmp_path),
        identity=owner_identity(),
        project_id="portfolio",
    )

    result = terminal.run("pwd")

    assert result["success"] is True
    assert str(tmp_path) in result["stdout"]


def test_terminal_timeout(tmp_path):
    terminal = TerminalTool(
        str(tmp_path),
        identity=owner_identity(),
        project_id="portfolio",
    )

    result = terminal.run(
        "sleep 2",
        timeout=1,
    )

    assert result["success"] is False
    assert result["return_code"] is None
    assert "timed out" in result["stderr"]


def test_terminal_uses_user_project_resource(tmp_path):
    terminal = TerminalTool(
        str(tmp_path),
        identity=owner_identity(),
        project_id="portfolio",
    )

    assert (
        terminal.resource
        == "user:owner:project:portfolio"
    )
