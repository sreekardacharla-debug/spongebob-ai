from app.llm.qwen import QwenProvider


def test_qwen_provider_configuration():
    provider = QwenProvider(
        region="us-east-1",
        model_id="qwen.qwen3-coder-next",
    )

    assert provider.region == "us-east-1"
    assert provider.model_id == "qwen.qwen3-coder-next"
    assert provider.client is not None
