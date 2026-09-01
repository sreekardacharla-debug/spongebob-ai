import json


class ContextManager:
    """
    Manages the amount of conversation context sent to the LLM.

    Strategy:
    - Keep the most recent messages in full.
    - Compress older messages into a summary.
    - Keep structured project state separately.
    """

    def __init__(
        self,
        max_recent_messages: int = 12,
        max_summary_chars: int = 6000,
    ):
        self.max_recent_messages = max_recent_messages
        self.max_summary_chars = max_summary_chars

    def build_context(
        self,
        conversation: list[dict],
        project_state: dict,
        summary: str = "",
    ) -> dict:
        """
        Build the model-facing context.

        Older conversation is represented by the summary,
        while recent messages remain intact.
        """

        recent_messages = conversation[
            -self.max_recent_messages:
        ]

        older_messages = conversation[
            :-self.max_recent_messages
        ]

        if older_messages and not summary:
            summary = self._create_local_summary(
                older_messages
            )

        summary = self._limit_summary(
            summary
        )

        return {
            "conversation_summary": summary,
            "recent_messages": recent_messages,
            "project_state": project_state,
        }

    def _create_local_summary(
        self,
        messages: list[dict],
    ) -> str:
        """
        Create a deterministic summary without calling an LLM.

        This is intentionally simple for now. Later, we can add
        an LLM-powered summarizer when a model provider is available.
        """

        if not messages:
            return ""

        lines = []

        for message in messages:
            role = message.get(
                "role",
                "unknown",
            )

            content = message.get(
                "content",
                "",
            ).strip()

            if not content:
                continue

            lines.append(
                f"{role}: {content}"
            )

        summary = "\n".join(lines)

        return summary

    def _limit_summary(
        self,
        summary: str,
    ) -> str:
        if len(summary) <= self.max_summary_chars:
            return summary

        return (
            summary[
                -self.max_summary_chars:
            ]
        )

    def build_model_messages(
        self,
        context: dict,
        system_instruction: str = "",
    ) -> list[dict]:
        """
        Convert managed context into LLM chat messages.
        """

        messages = []

        if system_instruction:
            messages.append(
                {
                    "role": "system",
                    "content": system_instruction,
                }
            )

        summary = context.get(
            "conversation_summary",
            "",
        )

        recent_messages = context.get(
            "recent_messages",
            [],
        )

        project_state = context.get(
            "project_state",
            {},
        )

        if summary:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Summary of earlier conversation:\n"
                        + summary
                    ),
                }
            )

        if project_state:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Current project state:\n"
                        + json.dumps(
                            project_state,
                            indent=2,
                        )
                    ),
                }
            )

        messages.extend(
            recent_messages
        )

        return messages