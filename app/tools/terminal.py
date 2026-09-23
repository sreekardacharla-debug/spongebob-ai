import subprocess

from app.security.capabilities import Capability
from app.security.capability_authorizer import CapabilityAuthorizer
from app.security.capability_request import CapabilityRequest
from app.security.identity import Identity
from app.security.policy_engine import PolicyEngine
from app.security.resources import Resources


class TerminalTool:
    """
    Controlled command execution for SpongeBob AI.

    Terminal operations are authorized through:

        Identity
            ↓
        CapabilityRequest
            ↓
        CapabilityAuthorizer
            ↓
        PolicyEngine
    """

    def __init__(
        self,
        workspace: str,
        identity: Identity | None = None,
        project_id: str = "default",
    ):
        self.workspace = workspace

        if identity is None:
            identity = Identity(
                user_id="owner",
                principal="owner",
            )

        self.identity = identity
        self.project_id = project_id

        self.resource = Resources.user_project(
            identity.user_id,
            project_id,
        )

        self.policy = PolicyEngine()

        self.authorizer = CapabilityAuthorizer(
            self.policy
        )

    def _check_capability(
        self,
        capability: Capability,
    ) -> None:
        """
        Check whether the current identity can use
        the requested capability on this project.
        """

        request = CapabilityRequest(
            identity=self.identity,
            capability=capability,
            resource=self.resource,
        )

        self.authorizer.check(request)

    def run(
        self,
        command: str,
        timeout: int = 60,
    ) -> dict:
        """
        Execute a command inside the project workspace.

        Permission is checked before the command runs.
        """

        self._check_capability(
            Capability.TERMINAL_EXECUTE
        )

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
                    f"Command timed out after "
                    f"{timeout} seconds."
                ),
                "success": False,
            }
