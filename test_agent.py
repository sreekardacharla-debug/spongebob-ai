from app.agent.graph import build_graph


def main():
    agent = build_graph()

    config = {
        "configurable": {
            "thread_id": "test-user-1"
        }
    }

    # First message
    result = agent.invoke(
        {
            "user_input": "Build me a portfolio website",
            "response": "",
            "intent": "",
            "project_type": "",
            "needs_requirements": False,
            "requirements": {},
            "requirements_complete": False,
            "next_question": "",
        },
        config,
    )

    print("\n--- Turn 1 ---")
    print("SpongeBob:", result["response"])
    print("Requirements:", result["requirements"])

    # Second message
    result = agent.invoke(
        {
            "user_input": "I want About, Skills, Projects and Contact sections",
        },
        config,
    )

    print("\n--- Turn 2 ---")
    print("SpongeBob:", result["response"])
    print("Requirements:", result["requirements"])


if __name__ == "__main__":
    main()