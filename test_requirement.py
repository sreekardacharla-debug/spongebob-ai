from app.brain.requirements import analyze_requirements


def main():
    requirements = {}

    messages = [
        "Build me a portfolio website",
        "I want About, Skills, Projects and Contact sections",
        "I don't have any design preference. Choose something good.",
        "Choose the technology stack yourself.",
        "No authentication is needed.",
    ]

    for i, message in enumerate(messages, start=1):

        result = analyze_requirements(
            user_input=message,
            project_type="portfolio",
            current_requirements=requirements,
        )

        requirements = result["requirements"]

        print(f"\n--- Turn {i} ---")
        print("User:", message)
        print("SpongeBob:", result["next_question"])
        print("Requirements:", requirements)
        print("Complete:", result["requirements_complete"])

        if result["requirements_complete"]:
            print("\nRequirements are complete.")
            break


if __name__ == "__main__":
    main()