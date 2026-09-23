from app.llm.service import ModelService
from app.security.identity import Identity


class FakeRouter:

    def generate(self, prompt: str) -> str:
        return f"ROUTER RESPONSE: {prompt}"


def test_model_service_uses_secure_gateway():
    identity = Identity(
        user_id="owner",
        principal="owner",
    )

    service = ModelService(
        identity=identity,
        router=FakeRouter(),
    )

    result = service.generate("Build a React app")

    assert result == "ROUTER RESPONSE: Build a React app"


def test_model_service_rejects_friend():
    identity = Identity(
        user_id="friend1",
        principal="friend",
    )

    service = ModelService(
        identity=identity,
        router=FakeRouter(),
    )

    try:
        service.generate("Build a React app")
        assert False
    except PermissionError:
        assert True
