from pathlib import Path
import shutil


class FileSystemTool:
    """
    Controlled filesystem operations for SpongeBob AI.

    All operations are restricted to the configured workspace.
    """

    def __init__(self, workspace: str):
        self.workspace = Path(workspace).resolve()

    def _safe_path(self, path: str) -> Path:
        """
        Resolve a path and ensure it stays inside the workspace.
        """

        target = (self.workspace / path).resolve()

        try:
            target.relative_to(self.workspace)
        except ValueError:
            raise PermissionError(
                f"Path is outside the allowed workspace: {path}"
            )

        return target

    def list_directory(self, path: str = ".") -> list[str]:
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

    def read_file(self, path: str) -> str:
        target = self._safe_path(path)

        if not target.exists():
            raise FileNotFoundError(
                f"File does not exist: {path}"
            )

        if not target.is_file():
            raise IsADirectoryError(
                f"Not a file: {path}"
            )

        return target.read_text(encoding="utf-8")

    def write_file(self, path: str, content: str) -> None:
        target = self._safe_path(path)

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target.write_text(
            content,
            encoding="utf-8",
        )

    def create_directory(self, path: str) -> None:
        target = self._safe_path(path)

        target.mkdir(
            parents=True,
            exist_ok=True,
        )

    def delete_file(self, path: str) -> None:
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

    def delete_directory(self, path: str) -> None:
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

    def copy(self, source: str, destination: str) -> None:
        source_path = self._safe_path(source)
        destination_path = self._safe_path(destination)

        if not source_path.exists():
            raise FileNotFoundError(
                f"Source does not exist: {source}"
            )

        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if source_path.is_dir():
            shutil.copytree(
                source_path,
                destination_path,
                dirs_exist_ok=True,
            )
        else:
            shutil.copy2(
                source_path,
                destination_path,
            )

    def move(self, source: str, destination: str) -> None:
        source_path = self._safe_path(source)
        destination_path = self._safe_path(destination)

        if not source_path.exists():
            raise FileNotFoundError(
                f"Source does not exist: {source}"
            )

        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.move(
            str(source_path),
            str(destination_path),
        )
