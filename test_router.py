from app.llm.router import ModelRouter


def test_model_router_configuration():
    router = ModelRouter()

    assert router.qwen is not None
