from app.security.identity import Identity
from app.security.model_gateway import ModelGateway


class FakeProvider:

    def generate(self, prompt: str) -> str:
        return f"FAKE RESPONSE: {prompt}"


def test_owner_can_invoke_model():
    identity = Identity(
        user_id="owner",
        principal="owner",
    )

    gateway = ModelGateway(
        provider=FakeProvider(),
        identity=identity,
    )

    result = gateway.generate("Hello SpongeBob")

    assert result == "FAKE RESPONSE: Hello SpongeBob"


def test_friend_cannot_invoke_model():
    identity = Identity(
        user_id="friend1",
        principal="friend",
    )

    gateway = ModelGateway(
        provider=FakeProvider(),
        identity=identity,
    )

    try:
        gateway.generate("Hello SpongeBob")
        assert False
    except PermissionError:
        assert True

def test_owner_can_invoke_claude():
    identity = Identity(
        user_id="owner",
        principal="owner",
    )

    gateway = ModelGateway(
        provider=FakeProvider(),
        identity=identity,
        model_resource="model:claude",
    )

    result = gateway.generate("Hello Claude")

    assert result == "FAKE RESPONSE: Hello Claude"
