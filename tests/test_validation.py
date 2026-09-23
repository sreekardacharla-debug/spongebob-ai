from pathlib import Path

from app.agent.validation import validate_html_file


def test_empty_html_file():
    path = Path("/tmp/empty.html")

    path.write_text(
        "",
        encoding="utf-8",
    )

    valid, message = validate_html_file(path)

    assert valid is False
    assert message == "HTML file is empty."


def test_missing_doctype():
    path = Path("/tmp/missing-doctype.html")

    path.write_text(
        "<html><head></head><body></body></html>",
        encoding="utf-8",
    )

    valid, message = validate_html_file(path)

    assert valid is False
    assert message == "Missing <!DOCTYPE html>."


def test_valid_html():
    path = Path("/tmp/valid.html")

    path.write_text(
        """<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <h1>Hello SpongeBob</h1>
</body>
</html>
""",
        encoding="utf-8",
    )

    valid, message = validate_html_file(path)

    assert valid is True
    assert message == "Basic HTML structure is valid."
