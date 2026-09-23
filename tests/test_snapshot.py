from pathlib import Path

from app.project.snapshot import ProjectSnapshot


def test_snapshot_restore():
    project_root = Path(
        "/tmp/spongebob-test-project"
    )

    project_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    index_file = project_root / "index.html"

    good_content = "GOOD VERSION"
    broken_content = "BROKEN VERSION"

    index_file.write_text(
        good_content,
        encoding="utf-8",
    )

    snapshot_manager = ProjectSnapshot(
        str(project_root)
    )

    snapshot_path = snapshot_manager.create()

    index_file.write_text(
        broken_content,
        encoding="utf-8",
    )

    snapshot_manager.restore(
        snapshot_path
    )

    restored_content = index_file.read_text(
        encoding="utf-8"
    )

    assert restored_content == good_content


def test_snapshot_restore_blocks_outside_path():
    project_root = Path(
        "/tmp/spongebob-security-test"
    )

    project_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    outside_path = Path(
        "/tmp/not-a-spongebob-snapshot"
    )

    outside_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    snapshot_manager = ProjectSnapshot(
        str(project_root)
    )

    try:
        snapshot_manager.restore(
            str(outside_path)
        )

        assert False, (
            "Restore should reject "
            "outside snapshot paths."
        )

    except PermissionError:
        pass
