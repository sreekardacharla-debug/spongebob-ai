from dataclasses import dataclass, field
from typing import List


@dataclass
class Impact:
    area: str
    current_state: str
    proposed_state: str
    impact: str
    affected_components: List[str] = field(default_factory=list)


@dataclass
class CounterfactualResult:
    decision: str
    current_value: str
    proposed_value: str
    benefits: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    impacts: List[Impact] = field(default_factory=list)
    requires_confirmation: bool = True

    def summary(self):
        return {
            "decision": self.decision,
            "current_value": self.current_value,
            "proposed_value": self.proposed_value,
            "benefits": self.benefits,
            "risks": self.risks,
            "impacts": [
                {
                    "area": impact.area,
                    "current_state": impact.current_state,
                    "proposed_state": impact.proposed_state,
                    "impact": impact.impact,
                    "affected_components": impact.affected_components,
                }
                for impact in self.impacts
            ],
            "requires_confirmation": self.requires_confirmation,
        }