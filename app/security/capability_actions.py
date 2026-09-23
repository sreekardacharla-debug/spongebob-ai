from app.security.capabilities import Capability


CAPABILITY_ACTIONS = {
    Capability.FILESYSTEM_READ: "read_file",
    Capability.FILESYSTEM_WRITE: "write_file",
    Capability.FILESYSTEM_CREATE: "create_file",
    Capability.FILESYSTEM_DELETE: "delete_file",
    Capability.FILESYSTEM_COPY: "copy",
    Capability.FILESYSTEM_MOVE: "move",
    Capability.TERMINAL_EXECUTE: "run_command",
    Capability.PROJECT_INSPECT: "read_file",
    Capability.MODEL_INVOKE: "model_invoke",
}


def action_for_capability(
    capability: Capability,
) -> str:
    """
    Return the PolicyEngine action associated
    with a capability.
    """

    try:
        return CAPABILITY_ACTIONS[capability]
    except KeyError:
        raise ValueError(
            f"No action is defined for capability: {capability}"
        )
