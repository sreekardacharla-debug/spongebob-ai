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
        "general",
    }

    for node in expected_nodes:
        assert node in nodes


def test_graph_has_end_node():
    graph = build_graph()

    nodes = graph.get_graph().nodes

    assert "__end__" in nodes


def test_successful_fix_routes_to_snapshot_promotion():
    from app.agent import graph as graph_module

    state = {
        "validation_passed": True,
        "retry_count": 1,
    }

    result = graph_module.route_after_validation(state)

    assert result == "promote"


def test_initial_success_does_not_require_snapshot_promotion():
    from app.agent import graph as graph_module

    state = {
        "validation_passed": True,
        "retry_count": 0,
    }

    result = graph_module.route_after_validation(state)

    assert result == "finish"
