from app.llm.qwen import QwenProvider


def main():
    qwen = QwenProvider()

    response = qwen.generate(
        "Reply with exactly: SpongeBob provider is working."
    )

    print(response)


if __name__ == "__main__":
    main()