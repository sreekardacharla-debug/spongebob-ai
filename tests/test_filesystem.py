from pathlib import Path

import pytest

from app.security.identity import Identity
from app.tools.filesystem import FileSystemTool


def create_workspace(
    path: str,
) -> Path:
    workspace = Path(path)

    if workspace.exists():
        import shutil
        shutil.rmtree(workspace)

    workspace.mkdir(
        parents=True,
        exist_ok=True,
    )

    return workspace


def owner_identity():
    return Identity(
        user_id="owner",
        principal="owner",
    )


def friend_identity():
    return Identity(
        user_id="friend1",
        principal="friend",
    )


def test_write_and_read_file():
    workspace = create_workspace(
        "/tmp/spongebob-filesystem-test"
    )

    filesystem = FileSystemTool(
        str(workspace),
        identity=owner_identity(),
        project_id="portfolio",
    )

    filesystem.write_file(
        "hello.txt",
        "Hello SpongeBob!",
    )

    content = filesystem.read_file(
        "hello.txt"
    )

    assert content == "Hello SpongeBob!"


def test_create_directory():
    workspace = create_workspace(
        "/tmp/spongebob-filesystem-test"
    )

    filesystem = FileSystemTool(
        str(workspace),
        identity=owner_identity(),
        project_id="portfolio",
    )

    filesystem.create_directory(
        "src"
    )

    assert (
        workspace / "src"
    ).exists()

    assert (
        workspace / "src"
    ).is_dir()


def test_delete_file():
    workspace = create_workspace(
        "/tmp/spongebob-filesystem-test"
    )

    filesystem = FileSystemTool(
        str(workspace),
        identity=owner_identity(),
        project_id="portfolio",
    )

    filesystem.write_file(
        "delete.txt",
        "temporary",
    )

    filesystem.delete_file(
        "delete.txt"
    )

    assert not (
        workspace / "delete.txt"
    ).exists()


def test_delete_directory():
    workspace = create_workspace(
        "/tmp/spongebob-filesystem-test"
    )

    filesystem = FileSystemTool(
        str(workspace),
        identity=owner_identity(),
        project_id="portfolio",
    )

    filesystem.create_directory(
        "temporary"
    )

    filesystem.delete_directory(
        "temporary"
    )

    assert not (
        workspace / "temporary"
    ).exists()


def test_copy_file():
    workspace = create_workspace(
        "/tmp/spongebob-filesystem-test"
    )

    filesystem = FileSystemTool(
        str(workspace),
        identity=owner_identity(),
        project_id="portfolio",
    )

    filesystem.write_file(
        "original.txt",
        "copy me",
    )

    filesystem.copy(
        "original.txt",
        "copy.txt",
    )

    assert filesystem.read_file(
        "copy.txt"
    ) == "copy me"


def test_move_file():
    workspace = create_workspace(
        "/tmp/spongebob-filesystem-test"
    )

    filesystem = FileSystemTool(
        str(workspace),
        identity=owner_identity(),
        project_id="portfolio",
    )

    filesystem.write_file(
        "old.txt",
        "move me",
    )

    filesystem.move(
        "old.txt",
        "new.txt",
    )

    assert not (
        workspace / "old.txt"
    ).exists()

    assert filesystem.read_file(
        "new.txt"
    ) == "move me"


def test_path_outside_workspace_is_blocked():
    workspace = create_workspace(
        "/tmp/spongebob-filesystem-test"
    )

    filesystem = FileSystemTool(
        str(workspace),
        identity=owner_identity(),
        project_id="portfolio",
    )

    with pytest.raises(
        PermissionError
    ):
        filesystem.read_file(
            "../outside.txt"
        )


def test_filesystem_checks_user_project_resource():
    workspace = create_workspace(
        "/tmp/spongebob-policy-filesystem-test"
    )

    filesystem = FileSystemTool(
        str(workspace),
        identity=friend_identity(),
        project_id="portfolio",
    )

    with pytest.raises(
        PermissionError
    ):
        filesystem.read_file(
            "secret.txt"
        )
