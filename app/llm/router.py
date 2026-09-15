from app.llm.provider import LLMProvider
from app.llm.qwen import QwenProvider


class ModelRouter:

    def __init__(self):
        self.qwen = QwenProvider()

    def generate(self, prompt: str) -> str:
        """
        Generate a response using the currently active model.

        Qwen is the active provider for now.
        Claude will be added to the routing system later.
        """
        return self.qwen.generate(prompt)
