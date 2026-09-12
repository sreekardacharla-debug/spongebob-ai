import boto3

from app.llm.provider import LLMProvider


class QwenProvider(LLMProvider):

    def __init__(
        self,
        region: str = "us-east-1",
        model_id: str = "qwen.qwen3-coder-next",
    ):
        self.region = region
        self.model_id = model_id

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=self.region,
        )

    def generate(self, prompt: str) -> str:
        response = self.client.converse(
            modelId=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt,
                        }
                    ],
                }
            ],
        )

        return response["output"]["message"]["content"][0]["text"]