import json

from app.llm.service import ModelService
from app.security.identity import Identity


identity = Identity(user_id="owner", principal="owner")
model_service = ModelService(identity=identity)


def _extract_json(text: str) -> dict:
    """
    Extract a JSON object from the model response.
    """

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.startswith("json"):
            text = text[4:].strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "Model did not return a valid JSON object."
            )

        try:
            return json.loads(
                text[start:end + 1]
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Model returned malformed JSON."
            ) from exc


def diagnose_failure(
    architecture_plan: dict,
    execution_results: list[dict],
    execution_errors: list[dict],
    validation_results: list[dict],
) -> dict:
    """
    Ask the model to diagnose an implementation
    or validation failure.

    The model only diagnoses the problem.
    It does not execute tools.
    """

    prompt = f"""
You are the diagnosis agent for SpongeBob AI.

Your job is to analyze why a software implementation
failed and determine what should be fixed.

You DO NOT execute commands.

You DO NOT modify files.

You ONLY return a structured diagnosis.

ARCHITECTURE PLAN:
{json.dumps(architecture_plan, indent=2)}

EXECUTION RESULTS:
{json.dumps(execution_results, indent=2)}

EXECUTION ERRORS:
{json.dumps(execution_errors, indent=2)}

VALIDATION RESULTS:
{json.dumps(validation_results, indent=2)}

Return ONLY valid JSON.

Use exactly this structure:

{{
  "problem": "short description of the problem",
  "cause": "likely cause of the problem",
  "severity": "low|medium|high",
  "files_affected": [
    "relative/path/to/file"
  ],
  "recommended_action": "clear description of what should be fixed",
  "can_auto_fix": true
}}

Rules:

1. Base the diagnosis only on the supplied information.

2. Do not invent errors that are not present.

3. Do not invent files.

4. Use relative file paths.

5. Do not execute commands.

6. Do not modify files.

7. Set can_auto_fix to true only when the problem
   can reasonably be fixed by SpongeBob automatically.

8. Return JSON only.

9. Do not use Markdown.

10. Do not add explanations outside the JSON.
""".strip()

    raw_result = model_service.generate(prompt)

    diagnosis = _extract_json(raw_result)

    if not isinstance(diagnosis, dict):
        raise ValueError(
            "Diagnosis response must be a JSON object."
        )

    required_fields = {
        "problem",
        "cause",
        "severity",
        "files_affected",
        "recommended_action",
        "can_auto_fix",
    }

    missing = required_fields - diagnosis.keys()

    if missing:
        raise ValueError(
            f"Diagnosis is missing fields: {sorted(missing)}"
        )

    if diagnosis["severity"] not in {
        "low",
        "medium",
        "high",
    }:
        raise ValueError(
            "Diagnosis severity must be low, medium, or high."
        )

    if not isinstance(
        diagnosis["files_affected"],
        list,
    ):
        raise ValueError(
            "files_affected must be a list."
        )

    if not isinstance(
        diagnosis["can_auto_fix"],
        bool,
    ):
        raise ValueError(
            "can_auto_fix must be a boolean."
        )

    return diagnosis
