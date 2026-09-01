import json

from app.llm.qwen import QwenClient


class RequirementsManager:

    def __init__(self, llm=None):
        self.llm = llm or QwenClient()

    def extract_answer(
        self,
        question: str,
        answer: str,
        context: dict | None = None,
    ) -> dict:

        context = context or {}

        prompt = f"""
You are the structured requirement extraction layer of SpongeBob AI.

Clarification question:
{question}

User answer:
{answer}

Current project context:
{json.dumps(context, indent=2)}

Return ONLY valid JSON:

{{
  "field": "",
  "value": "",
  "confidence": "high",
  "additional_requirements": [],
  "still_unknown": []
}}

Rules:
1. Extract only information supported by the answer.
2. Do not invent missing details.
3. Use stable field names such as:
   project_purpose
   target_users
   core_features
   frontend
   backend
   database
   authentication
   deployment
   integrations
   constraints
4. If multiple requirements are stated, put additional ones in
   additional_requirements.
5. Do not treat an unanswered question as answered.
"""

        response = self.llm.generate(
            [
                {
                    "role": "system",
                    "content": (
                        "Extract structured software "
                        "requirements accurately."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.0,
            max_tokens=800,
        )

        return self._parse_response(response)

    def assess_readiness(
        self,
        context: dict,
    ) -> dict:

        prompt = f"""
You are the senior engineering readiness evaluator for SpongeBob AI.

Your job is to decide whether enough information is known to move
from requirements discovery into ARCHITECTURAL decisions.

Current project context:
{json.dumps(context, indent=2)}

Return ONLY valid JSON:

{{
  "readiness": "NOT_READY",
  "reason": "",
  "missing_critical_information": [],
  "recommended_next_area": ""
}}

Allowed readiness values:

"NOT_READY"
    A missing requirement could materially change the architecture,
    product design, or engineering approach.

"READY_FOR_ARCHITECTURE"
    The product purpose, core functionality, and primary users are
    sufficiently understood to begin discussing technical architecture.

"READY_FOR_EXECUTION"
    Major requirements and consequential technical decisions have
    already been confirmed.

Rules:
1. Do not demand every possible detail.
2. Product purpose must be understood.
3. Core functionality must be understood.
4. Primary target users must be known before declaring
   READY_FOR_ARCHITECTURE unless users genuinely do not affect
   the architecture.
5. Do not treat technical stack choices as already decided.
6. Do not use a user-requirement question as a "technical decision."
7. recommended_next_area must be a REAL technical/architectural area,
   such as:
   frontend_framework
   backend_framework
   database
   authentication
   deployment
   architecture
8. If a critical user/product requirement is missing, return
   NOT_READY instead.
"""

        response = self.llm.generate(
            [
                {
                    "role": "system",
                    "content": (
                        "You evaluate software-project readiness "
                        "from a senior engineering perspective."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.0,
            max_tokens=800,
        )

        return self._parse_response(response)

    def determine_next_step(
        self,
        understanding: dict,
        context: dict | None = None,
    ) -> dict:

        context = context or {}

        readiness = self.assess_readiness(
            context
        )

        readiness_value = readiness.get(
            "readiness",
            "NOT_READY",
        )

        if readiness_value == "READY_FOR_ARCHITECTURE":

            decision_area = (
                readiness.get(
                    "recommended_next_area"
                )
                or "architecture"
            )

            return {
                "action": "recommend",
                "question": "",
                "reason": readiness.get(
                    "reason",
                    "Enough information is available to begin architecture decisions.",
                ),
                "priority": "high",
                "blocks_execution": True,
                "decision_area": decision_area,
                "confirmed_information": context.get(
                    "known_requirements",
                    [],
                ),
                "new_unknowns": readiness.get(
                    "missing_critical_information",
                    [],
                ),
                "readiness": "READY_FOR_ARCHITECTURE",
            }

        if readiness_value == "READY_FOR_EXECUTION":

            return {
                "action": "proceed",
                "question": "",
                "reason": (
                    "Major requirements and technical decisions "
                    "are sufficiently established for execution planning."
                ),
                "priority": "high",
                "blocks_execution": False,
                "decision_area": "",
                "confirmed_information": context.get(
                    "known_requirements",
                    [],
                ),
                "new_unknowns": [],
                "readiness": "READY_FOR_EXECUTION",
            }

        prompt = f"""
You are SpongeBob AI's adaptive requirements-management layer.

Act like a highly experienced software engineer working with a real client.

Your job is to ask the NEXT most valuable question only when necessary.

Understanding:
{json.dumps(understanding, indent=2)}

Project context:
{json.dumps(context, indent=2)}

Return ONLY valid JSON:

{{
  "action": "clarify",
  "question": "",
  "reason": "",
  "priority": "high",
  "blocks_execution": true,
  "decision_area": "",
  "confirmed_information": [],
  "new_unknowns": [],
  "readiness": "NOT_READY"
}}

Rules:
1. Ask at most ONE question.
2. Ask only what materially changes the next engineering decision.
3. Never ask for information already confirmed.
4. Never silently invent important requirements.
5. Do not ask for details that can safely be decided later.
6. Do not ask for information that can be discovered from the
   user's project or environment.
7. Prefer progressive discovery.
8. If target users materially affect the product, ask for them
   before technical architecture decisions.
"""

        response = self.llm.generate(
            [
                {
                    "role": "system",
                    "content": (
                        "You are an adaptive requirements manager "
                        "for a senior software-engineering agent."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            max_tokens=1200,
        )

        result = self._parse_response(
            response
        )

        result["readiness"] = "NOT_READY"

        return result

    @staticmethod
    def _parse_response(
        response: str,
    ) -> dict:

        response = response.strip()

        if response.startswith("```"):
            lines = response.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            response = "\n".join(
                lines
            ).strip()

        try:
            return json.loads(response)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Qwen returned invalid requirements JSON."
            ) from exc