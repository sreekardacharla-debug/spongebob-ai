from enum import Enum


class Capability(str, Enum):
    """
    Controlled capabilities that SpongeBob AI can request.

    The LLM can request a capability, but the capability
    itself does not grant permission. PolicyEngine still
    decides whether the identity may use it.
    """

    FILESYSTEM_READ = "filesystem.read"

    FILESYSTEM_WRITE = "filesystem.write"

    FILESYSTEM_CREATE = "filesystem.create"

    FILESYSTEM_DELETE = "filesystem.delete"

    FILESYSTEM_COPY = "filesystem.copy"

    FILESYSTEM_MOVE = "filesystem.move"

    TERMINAL_EXECUTE = "terminal.execute"

    PROJECT_INSPECT = "project.inspect"

    MODEL_INVOKE = "model.invoke"
