from pathlib import Path


class ProjectWorkspace:
    """
    Manages the location where SpongeBob AI works on a user's project.

    SpongeBob's own application directory and the user's project
    directory are kept separate.
    """

    def __init__(self, project_root: str | None = None):
        if project_root is None:
            project_root = (
                Path.home()
                / "Documents"
                / "SpongeBob Projects"
            )

        self.project_root = Path(project_root).expanduser().resolve()

    def exists(self) -> bool:
        return self.project_root.exists()

    def create(self) -> None:
        self.project_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def get_path(self) -> str:
        return str(self.project_root)

    def is_inside(self, path: str) -> bool:
        target = Path(path).expanduser().resolve()

        try:
            target.relative_to(self.project_root)
            return True
        except ValueError:
            return False

































