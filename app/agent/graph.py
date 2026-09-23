from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import AgentState
from app.brain.understanding import understand_request
from app.brain.requirements import (
    analyze_requirements,
    get_decision_history,
)
from app.brain.planner import create_architecture_plan
from app.agent.implementation import execute_implementation
from app.agent.validation import validate_execution
from app.agent.diagnosis import diagnose_failure
from app.agent.fix import create_fix_plan
from app.agent.fix_executor import execute_fix_plan
from app.project.inspector import inspect_project
from app.project.environment import inspect_environment
from app.project.snapshot import ProjectSnapshot

MAX_RETRIES = 2


def understand(state: AgentState):
    return understand_request(state["user_input"])


def route_request(state: AgentState):
    if state["intent"] == "general_question":
        return "general"
    return "requirements"


def requirements(state: AgentState):
    result = analyze_requirements(
        user_input=state["user_input"],
        project_type=state["project_type"],
        current_requirements=state["requirements"],
        user_facts=state["user_facts"],
        delegated_decisions=state["delegated_decisions"],
        inferences=state["inferences"],
        unknowns=state["unknowns"],
        blocking_unknowns=state["blocking_unknowns"],
    )
    return {
        **result,
        "decision_history": get_decision_history(),
    }


def route_after_requirements(state: AgentState):
    if state["requirements_complete"]:
        return "planner"
    return END


def planner(state: AgentState):
    project_context = inspect_project(state["project_root"])
    environment_context = inspect_environment()
    architecture_plan = create_architecture_plan(
        goal=state["goal"],
        project_type=state["project_type"],
        requirements=state["requirements"],
        user_facts=state["user_facts"],
        delegated_decisions=state["delegated_decisions"],
        inferences=state["inferences"],
        project_context=project_context,
        environment_context=environment_context,
    )
    return {
        "project_context": project_context,
        "environment_context": environment_context,
        "architecture_plan": architecture_plan,
        "response": "Architecture plan created.",
    }


def implementation(state: AgentState):
    snapshot_manager = ProjectSnapshot(state["project_root"])
    snapshot_path = snapshot_manager.create()
    execution_results, execution_errors = execute_implementation(
        architecture_plan=state["architecture_plan"],
        workspace=state["project_root"],
        project_context=state["project_context"],
        environment_context=state["environment_context"],
    )
    return {
        "execution_results": execution_results,
        "execution_errors": execution_errors,
        "snapshot_path": snapshot_path,
        "response": "Implementation completed.",
    }


def validation(state: AgentState):
    validation_results, validation_passed = validate_execution(
        project_root=state["project_root"],
        execution_results=state["execution_results"],
    )
    response = (
        "Implementation completed and validation passed."
        if validation_passed
        else "Implementation completed, but validation failed."
    )
    return {
        "validation_results": validation_results,
        "validation_passed": validation_passed,
        "response": response,
    }


def promote_snapshot(state: AgentState):
    snapshot_path = ProjectSnapshot(state["project_root"]).create()
    return {
        "snapshot_path": snapshot_path,
        "response": (
            "Automatic fix validated. "
            "New Last-Known-Good snapshot created."
        ),
    }


def diagnosis(state: AgentState):
    diagnosis_result = diagnose_failure(
        architecture_plan=state["architecture_plan"],
        execution_results=state["execution_results"],
        execution_errors=state["execution_errors"],
        validation_results=state["validation_results"],
    )
    return {
        "diagnosis": diagnosis_result,
        "response": "Implementation failure diagnosed.",
    }


def fix_planner(state: AgentState):
    fix_plan = create_fix_plan(
        architecture_plan=state["architecture_plan"],
        diagnosis=state["diagnosis"],
        project_context=state["project_context"],
    )
    return {
        "fix_plan": fix_plan,
        "response": "Fix plan created.",
    }


def fix_executor(state: AgentState):
    fix_results, fix_errors = execute_fix_plan(
        fix_plan=state["fix_plan"],
        diagnosis=state["diagnosis"],
        workspace=state["project_root"],
    )
    return {
        "execution_results": fix_results,
        "execution_errors": fix_errors,
        "retry_count": state["retry_count"] + 1,
        "response": "Automatic fix executed.",
    }


def restore_snapshot(state: AgentState):
    ProjectSnapshot(state["project_root"]).restore(state["snapshot_path"])
    return {
        "response": (
            "Automatic repair attempts exhausted. "
            "Last-Known-Good snapshot restored."
        )
    }


def route_after_validation(state: AgentState):
    if state["validation_passed"]:
        return "promote" if state["retry_count"] > 0 else "finish"
    if state["retry_count"] >= MAX_RETRIES:
        return "restore"
    return "diagnosis"


def route_after_diagnosis(state: AgentState):
    if (
        state["diagnosis"].get("can_auto_fix") is True
        and state["retry_count"] < MAX_RETRIES
    ):
        return "fix_planner"
    return "restore"


def general(state: AgentState):
    return {
        "response": (
            "This request does not require project implementation."
        )
    }


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("understand", understand)
    graph.add_node("requirements", requirements)
    graph.add_node("planner", planner)
    graph.add_node("implementation", implementation)
    graph.add_node("validation", validation)
    graph.add_node("diagnosis", diagnosis)
    graph.add_node("fix_planner", fix_planner)
    graph.add_node("fix_executor", fix_executor)
    graph.add_node("restore_snapshot", restore_snapshot)
    graph.add_node("promote_snapshot", promote_snapshot)
    graph.add_node("general", general)

    graph.add_edge(START, "understand")
    graph.add_conditional_edges(
        "understand",
        route_request,
        {"requirements": "requirements", "general": "general"},
    )
    graph.add_conditional_edges(
        "requirements",
        route_after_requirements,
        {"planner": "planner", END: END},
    )
    graph.add_edge("planner", "implementation")
    graph.add_edge("implementation", "validation")
    graph.add_conditional_edges(
        "validation",
        route_after_validation,
        {
            "finish": END,
            "promote": "promote_snapshot",
            "diagnosis": "diagnosis",
            "restore": "restore_snapshot",
        },
    )
    graph.add_conditional_edges(
        "diagnosis",
        route_after_diagnosis,
        {
            "fix_planner": "fix_planner",
            "restore": "restore_snapshot",
        },
    )
    graph.add_edge("fix_planner", "fix_executor")
    graph.add_edge("fix_executor", "validation")
    graph.add_edge("restore_snapshot", END)
    graph.add_edge("promote_snapshot", END)
    graph.add_edge("general", END)

    return graph.compile(checkpointer=MemorySaver())
