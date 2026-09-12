from typing import TypedDict


class AgentState(TypedDict):
    # Current conversation
    user_input: str
    response: str

    # Request understanding
    intent: str
    project_type: str
    needs_requirements: bool

    # Requirement knowledge
    requirements: dict
    user_facts: dict
    delegated_decisions: list
    inferences: dict

    # Uncertainty
    unknowns: list
    blocking_unknowns: list

    # Requirement decision
    requirements_complete: bool
    next_question: str
    next_action: str

    # Decision history
    decision_history: list