from __future__ import annotations

from app.agent.graph import build_graph
from app.core.startup import resolve_project_root


def _initial_state(user_input: str, project_root: str) -> dict:
    return {
        "user_input": user_input,
        "response": "",
        "intent": "",
        "project_type": "",
        "needs_requirements": False,
        "goal": "",
        "requirements": {},
        "user_facts": {},
        "delegated_decisions": [],
        "inferences": {},
        "unknowns": [],
        "blocking_unknowns": [],
        "requirements_complete": False,
        "next_question": "",
        "next_action": "",
        "reasoning": "",
        "decision_history": [],
        "project_root": project_root,
        "project_context": {},
        "environment_context": {},
        "architecture_plan": {},
        "snapshot_path": "",
        "execution_results": [],
        "execution_errors": [],
        "validation_results": [],
        "validation_passed": False,
        "diagnosis": {},
        "fix_plan": {},
        "retry_count": 0,
    }


def main() -> None:
    project_root = resolve_project_root()
    graph = build_graph()
    config = {"configurable": {"thread_id": "terminal-user-1"}}

    print("\nSpongeBob AI")
    print(f"Project workspace: {project_root}")
    print("Type 'exit' to stop.\n")

    first_message = True

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if first_message:
            state = _initial_state(user_input, project_root)
            first_message = False
        else:
            state = {"user_input": user_input}

        result = graph.invoke(state, config)
        print(f"SpongeBob: {result.get('response', '')}\n")


if __name__ == "__main__":
    main()
