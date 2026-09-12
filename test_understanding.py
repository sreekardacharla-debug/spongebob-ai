from app.brain.understanding import understand_request


def main():
    result = understand_request(
        "Build me an online shopping website"
    )

    print("\nUnderstanding result:")
    print(result)

    print("\nIntent:", result["intent"])
    print("Project type:", result["project_type"])
    print("Needs requirements:", result["needs_requirements"])


if __name__ == "__main__":
    main()