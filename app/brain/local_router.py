class LocalRouter:
    """
    Handles decisions that do not require an LLM.

    The purpose is to reduce unnecessary model calls.
    """

    SIMPLE_GREETING_WORDS = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
    }

    SIMPLE_HELP_WORDS = {
        "help",
        "what can you do",
        "what do you do",
    }

    def classify(self, user_message: str) -> dict:
        text = user_message.strip().lower()

        if text in self.SIMPLE_GREETING_WORDS:
            return {
                "handled": True,
                "type": "greeting",
                "response": (
                    "Hey! I'm SpongeBob AI! 🧽🤖"
                ),
            }

        if text in self.SIMPLE_HELP_WORDS:
            return {
                "handled": True,
                "type": "help",
                "response": (
                    "I can help with software projects, "
                    "requirements, architecture, coding, "
                    "debugging, and project execution."
                ),
            }

        return {
            "handled": False,
            "type": "unknown",
            "response": "",
        }