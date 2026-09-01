import os
from openai import OpenAI


class QwenClient:
    """
    Qwen model client for SpongeBob AI.

    Uses the Hugging Face OpenAI-compatible router during development.
    The backend can later be changed without changing the agent brain.
    """

    DEFAULT_BASE_URL = "https://router.huggingface.co/v1"
    DEFAULT_MODEL = "Qwen/Qwen3-Coder-30B-A3B-Instruct:featherless-ai"

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ):
        self.base_url = (
            base_url
            or os.getenv("QWEN_BASE_URL")
            or self.DEFAULT_BASE_URL
        )

        self.model = (
            model
            or os.getenv("QWEN_MODEL")
            or self.DEFAULT_MODEL
        )

        self.api_key = (
            api_key
            or os.getenv("HF_TOKEN")
            or os.getenv("QWEN_API_KEY")
        )

        if not self.api_key:
            raise RuntimeError(
                "No Qwen API token configured. "
                "Set HF_TOKEN or QWEN_API_KEY."
            )

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def generate(
        self,
        messages: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("Qwen returned an empty response.")

        return content