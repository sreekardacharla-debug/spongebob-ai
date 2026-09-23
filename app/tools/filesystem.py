from pathlib import Path
import shutil

from app.security.capabilities import Capability
from app.security.capability_authorizer import CapabilityAuthorizer
from app.security.capability_request import CapabilityRequest
from app.security.identity import Identity
from app.security.policy_engine import PolicyEngine
from app.security.resources import Resources


class FileSystemTool:
    """
    Controlled filesystem operations for SpongeBob AI.

    Filesystem operations are authorized through:

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
        self.workspace = Path(
            workspace
        ).resolve()

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

    def _safe_path(
        self,
        path: str,
    ) -> Path:

        target = (
            self.workspace / path
        ).resolve()

        try:
            target.relative_to(
                self.workspace
            )

        except ValueError:
            raise PermissionError(
                f"Path is outside the allowed workspace: {path}"
            )

        return target

    def list_directory(
        self,
        path: str = ".",
    ) -> list[str]:

        self._check_capability(
            Capability.FILESYSTEM_READ
        )

        target = self._safe_path(path)

        if not target.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {path}"
            )

        if not target.is_dir():
            raise NotADirectoryError(
                f"Not a directory: {path}"
            )

        return sorted(
            item.name
            for item in target.iterdir()
        )

    def read_file(
        self,
        path: str,
    ) -> str:

        self._check_capability(
            Capability.FILESYSTEM_READ
        )

        target = self._safe_path(path)

        if not target.exists():
            raise FileNotFoundError(
                f"File does not exist: {path}"
            )

        if not target.is_file():
            raise IsADirectoryError(
                f"Not a file: {path}"
            )

        return target.read_text(
            encoding="utf-8"
        )

    def write_file(
        self,
        path: str,
        content: str,
    ) -> None:

        self._check_capability(
            Capability.FILESYSTEM_WRITE
        )

        target = self._safe_path(path)

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target.write_text(
            content,
            encoding="utf-8",
        )

    def create_directory(
        self,
        path: str,
    ) -> None:

        self._check_capability(
            Capability.FILESYSTEM_CREATE
        )

        target = self._safe_path(path)

        target.mkdir(
            parents=True,
            exist_ok=True,
        )

    def delete_file(
        self,
        path: str,
    ) -> None:

        self._check_capability(
            Capability.FILESYSTEM_DELETE
        )

        target = self._safe_path(path)

        if not target.exists():
            raise FileNotFoundError(
                f"File does not exist: {path}"
            )

        if not target.is_file():
            raise IsADirectoryError(
                f"Not a file: {path}"
            )

        target.unlink()

    def delete_directory(
        self,
        path: str,
    ) -> None:

        self._check_capability(
            Capability.FILESYSTEM_DELETE
        )

        target = self._safe_path(path)

        if not target.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {path}"
            )

        if not target.is_dir():
            raise NotADirectoryError(
                f"Not a directory: {path}"
            )

        shutil.rmtree(target)

    def copy(
        self,
        source: str,
        destination: str,
    ) -> None:

        self._check_capability(
            Capability.FILESYSTEM_COPY
        )

        source_path = self._safe_path(
            source
        )

        destination_path = self._safe_path(
            destination
        )

        if not source_path.exists():
            raise FileNotFoundError(
                f"Source does not exist: {source}"
            )

        if destination_path.exists():
            raise FileExistsError(
                f"Destination already exists: {destination}"
            )

        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if source_path.is_dir():
            shutil.copytree(
                source_path,
                destination_path,
            )
        else:
            shutil.copy2(
                source_path,
                destination_path,
            )

    def move(
        self,
        source: str,
        destination: str,
    ) -> None:

        self._check_capability(
            Capability.FILESYSTEM_MOVE
        )

        source_path = self._safe_path(
            source
        )

        destination_path = self._safe_path(
            destination
        )

        if not source_path.exists():
            raise FileNotFoundError(
                f"Source does not exist: {source}"
            )

        if destination_path.exists():
            raise FileExistsError(
                f"Destination already exists: {destination}"
            )

        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.move(
            str(source_path),
            str(destination_path),
        )
