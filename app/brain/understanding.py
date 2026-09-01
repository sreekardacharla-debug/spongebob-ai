import json
from app.llm.qwen import QwenClient


class UnderstandingEngine:

    def __init__(self, llm=None):
        self.llm = llm or QwenClient()

    def analyze(self, user_message: str, context: dict | None = None) -> dict:

        context = context or {}

        prompt = f"""
You are the task-understanding layer of SpongeBob AI.

Your job is NOT to execute the user's request.
Your job is to understand what the user actually wants and determine
whether SpongeBob should answer, ask a clarification question, plan,
or prepare for execution.

You are acting like a highly experienced software engineer.

Current context:
{json.dumps(context, indent=2)}

User request:
{user_message}

Return ONLY valid JSON using this exact structure:

{{
  "goal": "",
  "task_type": "",
  "summary": "",
  "needs_clarification": false,
  "clarification_questions": [],
  "known_requirements": [],
  "unknown_requirements": [],
  "possible_tools": [],
  "execution_ready": false,
  "risk_level": "low"
}}

Rules:

1. Understand the user's actual goal, not just keywords.
2. Do not blindly assume technologies or architecture.
3. Ask clarification only when the missing information materially
   changes the answer or implementation.
4. Do not ask unnecessary questions for simple requests.
5. For software projects, identify important missing decisions such as
   frontend, backend, database, API, authentication, deployment,
   or constraints only when relevant.
6. Distinguish what the user explicitly said from what is unknown.
7. Do not execute tools.
8. Do not claim that anything has been created, changed, tested,
   or completed.
"""

        response = self.llm.generate(
            [
                {
                    "role": "system",
                    "content": "You are a precise task-understanding engine."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1500,
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
                "Qwen returned invalid understanding JSON."
            ) from exc