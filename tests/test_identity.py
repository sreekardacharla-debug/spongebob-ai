from app.security.identity import Identity


def test_identity_creation():
    identity = Identity(
        user_id="friend1",
        principal="friend",
    )

    assert identity.user_id == "friend1"
    assert identity.principal == "friend"


def test_identity_identifier():
    identity = Identity(
        user_id="friend1",
        principal="friend",
    )

    assert identity.identifier == "friend:friend1"


def test_owner_identity():
    identity = Identity(
        user_id="owner123",
        principal="owner",
    )

    assert identity.user_id == "owner123"
    assert identity.principal == "owner"
    assert identity.identifier == "owner:owner123"


def test_empty_user_id_rejected():
    try:
        Identity(
            user_id="",
            principal="friend",
        )
        assert False
    except ValueError:
        assert True


def test_empty_principal_rejected():
    try:
        Identity(
            user_id="friend1",
            principal="",
        )
        assert False
    except ValueError:
        assert True
