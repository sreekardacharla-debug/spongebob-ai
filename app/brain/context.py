import json
from dataclasses import dataclass, field
from typing import Any

from app.brain.memory import MemoryStore


@dataclass
class AgentContext:
    """
    Persistent state for the current SpongeBob session.

    Stores:
    - conversation history
    - known requirements
    - unresolved requirements
    - structured requirements
    - confirmed decisions
    - pending clarification question
    - pending technical decision
    - current goal
    - metadata

    The state can be saved to and restored from SQLite.
    """

    goal: str = ""

    conversation: list[dict[str, str]] = field(
        default_factory=list
    )

    known_requirements: list[str] = field(
        default_factory=list
    )

    unknown_requirements: list[str] = field(
        default_factory=list
    )

    structured_requirements: dict[str, dict] = field(
        default_factory=dict
    )

    decisions: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    pending_question: dict[str, Any] | None = None

    pending_decision: dict[str, Any] | None = None

    project_id: int | None = None

    conversation_id: int | None = None

    memory_store: MemoryStore | None = field(
        default=None,
        repr=False,
        compare=False,
    )

    def add_message(
        self,
        role: str,
        content: str,
    ) -> None:

        self.conversation.append(
            {
                "role": role,
                "content": content,
            }
        )

        if (
            self.memory_store
            and self.conversation_id
        ):
            self.memory_store.add_message(
                self.conversation_id,
                role,
                content,
            )

    def add_requirement(
        self,
        requirement: str,
    ) -> None:

        if requirement not in self.known_requirements:
            self.known_requirements.append(
                requirement
            )

    def add_unknown(
        self,
        requirement: str,
    ) -> None:

        if requirement not in self.unknown_requirements:
            self.unknown_requirements.append(
                requirement
            )

    def resolve_unknown(
        self,
        requirement: str,
    ) -> None:

        if requirement in self.unknown_requirements:
            self.unknown_requirements.remove(
                requirement
            )

    def set_structured_requirement(
        self,
        field_name: str,
        value: str,
        confidence: str = "medium",
        source: str = "user",
    ) -> None:

        self.structured_requirements[field_name] = {
            "value": value,
            "confidence": confidence,
            "source": source,
        }

        if (
            self.memory_store
            and self.project_id
        ):
            self.memory_store.save_requirement(
                project_id=self.project_id,
                field_name=field_name,
                value=value,
                confidence=confidence,
                source=source,
                resolved=True,
            )

    def set_decision(
        self,
        name: str,
        value: str,
        source: str = "user",
        reason: str = "",
    ) -> None:

        self.decisions[name] = {
            "value": value,
            "source": source,
            "reason": reason,
        }

        if (
            self.memory_store
            and self.project_id
        ):
            self.memory_store.save_decision(
                project_id=self.project_id,
                decision_area=name,
                selected_value=value,
                source=source,
                reason=reason,
            )

    def snapshot(self) -> dict:
        """
        Return the complete current agent state.
        """

        return {
            "goal": self.goal,
            "conversation": list(
                self.conversation
            ),
            "known_requirements": list(
                self.known_requirements
            ),
            "unknown_requirements": list(
                self.unknown_requirements
            ),
            "structured_requirements": dict(
                self.structured_requirements
            ),
            "decisions": dict(
                self.decisions
            ),
            "metadata": dict(
                self.metadata
            ),
            "pending_question": self.pending_question,
            "pending_decision": self.pending_decision,
            "project_id": self.project_id,
            "conversation_id": self.conversation_id,
        }

    def attach_storage(
        self,
        memory_store: MemoryStore | None = None,
        project_id: int | None = None,
        conversation_id: int | None = None,
    ) -> None:
        """
        Attach SQLite persistence to this context.
        """

        self.memory_store = (
            memory_store or MemoryStore()
        )

        self.project_id = project_id
        self.conversation_id = conversation_id

    def save(self) -> None:
        """
        Save the complete current project state to SQLite.
        """

        if not self.memory_store:
            return

        if not self.project_id:
            return

        state_json = json.dumps(
            self.snapshot(),
            indent=2,
        )

        self.memory_store.save_project_state(
            project_id=self.project_id,
            goal=self.goal,
            state_json=state_json,
        )

    @classmethod
    def load_project(
        cls,
        project_id: int,
        memory_store: MemoryStore | None = None,
    ) -> "AgentContext":
        """
        Restore an AgentContext from a saved SQLite project.
        """

        store = (
            memory_store or MemoryStore()
        )

        project = store.get_project(
            project_id
        )

        if project is None:
            raise ValueError(
                f"Project {project_id} was not found."
            )

        context = cls()

        context.memory_store = store
        context.project_id = project_id

        state_json = (
            project.get("state_json")
            or "{}"
        )

        try:
            state = json.loads(
                state_json
            )
        except json.JSONDecodeError:
            state = {}

        context.goal = (
            state.get("goal")
            or project.get("goal")
            or ""
        )

        context.conversation = list(
            state.get(
                "conversation",
                [],
            )
        )

        context.known_requirements = list(
            state.get(
                "known_requirements",
                [],
            )
        )

        context.unknown_requirements = list(
            state.get(
                "unknown_requirements",
                [],
            )
        )

        context.structured_requirements = dict(
            state.get(
                "structured_requirements",
                {},
            )
        )

        context.decisions = dict(
            state.get(
                "decisions",
                {},
            )
        )

        context.metadata = dict(
            state.get(
                "metadata",
                {},
            )
        )

        context.pending_question = (
            state.get(
                "pending_question"
            )
        )

        context.pending_decision = (
            state.get(
                "pending_decision"
            )
        )

        context.conversation_id = (
            state.get(
                "conversation_id"
            )
        )

        return context

    @classmethod
    def load_conversation(
        cls,
        conversation_id: int,
        memory_store: MemoryStore | None = None,
    ) -> "AgentContext":
        """
        Restore a conversation from SQLite.

        This restores the chat history. Project state can be loaded
        separately with load_project().
        """

        store = (
            memory_store or MemoryStore()
        )

        conversation = store.get_conversation(
            conversation_id
        )

        if conversation is None:
            raise ValueError(
                f"Conversation {conversation_id} "
                "was not found."
            )

        context = cls()

        context.memory_store = store
        context.conversation_id = (
            conversation_id
        )

        context.conversation = [
            {
                "role": message["role"],
                "content": message["content"],
            }
            for message in conversation.get(
                "messages",
                [],
            )
        ]

        return context