from app.tools.terminal import TerminalTool


terminal = TerminalTool("/workspaces/spongebob-ai")


# 1. Successful command
result = terminal.run(
    "python -c \"print('hello from terminal tool')\""
)

assert result["success"] is True
assert result["return_code"] == 0
assert "hello from terminal tool" in result["stdout"]


# 2. Failed command
result = terminal.run(
    "python -c \"raise SystemExit(1)\""
)

assert result["success"] is False
assert result["return_code"] == 1


# 3. Timeout
result = terminal.run(
    "python -c \"import time; time.sleep(2)\"",
    timeout=1,
)

assert result["success"] is False
assert result["return_code"] is None
assert "timed out" in result["stderr"].lower()


print("Terminal tool tests passed.")
