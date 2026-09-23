from pathlib import Path
import shutil
from datetime import datetime


class ProjectSnapshot:
    """
    Creates and restores Last-Known-Good snapshots
    of a SpongeBob project.
    """

    EXCLUDED_NAMES = {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        ".spongebob_snapshots",
        ".env",
    }

    def __init__(self, project_root: str):
        self.project_root = Path(
            project_root
        ).resolve()

        self.snapshot_root = (
            self.project_root.parent
            / ".spongebob_snapshots"
        ).resolve()

    def _is_safe_snapshot_path(
        self,
        snapshot: Path,
    ) -> bool:
        """
        Make sure the snapshot belongs to
        SpongeBob's snapshot directory.
        """

        try:
            snapshot.relative_to(
                self.snapshot_root
            )
            return True

        except ValueError:
            return False

    def create(self) -> str:
        """
        Create a complete Last-Known-Good snapshot.

        Certain generated, version-control, and
        secret files are excluded.
        """

        if not self.project_root.exists():
            raise FileNotFoundError(
                "Project directory does not exist."
            )

        if not self.project_root.is_dir():
            raise NotADirectoryError(
                "Project root is not a directory."
            )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        snapshot_path = (
            self.snapshot_root
            / timestamp
        )

        self.snapshot_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copytree(
            self.project_root,
            snapshot_path,
            ignore=shutil.ignore_patterns(
                *self.EXCLUDED_NAMES
            ),
        )

        return str(snapshot_path)

    def restore(
        self,
        snapshot_path: str,
    ) -> None:
        """
        Restore the project from a trusted
        SpongeBob snapshot.
        """

        snapshot = Path(
            snapshot_path
        ).resolve()

        # SECURITY CHECK
        if not self._is_safe_snapshot_path(
            snapshot
        ):
            raise PermissionError(
                "Snapshot path is outside "
                "the allowed snapshot directory."
            )

        if not snapshot.exists():
            raise FileNotFoundError(
                "Snapshot does not exist."
            )

        if not snapshot.is_dir():
            raise NotADirectoryError(
                "Snapshot is not a directory."
            )

        if self.project_root.exists():
            shutil.rmtree(
                self.project_root
            )

        shutil.copytree(
            snapshot,
            self.project_root,
        )

    def list_snapshots(self) -> list[str]:
        """
        Return available snapshots,
        newest first.
        """

        if not self.snapshot_root.exists():
            return []

        snapshots = [
            item
            for item in self.snapshot_root.iterdir()
            if item.is_dir()
        ]

        snapshots.sort(
            key=lambda path: path.name,
            reverse=True,
        )

        return [
            str(snapshot)
            for snapshot in snapshots
        ]
