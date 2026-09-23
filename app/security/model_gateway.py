from app.llm.router import ModelRouter
from app.llm.provider import LLMProvider

from app.security.capabilities import Capability
from app.security.capability_authorizer import CapabilityAuthorizer
from app.security.capability_request import CapabilityRequest
from app.security.identity import Identity


class ModelGateway:
    """
    Secure gateway for model invocation.

    The agent never calls a model provider directly.

        Agent
          ↓
        ModelGateway
          ↓
        CapabilityAuthorizer
          ↓
        ModelRouter / Provider
          ↓
        Qwen / Claude
    """

    def __init__(
        self,
        provider: LLMProvider | ModelRouter,
        identity: Identity,
        authorizer: CapabilityAuthorizer | None = None,
        model_resource: str = "model:qwen",
    ):
        self.provider = provider
        self.identity = identity
        self.model_resource = model_resource

        if authorizer is None:
            authorizer = CapabilityAuthorizer()

        self.authorizer = authorizer

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Authorize and execute a model request.

        Credentials remain inside the provider layer.
        """

        request = CapabilityRequest(
            identity=self.identity,
            capability=Capability.MODEL_INVOKE,
            resource=self.model_resource,
        )

        self.authorizer.check(request)

        return self.provider.generate(prompt)
