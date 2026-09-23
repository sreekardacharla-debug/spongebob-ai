from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check(name: str, fn) -> bool:
    print(f"\n[CHECK] {name}")
    print("-" * 64)
    try:
        fn()
    except Exception as exc:
        print(f"[FAIL] {name}: {exc}")
        return False
    print(f"[PASS] {name}")
    return True


def run(command: list[str], timeout: int = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def verify_tests() -> None:
    result = run([sys.executable, "-m", "pytest", "-q"])
    if result.returncode != 0:
        raise RuntimeError((result.stdout + "\n" + result.stderr)[-5000:])
    print(result.stdout.strip())


def verify_imports() -> None:
    commands = [
        "import app.cli",
        "from app.agent.graph import build_graph",
        "from app.security.policy_engine import PolicyEngine",
        "from app.tools.filesystem import FileSystemTool",
        "from app.tools.terminal import TerminalTool",
        "from app.project.snapshot import ProjectSnapshot",
    ]
    for code in commands:
        result = run([sys.executable, "-c", code])
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())


def verify_security() -> None:
    from app.security.identity import Identity
    from app.security.policy_engine import PolicyEngine
    from app.security.resources import Resources

    policy = PolicyEngine()
    owner = Identity(user_id="owner", principal="owner")
    friend = Identity(user_id="friend1", principal="friend")

    assert policy.is_allowed(owner, "read_file", Resources.WORKSPACE)
    assert not policy.is_allowed(friend, "read_file", Resources.WORKSPACE)
    assert not policy.is_allowed(
        owner,
        "read_file",
        Resources.PROTECTED_SPONGEBOB_CODE,
    )
    assert not policy.is_allowed(
        owner,
        "read_file",
        Resources.PROTECTED_CREDENTIALS,
    )


def verify_filesystem_boundary() -> None:
    from app.security.identity import Identity
    from app.tools.filesystem import FileSystemTool

    with tempfile.TemporaryDirectory() as tmp:
        tool = FileSystemTool(
            tmp,
            identity=Identity(user_id="owner", principal="owner"),
            project_id="verification",
        )

        tool.write_file("ok.txt", "safe")
        assert tool.read_file("ok.txt") == "safe"

        try:
            tool.read_file("../outside.txt")
        except PermissionError:
            pass
        else:
            raise AssertionError("Workspace escape was not blocked")


def verify_snapshot_roundtrip() -> None:
    from app.project.snapshot import ProjectSnapshot

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "project"
        root.mkdir()
        good = root / "index.html"
        good.write_text("<!DOCTYPE html><html><body>good</body></html>", encoding="utf-8")

        manager = ProjectSnapshot(str(root))
        snapshot = manager.create()

        good.write_text("broken", encoding="utf-8")
        manager.restore(snapshot)

        assert good.read_text(encoding="utf-8") == "<!DOCTYPE html><html><body>good</body></html>"
        assert manager.list_snapshots()


def verify_graph() -> None:
    from app.agent.graph import build_graph

    graph = build_graph()
    nodes = graph.get_graph().nodes
    expected = {
        "understand",
        "requirements",
        "planner",
        "implementation",
        "validation",
        "diagnosis",
        "fix_planner",
        "fix_executor",
        "restore_snapshot",
        "promote_snapshot",
        "general",
    }
    missing = expected - set(nodes)
    assert not missing, f"Missing graph nodes: {sorted(missing)}"


def verify_decision_history() -> None:
    from app.memory.decision_history import DecisionHistory

    history = DecisionHistory()
    first = history.add("frontend", "React")
    second = history.add("frontend", "React")

    assert first == second
    assert len(history.all()) == 1

    history.add("frontend", "Next.js")
    assert history.latest("frontend")["value"] == "Next.js"


def verify_cli_import() -> None:
    result = run([sys.executable, "-c", "from app.cli import main"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())


def verify_aws() -> None:
    result = run(["aws", "sts", "get-caller-identity"], timeout=60)
    if result.returncode != 0:
        raise RuntimeError(
            "AWS authentication failed. Refresh your AWS login and rerun verification."
        )

    data = json.loads(result.stdout)
    if not data.get("Account") or not data.get("Arn"):
        raise RuntimeError("AWS identity response is incomplete.")

    # Never print the identity payload.


def verify_qwen() -> None:
    code = (
        "from app.llm.qwen import QwenProvider; "
        "r=QwenProvider().generate('Reply with exactly: QWEN_TEST_OK'); "
        "assert r.strip() == 'QWEN_TEST_OK', repr(r)"
    )
    result = run([sys.executable, "-c", code], timeout=120)
    if result.returncode != 0:
        raise RuntimeError(
            "Live Qwen/Bedrock request failed. "
            "AWS authentication/model access may need attention.\n"
            + (result.stderr or result.stdout)[-3000:]
        )


def verify_cli_help() -> None:
    result = run(
        [
            sys.executable,
            "-c",
            "import app.cli; print('CLI_IMPORT_OK')",
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())


def main() -> int:
    print("=" * 64)
    print("              SPONGEBOB AI VERIFICATION")
    print("=" * 64)

    checks = [
        ("Python test suite", verify_tests),
        ("Module imports", verify_imports),
        ("Security policy", verify_security),
        ("Filesystem workspace boundary", verify_filesystem_boundary),
        ("Last-Known-Good snapshot roundtrip", verify_snapshot_roundtrip),
        ("Decision history", verify_decision_history),
        ("LangGraph structure", verify_graph),
        ("CLI wiring", verify_cli_import),
        ("AWS authentication", verify_aws),
        ("Qwen Bedrock integration", verify_qwen),
        ("CLI import smoke test", verify_cli_help),
    ]

    passed = 0

    for name, fn in checks:
        if check(name, fn):
            passed += 1

    print("\n" + "=" * 64)
    print(f"RESULT: {passed}/{len(checks)} CHECKS PASSED")

    if passed == len(checks):
        print("SPONGEBOB VERIFICATION: PASS")
        return 0

    print("SPONGEBOB VERIFICATION: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
