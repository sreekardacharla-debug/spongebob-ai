from app.agent.graph import build_graph


graph = build_graph()


initial_state = {
    "user_input": "Build me a portfolio website",
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

    "project_context": {},
    "environment_context": {},

    "architecture_plan": {},

    "execution_results": [],
    "execution_errors": [],

    "validation_results": [],
    "validation_passed": False,
}


result = graph.invoke( initial_state, config={"configurable": {"thread_id": "test-session-1"}})

print("\n===== SPONGEBOB AI RESULT =====\n")

print("Intent:")
print(result["intent"])

print("\nProject type:")
print(result["project_type"])

print("\nRequirements complete:")
print(result["requirements_complete"])

print("\nResponse:")
print(result["response"])

if result["architecture_plan"]:
    print("\nArchitecture plan:")
    print(result["architecture_plan"])
