import boto3


REGION = "us-east-1"
MODEL_ID = "qwen.qwen3-coder-next"


client = boto3.client(
    "bedrock-runtime",
    region_name=REGION,
)


response = client.converse(
    modelId=MODEL_ID,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "text": "Hello. You are the AI model powering SpongeBob AI. Reply with a short greeting."
                }
            ],
        }
    ],
)


text = response["output"]["message"]["content"][0]["text"]

print("\nQwen response:")
print(text)