from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import AgentState
from app.brain.requirements import analyze_requirements
from app.brain.understanding import understand_request


def understand(state: AgentState) -> AgentState:
    # Only classify when we don't already know the intent.
    if state["intent"]:
        return state

    result = understand_request(state["user_input"])

    return {
        **state,
        "intent": result["intent"],
        "project_type": result["project_type"],
        "needs_requirements": result["needs_requirements"],
    }


def route_request(state: AgentState) -> str:
    if state["intent"] == "create_project":
        return "requirements"

    if state["intent"] == "general_question":
        return "general"

    return "other"


def requirements(state: AgentState) -> AgentState:
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
        **state,

        "goal": result["goal"],
        "user_facts": result["user_facts"],
        "delegated_decisions": result["delegated_decisions"],
        "inferences": result["inferences"],

        "unknowns": result["unknowns"],
        "blocking_unknowns": result["blocking_unknowns"],

        "requirements": result["requirements"],
        "requirements_complete": result["requirements_complete"],
        "next_question": result["next_question"],

        "next_action": result["action"],
        "reasoning": result["reasoning"],

        "response": (
            result["next_question"]
            if result["next_question"]
            else result["reasoning"]
        ),
    }


def general_response(state: AgentState) -> AgentState:
    return {
        **state,
        "response": "This is a general question.",
    }


def other_response(state: AgentState) -> AgentState:
    return {
        **state,
        "response": (
            "I understood your request, but this flow "
            "is not implemented yet."
        ),
    }


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("understand", understand)
    graph.add_node("requirements", requirements)
    graph.add_node("general", general_response)
    graph.add_node("other", other_response)

    graph.add_edge(START, "understand")

    graph.add_conditional_edges(
        "understand",
        route_request,
        {
            "requirements": "requirements",
            "general": "general",
            "other": "other",
        },
    )

    graph.add_edge("requirements", END)
    graph.add_edge("general", END)
    graph.add_edge("other", END)

    memory = MemorySaver()

    return graph.compile(checkpointer=memory)