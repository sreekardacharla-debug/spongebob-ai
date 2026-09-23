from app.agent.graph import build_graph


def test_graph_builds():
    graph = build_graph()
    assert graph is not None


def test_graph_contains_expected_nodes():
    graph = build_graph()
    nodes = graph.get_graph().nodes

    expected_nodes = {
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

    for node in expected_nodes:
        assert node in nodes


def test_graph_has_end_node():
    graph = build_graph()
    nodes = graph.get_graph().nodes
    assert "__end__" in nodes


def test_general_question_routes_to_general():
    from app.agent import graph as graph_module

    assert graph_module.route_request({"intent": "general_question"}) == "general"


def test_non_general_request_routes_to_requirements():
    from app.agent import graph as graph_module

    assert graph_module.route_request({"intent": "create_project"}) == "requirements"


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

    monkeypatch.setattr(
        graph_module,
        "analyze_requirements",
        lambda **kwargs: {
            "goal": "Build app",
            "user_facts": {"frontend": "React"},
            "delegated_decisions": [],
            "inferences": {},
            "unknowns": [],
            "blocking_unknowns": [],
            "action": "CONTINUE_PLANNING",
            "requirements_complete": True,
            "next_question": "",
            "requirements": {"frontend": "React"},
            "reasoning": "Enough information.",
        },
    )

    monkeypatch.setattr(
        graph_module,
        "get_decision_history",
        lambda: [
            {
                "decision": "frontend",
                "value": "React",
                "source": "user",
                "timestamp": "test",
            }
        ],
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
    }

    result = graph_module.requirements(state)

    assert result["decision_history"] == [
        {
            "decision": "frontend",
            "value": "React",
            "source": "user",
            "timestamp": "test",
        }
    ]
