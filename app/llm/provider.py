from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Common interface for all language-model providers.
    """

    @abstractmethod
    def generate(
        self,
        messages: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """
        Generate a text response from the model.
        """
        raise NotImplementedError