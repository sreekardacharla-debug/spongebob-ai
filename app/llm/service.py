from app.llm.router import ModelRouter
from app.security.identity import Identity
from app.security.model_gateway import ModelGateway


class ModelService:
    """
    Application-level interface for model generation.

    The rest of SpongeBob AI uses this service instead
    of directly accessing model providers.
    """

    def __init__(
        self,
        identity: Identity,
        router: ModelRouter | None = None,
    ):
        if router is None:
            router = ModelRouter()

        self.gateway = ModelGateway(
            provider=router,
            identity=identity,
        )

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a response through the secure model gateway.
        """

        return self.gateway.generate(prompt)
