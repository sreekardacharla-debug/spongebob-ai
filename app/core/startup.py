from app.project.workspace import ProjectWorkspace


def resolve_project_root(project_root: str | None = None) -> str:
    workspace = ProjectWorkspace(project_root)
    workspace.create()
    return workspace.get_path()
