from app.security.capability_actions import action_for_capability
from app.security.capability_request import CapabilityRequest
from app.security.policy_engine import PolicyEngine


class CapabilityAuthorizer:
    """
    Authorizes capability requests through the PolicyEngine.

    The capability itself never grants permission.
    The PolicyEngine remains the final authority.
    """

    def __init__(
        self,
        policy_engine: PolicyEngine | None = None,
    ):
        if policy_engine is None:
            policy_engine = PolicyEngine()

        self.policy = policy_engine

    def is_allowed(
        self,
        request: CapabilityRequest,
    ) -> bool:
        """
        Return True when the request is authorized.
        """

        action = action_for_capability(
            request.capability
        )

        return self.policy.is_allowed(
            request.identity,
            action,
            request.resource,
        )

    def check(
        self,
        request: CapabilityRequest,
    ) -> None:
        """
        Authorize a capability request.

        Raises PermissionError when denied.
        """

        action = action_for_capability(
            request.capability
        )

        self.policy.check(
            request.identity,
            action,
            request.resource,
        )
