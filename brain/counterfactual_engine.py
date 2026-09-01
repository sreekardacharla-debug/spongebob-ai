import json

from brain.counterfactual import CounterfactualResult, Impact
from brain.decision import ProjectState
from llm.qwen_sglang import QwenSGLangLLM


class CounterfactualEngine:

    def __init__(self, llm=None):
        self.llm = llm or QwenSGLangLLM()

    def analyze(
        self,
        state: ProjectState,
        decision_name: str,
        proposed_value: str,
    ) -> CounterfactualResult:

        current_value = ""

        if decision_name in state.decisions:
            current_value = state.decisions[decision_name].value

        project_state = state.snapshot()

        prompt = f"""
You are SpongeBob AI acting as a senior software engineer.

You are analyzing a proposed architectural change BEFORE it is applied
to a real software project.

Current project state:
{json.dumps(project_state, indent=2)}

Proposed decision change:
Decision: {decision_name}
Current value: {current_value or "Not decided"}
Proposed value: {proposed_value}

Analyze the likely engineering impact.

Return ONLY valid JSON with this structure:

{{
  "benefits": [],
  "risks": [],
  "impacts": [
    {{
      "area": "",
      "current_state": "",
      "proposed_state": "",
      "impact": "",
      "affected_components": []
    }}
  ],
  "requires_confirmation": true
}}

Rules:
- Do not claim that a file was changed.
- Do not claim that a command was executed.
- Analyze consequences only.
- Consider architecture, dependencies, APIs, testing, deployment,
  security, and maintainability when relevant.
- Only include impacts that are reasonably connected to the proposed change.
"""

        response = self.llm.generate(prompt)

        data = self._parse_json(response)

        impacts = [
            Impact(
                area=item.get("area", ""),
                current_state=item.get("current_state", ""),
                proposed_state=item.get("proposed_state", ""),
                impact=item.get("impact", ""),
                affected_components=item.get(
                    "affected_components", []
                ),
            )
            for item in data.get("impacts", [])
        ]

        return CounterfactualResult(
            decision=decision_name,
            current_value=current_value,
            proposed_value=proposed_value,
            benefits=data.get("benefits", []),
            risks=data.get("risks", []),
            impacts=impacts,
            requires_confirmation=data.get(
                "requires_confirmation",
                True,
            ),
        )

    @staticmethod
    def _parse_json(response: str) -> dict:

        response = response.strip()

        if response.startswith("```"):
            lines = response.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            response = "\n".join(lines).strip()

        try:
            return json.loads(response)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Qwen returned invalid counterfactual JSON"
            ) from exc