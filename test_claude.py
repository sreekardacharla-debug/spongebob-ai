from app.llm.claude import ClaudeProvider


def test_claude_provider_configuration():
    provider = ClaudeProvider()

    assert provider.region == "us-east-1"
    assert provider.model_id == "anthropic.claude-opus-5"
    assert provider.client is not None
