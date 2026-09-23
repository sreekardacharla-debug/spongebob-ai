from app.security.identity import Identity
from app.security.resources import Resources


class PolicyEngine:
    """
    IAM-style policy engine for SpongeBob AI.

    Permission request:

        identity + action + resource

    Security principles:

        1. Deny by default.
        2. Explicit deny overrides allow.
        3. Users access only explicitly permitted projects.
        4. Protected SpongeBob resources are denied.
    """

    def __init__(self):
        self.policies = []

        # Protected resources are always denied.
        self.add_policy(
            effect="deny",
            principals={
                "owner",
                "user",
                "friend",
                "agent",
            },
            actions={
                "read_file",
                "write_file",
                "create_file",
                "update_file",
                "create_directory",
                "delete_file",
                "delete_directory",
                "copy",
                "move",
                "run_command",
                "model_invoke",
            },
            resources={
                Resources.PROTECTED_SPONGEBOB_CODE,
                Resources.PROTECTED_CREDENTIALS,
                Resources.PROTECTED_PRIVATE_DATA,
            },
        )

        # Owner filesystem permissions.
        self.add_policy(
            effect="allow",
            principals={"owner"},
            actions={
                "read_file",
                "write_file",
                "create_file",
                "update_file",
                "create_directory",
                "delete_file",
                "delete_directory",
                "copy",
                "move",
            },
            resources={Resources.WORKSPACE},
        )

        # Owner terminal permission.
        self.add_policy(
            effect="allow",
            principals={"owner"},
            actions={"run_command"},
            resources={Resources.WORKSPACE},
        )

        # Owner model invocation permission.
        #
        # This allows the owner to request model execution
        # through the future secure model gateway.
        self.add_policy(
            effect="allow",
            principals={"owner"},
            actions={"model_invoke"},
            resources={"model:*"},
        )

        # Owner can fully manage their own projects.
        self.add_policy(
            effect="allow",
            principals={"owner"},
            actions={
                "read_file",
                "write_file",
                "create_file",
                "update_file",
                "create_directory",
                "delete_file",
                "delete_directory",
                "copy",
                "move",
                "run_command",
            },
            resources={"user:owner:project:*"},
        )

        # Owner can manage project resources.
        self.add_policy(
            effect="allow",
            principals={"owner"},
            actions={
                "read_file",
                "write_file",
                "create_file",
                "update_file",
                "create_directory",
                "delete_file",
                "delete_directory",
                "copy",
                "move",
                "run_command",
            },
            resources={"project:*"},
        )

    def add_policy(
        self,
        effect: str,
        principals: set[str],
        actions: set[str],
        resources: set[str],
    ) -> None:
        if effect not in {"allow", "deny"}:
            raise ValueError(
                "Effect must be 'allow' or 'deny'."
            )

        self.policies.append(
            {
                "effect": effect,
                "principals": set(principals),
                "actions": set(actions),
                "resources": set(resources),
            }
        )

    def _resource_matches(
        self,
        requested_resource: str,
        policy_resources: set[str],
    ) -> bool:
        if requested_resource in policy_resources:
            return True

        if (
            requested_resource.startswith("project:")
            and "project:*" in policy_resources
        ):
            return True

        if (
            requested_resource.startswith(
                "user:owner:project:"
            )
            and "user:owner:project:*"
            in policy_resources
        ):
            return True

        if (
            requested_resource.startswith("model:")
            and "model:*" in policy_resources
        ):
            return True

        return False

    def is_allowed(
        self,
        identity: Identity,
        action: str,
        resource: str,
    ) -> bool:
        matching_allow = False
        principal = identity.principal

        for policy in self.policies:
            if principal not in policy["principals"]:
                continue

            if action not in policy["actions"]:
                continue

            if not self._resource_matches(
                resource,
                policy["resources"],
            ):
                continue

            if policy["effect"] == "deny":
                return False

            if policy["effect"] == "allow":
                matching_allow = True

        return matching_allow

    def check(
        self,
        identity: Identity,
        action: str,
        resource: str,
    ) -> None:
        if not self.is_allowed(
            identity,
            action,
            resource,
        ):
            raise PermissionError(
                f"Identity '{identity.identifier}' "
                f"is not allowed to perform "
                f"action '{action}' "
                f"on resource '{resource}'."
            )
