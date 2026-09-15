from pathlib import Path
import tempfile

from app.tools.filesystem import FileSystemTool


with tempfile.TemporaryDirectory() as temp_dir:
    fs = FileSystemTool(temp_dir)

    # Create a directory
    fs.create_directory("demo")

    # Write a file
    fs.write_file(
        "demo/hello.txt",
        "Hello from SpongeBob AI!",
    )

    # Read it back
    content = fs.read_file("demo/hello.txt")

    assert content == "Hello from SpongeBob AI!"

    # List directory
    files = fs.list_directory("demo")

    assert files == ["hello.txt"]

    # Verify path traversal is blocked
    try:
        fs.read_file("../outside.txt")
        raise AssertionError(
            "Path traversal was not blocked."
        )
    except PermissionError:
        pass

print("Filesystem tool tests passed.")
