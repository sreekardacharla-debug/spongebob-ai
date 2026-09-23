from app.security.identity import Identity
from app.security.policy_engine import PolicyEngine
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


def test_owner_can_read_workspace():
    policy = PolicyEngine()

    assert policy.is_allowed(
        owner_identity(),
        "read_file",
        Resources.WORKSPACE,
    )


def test_owner_can_write_workspace():
    policy = PolicyEngine()

    assert policy.is_allowed(
        owner_identity(),
        "write_file",
        Resources.WORKSPACE,
    )


def test_owner_can_create_file():
    policy = PolicyEngine()

    assert policy.is_allowed(
        owner_identity(),
        "create_file",
        Resources.WORKSPACE,
    )


def test_owner_can_delete_file():
    policy = PolicyEngine()

    assert policy.is_allowed(
        owner_identity(),
        "delete_file",
        Resources.WORKSPACE,
    )


def test_owner_can_create_directory():
    policy = PolicyEngine()

    assert policy.is_allowed(
        owner_identity(),
        "create_directory",
        Resources.WORKSPACE,
    )


def test_owner_can_delete_directory():
    policy = PolicyEngine()

    assert policy.is_allowed(
        owner_identity(),
        "delete_directory",
        Resources.WORKSPACE,
    )


def test_owner_can_copy():
    policy = PolicyEngine()

    assert policy.is_allowed(
        owner_identity(),
        "copy",
        Resources.WORKSPACE,
    )


def test_owner_can_move():
    policy = PolicyEngine()

    assert policy.is_allowed(
        owner_identity(),
        "move",
        Resources.WORKSPACE,
    )


def test_owner_can_run_command():
    policy = PolicyEngine()

    assert policy.is_allowed(
        owner_identity(),
        "run_command",
        Resources.WORKSPACE,
    )


def test_friend_cannot_access_workspace_by_default():
    policy = PolicyEngine()

    assert not policy.is_allowed(
        friend_identity(),
        "read_file",
        Resources.WORKSPACE,
    )


def test_friend_cannot_write_workspace_by_default():
    policy = PolicyEngine()

    assert not policy.is_allowed(
        friend_identity(),
        "write_file",
        Resources.WORKSPACE,
    )


def test_unknown_principal_denied():
    policy = PolicyEngine()

    identity = Identity(
        user_id="user123",
        principal="unknown",
    )

    assert not policy.is_allowed(
        identity,
        "read_file",
        Resources.WORKSPACE,
    )


def test_deny_overrides_allow():
    policy = PolicyEngine()

    policy.add_policy(
        effect="allow",
        principals={"friend"},
        actions={"read_file"},
        resources={"project:test"},
    )

    policy.add_policy(
        effect="deny",
        principals={"friend"},
        actions={"read_file"},
        resources={"project:test"},
    )

    assert not policy.is_allowed(
        friend_identity(),
        "read_file",
        "project:test",
    )


def test_owner_user_project_access():
    policy = PolicyEngine()

    identity = owner_identity()

    resource = Resources.user_project(
        "owner",
        "portfolio",
    )

    assert policy.is_allowed(
        identity,
        "read_file",
        resource,
    )


def test_owner_user_project_write_access():
    policy = PolicyEngine()

    identity = owner_identity()

    resource = Resources.user_project(
        "owner",
        "portfolio",
    )

    assert policy.is_allowed(
        identity,
        "write_file",
        resource,
    )


def test_owner_user_project_delete_access():
    policy = PolicyEngine()

    identity = owner_identity()

    resource = Resources.user_project(
        "owner",
        "portfolio",
    )

    assert policy.is_allowed(
        identity,
        "delete_file",
        resource,
    )


def test_owner_user_project_command_access():
    policy = PolicyEngine()

    identity = owner_identity()

    resource = Resources.user_project(
        "owner",
        "portfolio",
    )

    assert policy.is_allowed(
        identity,
        "run_command",
        resource,
    )


def test_friend_project_isolation():
    policy = PolicyEngine()

    friend = friend_identity()

    friend_resource = Resources.user_project(
        "friend1",
        "portfolio",
    )

    owner_resource = Resources.user_project(
        "owner",
        "portfolio",
    )

    policy.add_policy(
        effect="allow",
        principals={"friend"},
        actions={"read_file"},
        resources={
            friend_resource,
        },
    )

    assert policy.is_allowed(
        friend,
        "read_file",
        friend_resource,
    )

    assert not policy.is_allowed(
        friend,
        "read_file",
        owner_resource,
    )


def test_friend_cannot_access_another_friend_project():
    policy = PolicyEngine()

    friend = friend_identity()

    friend1_project = Resources.user_project(
        "friend1",
        "portfolio",
    )

    friend2_project = Resources.user_project(
        "friend2",
        "portfolio",
    )

    policy.add_policy(
        effect="allow",
        principals={"friend"},
        actions={"read_file"},
        resources={
            friend1_project,
        },
    )

    assert policy.is_allowed(
        friend,
        "read_file",
        friend1_project,
    )

    assert not policy.is_allowed(
        friend,
        "read_file",
        friend2_project,
    )


def test_user_project_resource_format():
    resource = Resources.user_project(
        "friend1",
        "portfolio",
    )

    assert resource == (
        "user:friend1:project:portfolio"
    )


def test_project_resource_format():
    resource = Resources.project(
        "portfolio",
    )

    assert resource == "project:portfolio"


def test_protected_spongebob_code_denied():
    policy = PolicyEngine()

    assert not policy.is_allowed(
        owner_identity(),
        "read_file",
        Resources.PROTECTED_SPONGEBOB_CODE,
    )


def test_protected_credentials_denied():
    policy = PolicyEngine()

    assert not policy.is_allowed(
        owner_identity(),
        "read_file",
        Resources.PROTECTED_CREDENTIALS,
    )


def test_protected_private_data_denied():
    policy = PolicyEngine()

    assert not policy.is_allowed(
        owner_identity(),
        "read_file",
        Resources.PROTECTED_PRIVATE_DATA,
    )


def test_friend_protected_code_denied():
    policy = PolicyEngine()

    assert not policy.is_allowed(
        friend_identity(),
        "read_file",
        Resources.PROTECTED_SPONGEBOB_CODE,
    )


def test_friend_protected_credentials_denied():
    policy = PolicyEngine()

    assert not policy.is_allowed(
        friend_identity(),
        "read_file",
        Resources.PROTECTED_CREDENTIALS,
    )


def test_check_allows_valid_request():
    policy = PolicyEngine()

    policy.check(
        owner_identity(),
        "read_file",
        Resources.WORKSPACE,
    )


def test_check_raises_for_denied_request():
    policy = PolicyEngine()

    try:
        policy.check(
            friend_identity(),
            "read_file",
            Resources.WORKSPACE,
        )
        assert False
    except PermissionError:
        assert True
