from app.brain.context import AgentContext
from app.brain.context_manager import ContextManager
from app.brain.agent_analysis import AgentAnalysisEngine
from app.brain.decision import DecisionEngine
from app.brain.memory import MemoryStore
from app.brain.local_router import LocalRouter


class ConversationManager:

    def __init__(
        self,
        context: AgentContext | None = None,
        memory_store: MemoryStore | None = None,
        context_manager: ContextManager | None = None,
        analysis: AgentAnalysisEngine | None = None,
        decisions: DecisionEngine | None = None,
        local_router: LocalRouter | None = None,
        llm=None,
        project_id: int | None = None,
        project_name: str = "SpongeBob Project",
        conversation_id: int | None = None,
    ):
        self.memory_store = (
            memory_store
            or MemoryStore()
        )

        self.context_manager = (
            context_manager
            or ContextManager()
        )

        self.llm = llm

        self.analysis = (
            analysis
            or AgentAnalysisEngine(
                llm=self.llm
            )
        )

        self.decisions = (
            decisions
            or DecisionEngine(
                llm=self.llm
            )
        )

        self.local_router = (
            local_router
            or LocalRouter()
        )

        # ---------------------------------------------------------
        # USE EXISTING CONTEXT
        # ---------------------------------------------------------

        if context is not None:
            self.context = context

            if self.context.memory_store is None:
                self.context.attach_storage(
                    memory_store=self.memory_store,
                    project_id=project_id,
                    conversation_id=conversation_id,
                )

        # ---------------------------------------------------------
        # LOAD EXISTING PROJECT
        # ---------------------------------------------------------

        elif project_id is not None:
            self.context = (
                AgentContext.load_project(
                    project_id=project_id,
                    memory_store=self.memory_store,
                )
            )

            if conversation_id is not None:
                self.context.conversation_id = (
                    conversation_id
                )

        # ---------------------------------------------------------
        # LOAD EXISTING CONVERSATION
        # ---------------------------------------------------------

        elif conversation_id is not None:
            self.context = (
                AgentContext.load_conversation(
                    conversation_id=conversation_id,
                    memory_store=self.memory_store,
                )
            )

        # ---------------------------------------------------------
        # CREATE NEW PROJECT SESSION
        # ---------------------------------------------------------

        else:
            new_project_id = (
                self.memory_store.create_project(
                    name=project_name,
                    goal="",
                    state_json="{}",
                )
            )

            new_conversation_id = (
                self.memory_store.create_conversation(
                    title=project_name,
                )
            )

            self.context = AgentContext()

            self.context.attach_storage(
                memory_store=self.memory_store,
                project_id=new_project_id,
                conversation_id=new_conversation_id,
            )

    # ============================================================
    # MANAGED MODEL CONTEXT
    # ============================================================

    def _build_model_context(self) -> dict:
        project_state = {
            "goal": self.context.goal,
            "known_requirements": (
                self.context.known_requirements
            ),
            "unknown_requirements": (
                self.context.unknown_requirements
            ),
            "structured_requirements": (
                self.context.structured_requirements
            ),
            "decisions": (
                self.context.decisions
            ),
            "metadata": (
                self.context.metadata
            ),
            "pending_question": (
                self.context.pending_question
            ),
            "pending_decision": (
                self.context.pending_decision
            ),
            "project_id": (
                self.context.project_id
            ),
        }

        return self.context_manager.build_context(
            conversation=self.context.conversation,
            project_state=project_state,
        )

    # ============================================================
    # MAIN MESSAGE PROCESSING
    # ============================================================

    def process_user_message(
        self,
        user_message: str,
    ) -> dict:

        self.context.add_message(
            "user",
            user_message,
        )

        # ---------------------------------------------------------
        # 1. HANDLE SIMPLE LOCAL REQUESTS
        # ---------------------------------------------------------

        local_result = (
            self.local_router.classify(
                user_message
            )
        )

        if local_result.get("handled"):

            response = {
                "type": local_result.get(
                    "type",
                    "local",
                ),
                "message": local_result.get(
                    "response",
                    "",
                ),
                "next_step": {
                    "action": "answer"
                },
                "context": (
                    self.context.snapshot()
                ),
            }

            self.context.save()

            return response

        # ---------------------------------------------------------
        # 2. HANDLE PENDING TECHNICAL DECISION
        # ---------------------------------------------------------

        if self.context.pending_decision:

            choice = (
                self.decisions.extract_choice(
                    self.context.pending_decision,
                    user_message,
                )
            )

            if choice.get("confirmed"):

                selected_option = (
                    choice.get(
                        "selected_option"
                    )
                )

                decision_area = (
                    self.context.pending_decision.get(
                        "decision_area",
                        "",
                    )
                )

                if (
                    selected_option
                    and decision_area
                ):

                    self.context.set_decision(
                        name=decision_area,
                        value=selected_option,
                        source="user",
                        reason=choice.get(
                            "reason",
                            "",
                        ),
                    )

                    self.context.resolve_unknown(
                        decision_area
                    )

                    self.context.metadata[
                        "last_decision"
                    ] = {
                        "decision_area": decision_area,
                        "selected_option": (
                            selected_option
                        ),
                        "source": "user",
                    }

                    self.context.pending_decision = None

                    self.context.save()

                    return {
                        "type": (
                            "decision_confirmed"
                        ),
                        "message": (
                            f"Confirmed: "
                            f"{decision_area} = "
                            f"{selected_option}"
                        ),
                        "next_step": {
                            "action": "continue"
                        },
                        "context": (
                            self.context.snapshot()
                        ),
                    }

            if choice.get(
                "needs_clarification"
            ):

                return {
                    "type": (
                        "decision_clarification"
                    ),
                    "message": (
                        "I want to make sure I use "
                        "the option you intended."
                    ),
                    "options": (
                        self.context.pending_decision.get(
                            "options",
                            [],
                        )
                    ),
                    "next_step": {
                        "action": (
                            "decision_clarification"
                        ),
                    },
                    "context": (
                        self.context.snapshot()
                    ),
                }

        # ---------------------------------------------------------
        # 3. HANDLE PENDING QUESTION
        # ---------------------------------------------------------

        # The answer is deliberately handled by the SAME
        # consolidated analysis call below instead of making
        # another separate RequirementsManager LLM call.

        # ---------------------------------------------------------
        # 4. BUILD COMPACT CONTEXT
        # ---------------------------------------------------------

        model_context = (
            self._build_model_context()
        )

        # ---------------------------------------------------------
        # 5. ONE CONSOLIDATED ANALYSIS CALL
        # ---------------------------------------------------------

        analysis = (
            self.analysis.analyze(
                user_message=user_message,
                context=model_context,
            )
        )

        # ---------------------------------------------------------
        # 6. APPLY UNDERSTANDING
        # ---------------------------------------------------------

        understanding = (
            analysis.get(
                "understanding",
                {},
            )
        )

        goal = understanding.get(
            "goal"
        )

        if goal:
            self.context.goal = goal

        task_type = understanding.get(
            "task_type"
        )

        if task_type:
            self.context.metadata[
                "task_type"
            ] = task_type

        summary = understanding.get(
            "summary"
        )

        if summary:
            self.context.metadata[
                "last_analysis_summary"
            ] = summary

        # ---------------------------------------------------------
        # 7. APPLY REQUIREMENTS
        # ---------------------------------------------------------

        requirements = (
            analysis.get(
                "requirements",
                {},
            )
        )

        confirmed = requirements.get(
            "confirmed",
            [],
        )

        for requirement in confirmed:
            self.context.add_requirement(
                requirement
            )

        new_unknowns = requirements.get(
            "new_unknowns",
            [],
        )

        for unknown in new_unknowns:
            self.context.add_unknown(
                unknown
            )

        # A requirement explicitly confirmed by the model
        # should no longer remain unresolved if the same
        # field/value is present in structured state.
        for field_name in (
            self.context.structured_requirements
        ):
            self.context.resolve_unknown(
                field_name
            )

        # ---------------------------------------------------------
        # 8. APPLY READINESS
        # ---------------------------------------------------------

        readiness = (
            analysis.get(
                "readiness",
                {},
            )
        )

        readiness_level = (
            readiness.get(
                "level",
                "NOT_READY",
            )
        )

        self.context.metadata[
            "readiness"
        ] = {
            "level": readiness_level,
            "reason": readiness.get(
                "reason",
                "",
            ),
        }

        # ---------------------------------------------------------
        # 9. APPLY NEXT ACTION
        # ---------------------------------------------------------

        next_action = (
            analysis.get(
                "next_action",
                {},
            )
        )

        action_type = next_action.get(
            "type",
            "answer",
        )

        # ---------------------------------------------------------
        # 10. CLARIFICATION
        # ---------------------------------------------------------

        if action_type == "clarify":

            question = next_action.get(
                "question",
                "",
            )

            reason = next_action.get(
                "reason",
                "",
            )

            self.context.pending_question = {
                "question": question,
                "reason": reason,
            }

            self.context.save()

            return {
                "type": "clarification",
                "understanding": understanding,
                "requirements": requirements,
                "readiness": readiness,
                "next_step": next_action,
                "context": (
                    self.context.snapshot()
                ),
            }

        # ---------------------------------------------------------
        # 11. ARCHITECTURAL RECOMMENDATION
        # ---------------------------------------------------------

        if action_type == "recommend":

            decision_area = (
                next_action.get(
                    "decision_area"
                )
                or "architecture"
            )

            recommendation = (
                self.decisions.recommend(
                    decision_area,
                    model_context,
                )
            )

            recommendation[
                "decision_area"
            ] = decision_area

            self.context.pending_decision = (
                recommendation
            )

            self.context.pending_question = None

            self.context.save()

            return {
                "type": (
                    "decision_recommendation"
                ),
                "understanding": understanding,
                "requirements": requirements,
                "readiness": readiness,
                "next_step": next_action,
                "recommendation": (
                    recommendation
                ),
                "context": (
                    self.context.snapshot()
                ),
            }

        # ---------------------------------------------------------
        # 12. PROCEED
        # ---------------------------------------------------------

        if action_type == "proceed":

            self.context.pending_question = None

            self.context.save()

            return {
                "type": "proceed",
                "understanding": understanding,
                "requirements": requirements,
                "readiness": readiness,
                "next_step": next_action,
                "context": (
                    self.context.snapshot()
                ),
            }

        # ---------------------------------------------------------
        # 13. DEFAULT ANSWER
        # ---------------------------------------------------------

        self.context.save()

        return {
            "type": "answer",
            "understanding": understanding,
            "requirements": requirements,
            "readiness": readiness,
            "next_step": next_action,
            "context": (
                self.context.snapshot()
            ),
        }

    # ============================================================
    # ASSISTANT RESPONSE STORAGE
    # ============================================================

    def record_assistant_response(
        self,
        response: str,
    ) -> None:

        self.context.add_message(
            "assistant",
            response,
        )

        self.context.save()

    # ============================================================
    # IDENTIFIERS
    # ============================================================

    def project_id(self) -> int | None:
        return self.context.project_id

    def conversation_id(self) -> int | None:
        return self.context.conversation_id

    # ============================================================
    # DEBUG / CONTEXT
    # ============================================================

    def get_managed_context(self) -> dict:
        return self._build_model_context()