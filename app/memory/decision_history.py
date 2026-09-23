from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass(frozen=True)
class DecisionRecord:
    decision: str
    value: str
    source: str
    timestamp: str


class DecisionHistory:
    """
    Stores important decisions made during a SpongeBob session.
    """

    def __init__(self):
        self._records: list[DecisionRecord] = []

    def add(
        self,
        decision: str,
        value: str,
        source: str = "user",
    ) -> DecisionRecord:
        record = DecisionRecord(
            decision=decision,
            value=value,
            source=source,
            timestamp=datetime.now().isoformat(),
        )

        self._records.append(record)
        return record

    def all(self) -> list[dict]:
        return [
            asdict(record)
            for record in self._records
        ]

    def latest(self, decision: str) -> dict | None:
        for record in reversed(self._records):
            if record.decision == decision:
                return asdict(record)

        return None

    def clear(self) -> None:
        self._records.clear()
