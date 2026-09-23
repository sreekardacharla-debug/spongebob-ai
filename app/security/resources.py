class Resources:
    """
    Resource identifiers used by SpongeBob AI security policies.
    """

    WORKSPACE = "workspace"

    PROTECTED_SPONGEBOB_CODE = (
        "protected:spongebob_code"
    )

    PROTECTED_CREDENTIALS = (
        "protected:credentials"
    )

    PROTECTED_PRIVATE_DATA = (
        "protected:private_data"
    )

    @staticmethod
    def project(project_id: str) -> str:
        return f"project:{project_id}"

    @staticmethod
    def user_project(
        user_id: str,
        project_id: str,
    ) -> str:
        return (
            f"user:{user_id}:project:{project_id}"
        )
