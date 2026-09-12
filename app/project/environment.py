import platform
import shutil
import subprocess
import sys


def command_version(command: str, version_flag: str = "--version") -> str | None:
    """
    Return a command's version output, or None if the command
    is unavailable.
    """
    if shutil.which(command) is None:
        return None

    try:
        result = subprocess.run(
            [command, version_flag],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        output = (result.stdout or result.stderr).strip()

        return output if output else None

    except (OSError, subprocess.SubprocessError):
        return None


def inspect_environment() -> dict:
    """
    Inspect the local development environment.

    This function only observes the machine.
    It does not install, modify, delete, or execute project files.
    """

    return {
        "operating_system": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),

        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },

        "tools": {
            "git": command_version("git"),
            "node": command_version("node"),
            "npm": command_version("npm"),
            "docker": command_version("docker"),
        },

        "available_commands": {
            "python": shutil.which("python"),
            "git": shutil.which("git"),
            "node": shutil.which("node"),
            "npm": shutil.which("npm"),
            "docker": shutil.which("docker"),
        },
    }