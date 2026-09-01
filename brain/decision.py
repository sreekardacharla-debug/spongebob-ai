from dataclasses import dataclass, field
from typing import Dict, List
import json


@dataclass
class Decision:
    name: str
    value: str
    source: str = "user"
    reason: str = ""
    status: str = "confirmed"


@dataclass
class ProjectState:
    goal: str = ""
    requirements: List[str] = field(default_factory=list)
    decisions: Dict[str, Decision] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    open_decisions: List[str] = field(default_factory=list)
    history: List[dict] = field(default_factory=list)

    def set_decision(
        self,
        name: str,
        value: str,
        source: str = "user",
        reason: str = "",
    ):
        old_value = None

        if name in self.decisions:
            old_value = self.decisions[name].value

        self.decisions[name] = Decision(
            name=name,
            value=value,
            source=source,
            reason=reason,
            status="confirmed",
        )

        self.history.append({
            "type": "decision",
            "name": name,
            "old_value": old_value,
            "new_value": value,
            "source": source,
            "reason": reason,
        })

    def add_requirement(self, requirement: str):
        if requirement not in self.requirements:
            self.requirements.append(requirement)

    def add_assumption(self, assumption: str):
        if assumption not in self.assumptions:
            self.assumptions.append(assumption)

    def add_open_decision(self, decision: str):
        if decision not in self.open_decisions:
            self.open_decisions.append(decision)

    def resolve_open_decision(self, decision: str):
        if decision in self.open_decisions:
            self.open_decisions.remove(decision)

    def snapshot(self):
        return {
            "goal": self.goal,
            "requirements": self.requirements,
            "decisions": {
                key: {
                    "name": value.name,
                    "value": value.value,
                    "source": value.source,
                    "reason": value.reason,
                    "status": value.status,
                }
                for key, value in self.decisions.items()
            },
            "assumptions": self.assumptions,
            "open_decisions": self.open_decisions,
            "history": self.history,
        }

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.snapshot(), f, indent=2)

    @classmethod
    def load(cls, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        state = cls(
            goal=data.get("goal", ""),
            requirements=data.get("requirements", []),
            assumptions=data.get("assumptions", []),
            open_decisions=data.get("open_decisions", []),
            history=data.get("history", []),
        )

        for key, value in data.get("decisions", {}).items():
            state.decisions[key] = Decision(
                name=value["name"],
                value=value["value"],
                source=value.get("source", "user"),
                reason=value.get("reason", ""),
                status=value.get("status", "confirmed"),
            )

        return state