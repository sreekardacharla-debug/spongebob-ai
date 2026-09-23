from dataclasses import dataclass

from app.security.capabilities import Capability
from app.security.identity import Identity


@dataclass(frozen=True)
class CapabilityRequest:
    """
    Represents a request to use a specific SpongeBob capability.

    A capability request does NOT grant permission.

    The PolicyEngine must still approve the request.
    """

    identity: Identity
    capability: Capability
    resource: str

    def __post_init__(self):
        if not isinstance(
            self.identity,
            Identity,
        ):
            raise TypeError(
                "identity must be an Identity object."
            )

        if not isinstance(
            self.capability,
            Capability,
        ):
            raise TypeError(
                "capability must be a Capability."
            )

        if not self.resource:
            raise ValueError(
                "resource cannot be empty."
            )
