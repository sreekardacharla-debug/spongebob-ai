from pathlib import Path

from app.agent.graph import build_graph
from app.agent import graph as graph_module
from app.project.snapshot import ProjectSnapshot


# --------------------------------------------------
# TEST PROJECT
# --------------------------------------------------

project_root = Path(
    "/tmp/spongebob-full-restore-test"
)

project_root.mkdir(
    parents=True,
    exist_ok=True,
)

index_file = project_root / "index.html"


# --------------------------------------------------
# CREATE GOOD VERSION
# --------------------------------------------------

good_html = """<!DOCTYPE html>
<html>
<head>
    <title>Good Version</title>
</head>
<body>
    <h1>Good Version</h1>
</body>
</html>
"""

index_file.write_text(
    good_html,
    encoding="utf-8",
)


# --------------------------------------------------
# CREATE LAST-KNOWN-GOOD SNAPSHOT
# --------------------------------------------------

snapshot_manager = ProjectSnapshot(
    str(project_root)
)

snapshot_path = snapshot_manager.create()


# --------------------------------------------------
# CREATE BROKEN VERSION
# --------------------------------------------------

index_file.write_text(
    "<html><body>Broken Version</body></html>",
    encoding="utf-8",
)


# --------------------------------------------------
# INITIAL STATE
# --------------------------------------------------

initial_state = {
    "user_input": "Test automatic restore",
    "response": "",

    "intent": "create_project",
    "project_type": "portfolio",
    "needs_requirements": False,

    "goal": "Test automatic restore",
    "requirements": {},
    "user_facts": {},
    "delegated_decisions": [],
    "inferences": {},

    "unknowns": [],
    "blocking_unknowns": [],

    "requirements_complete": True,
    "next_question": "",
    "next_action": "",
    "reasoning": "",

    "decision_history": [],

    "project_root": str(project_root),

    "project_context": {},
    "environment_context": {},

    "architecture_plan": {
        "architecture_summary": (
            "A single-page HTML portfolio website."
        ),
        "files_to_create": [],
        "files_to_modify": [
            "index.html"
        ],
    },

    "snapshot_path": snapshot_path,

    "execution_results": [
        {
            "action": "update_file",
            "path": "index.html",
            "success": True,
        }
    ],

    "execution_errors": [],

    "validation_results": [
        {
            "action": "update_file",
            "path": "index.html",
            "success": False,
            "error": "Missing <!DOCTYPE html>.",
        }
    ],

    "validation_passed": False,

    "diagnosis": {},

    "fix_plan": {},

    "retry_count": 2,
}


# --------------------------------------------------
# TEMPORARILY FORCE THE GRAPH TO START AT VALIDATION
# --------------------------------------------------

graph = build_graph()


# --------------------------------------------------
# TEST RESTORE NODE DIRECTLY THROUGH GRAPH NODE
# --------------------------------------------------

restore_node = graph_module.restore_snapshot

result = restore_node(
    initial_state
)


# --------------------------------------------------
# CHECK RESULT
# --------------------------------------------------

restored_content = index_file.read_text(
    encoding="utf-8"
)

print("\n===== FULL RESTORE TEST =====")

print("\nSnapshot:")
print(snapshot_path)

print("\nResponse:")
print(result["response"])

print("\nRestored file:")
print(restored_content)

print("\nRestore successful:")
print(restored_content == good_html)
