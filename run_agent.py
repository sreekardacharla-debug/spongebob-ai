from app.agent.graph import build_graph


def main():
    agent = build_graph()

    config = {
        "configurable": {
            "thread_id": "terminal-user-1"
        }
    }

    first_message = True

    print("\nSpongeBob AI")
    print("Type 'exit' to stop.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower().strip() == "exit":
            print("Goodbye!")
            break

        if first_message:
            state = {
                "user_input": user_input,
                "response": "",
                "intent": "",
                "project_type": "",
                "needs_requirements": False,
                "requirements": {},
                "requirements_complete": False,
                "next_question": "",
            }

            first_message = False

        else:
            state = {
                "user_input": user_input,
            }

        result = agent.invoke(state, config)

        print(f"SpongeBob: {result['response']}\n")


if __name__ == "__main__":
    main()