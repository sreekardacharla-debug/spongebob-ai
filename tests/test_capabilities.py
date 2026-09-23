from app.security.capabilities import Capability
from app.security.capability_actions import (
    action_for_capability,
)
from app.security.capability_authorizer import (
    CapabilityAuthorizer,
)
from app.security.capability_request import (
    CapabilityRequest,
)
from app.security.identity import Identity
from app.security.resources import Resources


def owner_identity():
    return Identity(
        user_id="owner",
        principal="owner",
    )


def friend_identity():
    return Identity(
        user_id="friend1",
        principal="friend",
    )


def test_capability_values():
    assert (
        Capability.FILESYSTEM_READ.value
        == "filesystem.read"
    )

    assert (
        Capability.TERMINAL_EXECUTE.value
        == "terminal.execute"
    )

    assert (
        Capability.MODEL_INVOKE.value
        == "model.invoke"
    )


def test_capability_maps_to_action():
    assert (
        action_for_capability(
            Capability.FILESYSTEM_READ
        )
        == "read_file"
    )

    assert (
        action_for_capability(
            Capability.FILESYSTEM_WRITE
        )
        == "write_file"
    )

    assert (
        action_for_capability(
            Capability.TERMINAL_EXECUTE
        )
        == "run_command"
    )


def test_owner_filesystem_capability_allowed():
    request = CapabilityRequest(
        identity=owner_identity(),
        capability=Capability.FILESYSTEM_READ,
        resource=Resources.WORKSPACE,
    )

    authorizer = CapabilityAuthorizer()

    assert authorizer.is_allowed(
        request
    )


def test_friend_workspace_capability_denied():
    request = CapabilityRequest(
        identity=friend_identity(),
        capability=Capability.FILESYSTEM_READ,
        resource=Resources.WORKSPACE,
    )

    authorizer = CapabilityAuthorizer()

    assert not authorizer.is_allowed(
        request
    )


def test_owner_terminal_capability_allowed():
    request = CapabilityRequest(
        identity=owner_identity(),
        capability=Capability.TERMINAL_EXECUTE,
        resource=Resources.WORKSPACE,
    )

    authorizer = CapabilityAuthorizer()

    assert authorizer.is_allowed(
        request
    )


def test_protected_resource_denied():
    request = CapabilityRequest(
        identity=owner_identity(),
        capability=Capability.FILESYSTEM_READ,
        resource=Resources.PROTECTED_SPONGEBOB_CODE,
    )

    authorizer = CapabilityAuthorizer()

    assert not authorizer.is_allowed(
        request
    )


def test_check_allows_owner():
    request = CapabilityRequest(
        identity=owner_identity(),
        capability=Capability.FILESYSTEM_READ,
        resource=Resources.WORKSPACE,
    )

    authorizer = CapabilityAuthorizer()

    authorizer.check(request)


def test_check_denies_friend():
    request = CapabilityRequest(
        identity=friend_identity(),
        capability=Capability.FILESYSTEM_READ,
        resource=Resources.WORKSPACE,
    )

    authorizer = CapabilityAuthorizer()

    try:
        authorizer.check(request)
        assert False
    except PermissionError:
        assert True

def test_owner_model_invoke_allowed():
    request = CapabilityRequest(
        identity=owner_identity(),
        capability=Capability.MODEL_INVOKE,
        resource="model:qwen",
    )
    authorizer = CapabilityAuthorizer()
    assert authorizer.is_allowed(request)


def test_friend_model_invoke_denied():
    request = CapabilityRequest(
        identity=friend_identity(),
        capability=Capability.MODEL_INVOKE,
        resource="model:qwen",
    )
    authorizer = CapabilityAuthorizer()
    assert not authorizer.is_allowed(request)
