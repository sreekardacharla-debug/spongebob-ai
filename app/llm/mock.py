import json

from app.llm.provider import LLMProvider


class MockLLM(LLMProvider):
    """
    Deterministic local provider used for development and tests.

    It simulates the STRUCTURE of model responses so we can test
    SpongeBob's Python architecture without consuming API credits.

    It is not intended to replace the real Qwen model.
    """

    def __init__(self):
        self.call_count = 0

    def generate(
        self,
        messages: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:

        self.call_count += 1

        prompt = ""

        for message in messages:
            if message.get("role") in {
                "system",
                "user",
            }:
                prompt += (
                    message.get("content", "")
                    + "\n"
                )

        lowered = prompt.lower()

        # =========================================================
        # CONSOLIDATED AGENT ANALYSIS
        # =========================================================

        if (
            "central reasoning layer of spongebob ai"
            in lowered
            or
            "consolidated engineering reasoning engine"
            in lowered
        ):

            if "cost optimization" in lowered:
                return json.dumps(
                    {
                        "understanding": {
                            "goal": (
                                "Build an AI cost "
                                "optimization web application"
                            ),
                            "task_type": (
                                "web_app_development"
                            ),
                            "summary": (
                                "The user wants a web "
                                "application for AI cost "
                                "optimization."
                            ),
                        },
                        "requirements": {
                            "confirmed": [
                                "web application",
                                "AI cost optimization",
                            ],
                            "new_unknowns": [
                                "target_users",
                                "technology_stack",
                            ],
                            "important_missing": [
                                "target_users",
                            ],
                        },
                        "readiness": {
                            "level": "NOT_READY",
                            "reason": (
                                "The product purpose is "
                                "known, but target users "
                                "are still unresolved."
                            ),
                        },
                        "next_action": {
                            "type": "clarify",
                            "question": (
                                "Who are the primary "
                                "users of this platform?"
                            ),
                            "decision_area": "",
                            "reason": (
                                "Target users affect "
                                "product workflow and UI."
                            ),
                        },
                    }
                )

            return json.dumps(
                {
                    "understanding": {
                        "goal": (
                            "Understand and respond "
                            "to the user's request"
                        ),
                        "task_type": "general",
                        "summary": (
                            "The user's request "
                            "requires analysis."
                        ),
                    },
                    "requirements": {
                        "confirmed": [],
                        "new_unknowns": [],
                        "important_missing": [],
                    },
                    "readiness": {
                        "level": "READY_FOR_EXECUTION",
                        "reason": (
                            "No project-specific "
                            "requirements are blocking "
                            "a response."
                        ),
                    },
                    "next_action": {
                        "type": "answer",
                        "question": "",
                        "decision_area": "",
                        "reason": "",
                    },
                }
            )

        # =========================================================
        # REQUIREMENT EXTRACTION
        # =========================================================

        if (
            "structured requirement extraction"
            in lowered
        ):
            return json.dumps(
                {
                    "field": "project_purpose",
                    "value": (
                        "AI cost optimization "
                        "platform for companies"
                    ),
                    "confidence": "high",
                    "additional_requirements": [],
                    "still_unknown": [],
                }
            )

        # =========================================================
        # READINESS
        # =========================================================

        if (
            "senior engineering readiness evaluator"
            in lowered
        ):

            if "cost optimization" not in lowered:
                return json.dumps(
                    {
                        "readiness": "NOT_READY",
                        "reason": (
                            "Project purpose is "
                            "not defined."
                        ),
                        "missing_critical_information": [
                            "project_purpose"
                        ],
                        "recommended_next_area": "",
                    }
                )

            return json.dumps(
                {
                    "readiness": (
                        "READY_FOR_ARCHITECTURE"
                    ),
                    "reason": (
                        "The product purpose and "
                        "core functionality are "
                        "sufficiently defined."
                    ),
                    "missing_critical_information": [],
                    "recommended_next_area": (
                        "frontend_framework"
                    ),
                }
            )

        # =========================================================
        # REQUIREMENTS MANAGER
        # =========================================================

        if (
            "adaptive requirements-management"
            in lowered
        ):
            return json.dumps(
                {
                    "action": "clarify",
                    "question": (
                        "Who are the primary users "
                        "of this platform?"
                    ),
                    "reason": (
                        "Target users affect "
                        "workflow and UI."
                    ),
                    "priority": "high",
                    "blocks_execution": True,
                    "decision_area": "",
                    "confirmed_information": [],
                    "new_unknowns": [
                        "target_users"
                    ],
                    "readiness": "NOT_READY",
                }
            )

        # =========================================================
        # ARCHITECTURE RECOMMENDATION
        # =========================================================

        if (
            "software architecture decision assistant"
            in lowered
        ):
            return json.dumps(
                {
                    "decision_area": (
                        "frontend_framework"
                    ),
                    "recommended_option": "Next.js",
                    "recommendation_reason": (
                        "Next.js provides a strong "
                        "foundation for a modern "
                        "production web application."
                    ),
                    "options": [
                        {
                            "name": "Next.js",
                            "advantages": [
                                "React ecosystem",
                                "Integrated routing",
                                "Full-stack capabilities",
                            ],
                            "disadvantages": [
                                "More complexity "
                                "than a simple SPA"
                            ],
                            "best_when": (
                                "You want a production "
                                "web application."
                            ),
                        },
                        {
                            "name": "React + Vite",
                            "advantages": [
                                "Simple setup",
                                "Fast development",
                            ],
                            "disadvantages": [
                                "More architecture "
                                "must be chosen separately"
                            ],
                            "best_when": (
                                "You want a lightweight "
                                "frontend."
                            ),
                        },
                    ],
                    "tradeoffs": [
                        (
                            "Next.js provides more "
                            "integrated application "
                            "capabilities."
                        ),
                        (
                            "React + Vite is simpler "
                            "but requires more decisions."
                        ),
                    ],
                    "requires_user_confirmation": True,
                }
            )

        # =========================================================
        # DECISION CHOICE
        # =========================================================

        if (
            "extract confirmed technical decisions"
            in lowered
        ):
            if "next.js" in lowered:
                return json.dumps(
                    {
                        "confirmed": True,
                        "selected_option": "Next.js",
                        "reason": (
                            "The user explicitly "
                            "selected Next.js."
                        ),
                        "needs_clarification": False,
                    }
                )

            return json.dumps(
                {
                    "confirmed": False,
                    "selected_option": "",
                    "reason": "",
                    "needs_clarification": True,
                }
            )

        # =========================================================
        # FALLBACK
        # =========================================================

        return json.dumps(
            {
                "message": "Mock LLM response."
            }
        )