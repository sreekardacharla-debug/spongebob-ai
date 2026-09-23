from app.memory.decision_history import DecisionHistory


def test_add_decision():
    history = DecisionHistory()

    record = history.add(
        decision="database",
        value="MySQL",
    )

    assert record.decision == "database"
    assert record.value == "MySQL"
    assert record.source == "user"


def test_latest_returns_most_recent_decision():
    history = DecisionHistory()

    history.add("database", "MySQL")
    history.add("database", "PostgreSQL")

    latest = history.latest("database")

    assert latest["value"] == "PostgreSQL"


def test_all_returns_decisions():
    history = DecisionHistory()

    history.add("frontend", "React")
    history.add("backend", "Spring Boot")

    records = history.all()

    assert len(records) == 2
    assert records[0]["value"] == "React"
    assert records[1]["value"] == "Spring Boot"


def test_latest_returns_none_for_unknown_decision():
    history = DecisionHistory()

    assert history.latest("database") is None


def test_clear_removes_all_decisions():
    history = DecisionHistory()

    history.add("database", "MySQL")
    history.clear()

    assert history.all() == []
