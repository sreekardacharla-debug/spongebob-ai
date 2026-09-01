import json

from app.llm.qwen import QwenClient


class AgentAnalysisEngine:
    """
    Consolidates understanding, requirement analysis, readiness,
    and next-action selection into one model call.
    """

    def __init__(self, llm=None):
        self.llm = llm or QwenClient()

    def analyze(
        self,
        user_message: str,
        context: dict,
    ) -> dict:

        prompt = f"""
You are the central reasoning engine of SpongeBob AI.

Act like a senior software engineer.

Analyze the user's latest message together with the existing
project state.

USER MESSAGE:
{user_message}

CURRENT PROJECT STATE:
{json.dumps(context, indent=2)}

Return ONLY valid JSON:

{{
  "understanding": {{
    "goal": "",
    "task_type": "",
    "summary": ""
  }},
  "requirements": {{
    "confirmed": [],
    "new_unknowns": [],
    "important_missing": []
  }},
  "readiness": {{
    "level": "NOT_READY",
    "reason": ""
  }},
  "next_action": {{
    "type": "answer",
    "question": "",
    "decision_area": "",
    "reason": ""
  }}
}}

Allowed readiness:
- NOT_READY
- READY_FOR_ARCHITECTURE
- READY_FOR_EXECUTION

Allowed next_action types:
- answer
- clarify
- recommend
- proceed

Rules:
1. Understand the user's actual goal.
2. Never invent requirements.
3. Ask at most one clarification question.
4. Never ask for information already confirmed.
5. Use recommend only for a real technical decision.
6. Valid decision areas include:
   frontend_framework
   backend_framework
   database
   authentication
   deployment
   architecture
7. Do not use a product-requirement question as decision_area.
8. Use proceed only when execution can genuinely begin.
9. Keep the result concise.
"""

        response = self.llm.generate(
            [
                {
                    "role": "system",
                    "content": (
                        "You are SpongeBob AI's consolidated "
                        "engineering reasoning engine."
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

        return self._parse_response(response)

    @staticmethod
    def _parse_response(response: str) -> dict:

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
                "Qwen returned invalid consolidated analysis JSON."
            ) from exc