from dataclasses import dataclass


@dataclass(frozen=True)
class Identity:
    """
    Represents the security identity making a request.

    An identity has:

        user_id  -> unique user identifier
        principal -> role/type of actor
    """

    user_id: str
    principal: str

    def __post_init__(self):
        if not self.user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        if not self.principal:
            raise ValueError(
                "principal cannot be empty."
            )

    @property
    def identifier(self) -> str:
        """
        Return a stable identity identifier.
        """

        return (
            f"{self.principal}:{self.user_id}"
        )
