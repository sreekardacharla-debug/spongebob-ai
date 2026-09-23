from app.agent.graph import build_graph


def test_graph_builds():
    assert build_graph() is not None


def test_graph_contains_expected_nodes():
    nodes = build_graph().get_graph().nodes
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
    assert expected.issubset(nodes)


def test_graph_has_end_node():
    assert "__end__" in build_graph().get_graph().nodes


def test_successful_fix_routes_to_snapshot_promotion():
    from app.agent import graph as graph_module
    assert graph_module.route_after_validation(
        {"validation_passed": True, "retry_count": 1}
    ) == "promote"


def test_initial_success_does_not_require_snapshot_promotion():
    from app.agent import graph as graph_module
    assert graph_module.route_after_validation(
        {"validation_passed": True, "retry_count": 0}
    ) == "finish"


def test_requirements_node_returns_decision_history(monkeypatch):
    from app.agent import graph as graph_module
    from app.brain import requirements as requirements_module

    requirements_module.reset_decision_history()
    requirements_module.decision_history.add(
        "frontend", "React", source="user"
    )

    monkeypatch.setattr(
        graph_module,
        "analyze_requirements",
        lambda **kwargs: {
            "goal": "Build app",
            "user_facts": {},
            "delegated_decisions": [],
            "inferences": {},
            "unknowns": [],
            "blocking_unknowns": [],
            "action": "CONTINUE_PLANNING",
            "requirements_complete": True,
            "next_question": "",
            "requirements": {},
            "reasoning": "Enough information.",
        },
    )

    state = {
        "user_input": "Build an app",
        "project_type": "web_application",
        "requirements": {},
        "user_facts": {},
        "delegated_decisions": [],
        "inferences": {},
        "unknowns": [],
        "blocking_unknowns": [],
        "decision_history": [],
    }

    result = graph_module.requirements(state)

    assert len(result["decision_history"]) == 1
    assert result["decision_history"][0]["decision"] == "frontend"
    assert result["decision_history"][0]["value"] == "React"

    requirements_module.reset_decision_history()
