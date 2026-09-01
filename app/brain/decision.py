import json

from app.llm.qwen import QwenClient


class DecisionEngine:

    def __init__(self, llm=None):
        self.llm = llm or QwenClient()

    def recommend(
        self,
        decision_area: str,
        context: dict | None = None,
    ) -> dict:
        """
        Analyze an unresolved architectural decision and recommend
        suitable options based on the current project context.
        """

        context = context or {}

        prompt = f"""
You are SpongeBob AI acting as a senior software engineer.

The project has reached an architectural decision point.

Decision area:
{decision_area}

Current project context:
{json.dumps(context, indent=2)}

Analyze the decision in the context of this project.

Return ONLY valid JSON:

{{
  "decision_area": "",
  "recommended_option": "",
  "recommendation_reason": "",
  "options": [
    {{
      "name": "",
      "advantages": [],
      "disadvantages": [],
      "best_when": ""
    }}
  ],
  "tradeoffs": [],
  "requires_user_confirmation": true
}}

Rules:
1. Do not make the final decision for the user.
2. Recommend one option when there is enough information.
3. Include a small number of useful alternatives.
4. Base the recommendation on the actual project context.
5. Do not invent requirements.
6. Focus on meaningful engineering tradeoffs.
7. Require user confirmation before committing the decision.
"""

        response = self.llm.generate(
            [
                {
                    "role": "system",
                    "content": (
                        "You are an experienced software "
                        "architecture decision assistant."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            max_tokens=1800,
        )

        return self._parse_response(response)

    def extract_choice(
        self,
        decision: dict,
        user_message: str,
    ) -> dict:
        """
        Determine whether the user selected one of the proposed
        options or requested another option.
        """

        prompt = f"""
You are processing a user's response to a software architecture
decision.

Decision:
{json.dumps(decision, indent=2)}

User response:
{user_message}

Return ONLY valid JSON:

{{
  "confirmed": false,
  "selected_option": "",
  "reason": "",
  "needs_clarification": false
}}

Rules:
1. Set confirmed=true only when the user's response clearly
   selects an option.
2. Match natural language choices such as:
   - "I'll use React"
   - "React"
   - "the first one"
   - "let's go with the recommended option"
3. Do not guess when the choice is ambiguous.
4. If ambiguous, set needs_clarification=true.
5. Do not invent an option that was not presented.
"""

        response = self.llm.generate(
            [
                {
                    "role": "system",
                    "content": (
                        "You extract confirmed technical "
                        "decisions from natural conversation."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.0,
            max_tokens=600,
        )

        return self._parse_response(response)

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

            response = "\n".join(lines).strip()

        try:
            return json.loads(response)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Qwen returned invalid decision JSON."
            ) from exc