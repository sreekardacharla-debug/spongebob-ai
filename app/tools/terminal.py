import subprocess


class TerminalTool:
    """
    Controlled command execution for SpongeBob AI.

    Commands are executed inside the configured workspace.
    """

    def __init__(self, workspace: str):
        self.workspace = workspace

    def run(
        self,
        command: str,
        timeout: int = 60,
    ) -> dict:
        """
        Execute a shell command and capture its result.
        """

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }

        except subprocess.TimeoutExpired:
            return {
                "command": command,
                "return_code": None,
                "stdout": "",
                "stderr": (
                    f"Command timed out after {timeout} seconds."
                ),
                "success": False,
            }
