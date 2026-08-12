from uuid import UUID

from llm.config import get_settings
from llm.base import LLMProvider
from llm.provider.zydit import ZyditClient
from llm.manager.conversation_manager import ConversationManager
from llm.prompt.concise import ConciseBuilder
from llm.prompt.guard import ConversationGuard
from llm.prompt.models.conversation import Conversation
from llm.prompt.models.message import MessageRole
from llm.prompt.prompt_builder import PromptBuilder


class LLMService:
    """Application service for language-model operations."""

    def __init__(
        self,
        conversation_manager: ConversationManager | None = None,
        conversation_guard: ConversationGuard | None = None,
        concise_builder: ConciseBuilder | None = None,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        settings = get_settings()

        provider_factories = {
            "zydit": ZyditClient,
        }

        provider_name = settings.llm_provider.lower()

        provider_factory = provider_factories.get(
            provider_name
        )

        if provider_factory is None:
            raise ValueError(
                f"Unsupported LLM provider: "
                f"{settings.llm_provider}"
            )

        self.provider: LLMProvider = (
            provider_factory()
        )

        self.conversation_manager = (
            conversation_manager
            or ConversationManager()
        )

        self.conversation_guard = (
            conversation_guard
            or ConversationGuard(
                max_recent_messages=(
                    settings.conversation_recent_messages
                )
            )
        )

        self.concise_builder = (
            concise_builder
            or ConciseBuilder()
        )

        self.prompt_builder = (
            prompt_builder
            or PromptBuilder()
        )

    def create_conversation(self) -> UUID:
        """Create a new conversation and return its ID."""

        conversation = (
            self.conversation_manager.create()
        )

        return conversation.id

    def generate(
        self,
        conversation_id: UUID,
        prompt: str,
    ) -> str:
        """
        Generate an assistant response for a conversation.

        Flow:

        1. Add the user message.
        2. Build the response prompt.
        3. Generate the assistant response.
        4. Add the assistant response.
        5. Compact older history if required.
        """

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        conversation = (
            self.conversation_manager.get(
                conversation_id
            )
        )

        self.conversation_manager.add_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=prompt,
        )

        response_prompt = (
            self.prompt_builder.build(
                conversation=conversation
            )
        )

        response = self.provider.generate(
            response_prompt
        )

        self.conversation_manager.add_message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=response,
        )

        self._compact_conversation(
            conversation
        )

        return response

    def _compact_conversation(
        self,
        conversation: Conversation,
    ) -> None:
        """
        Compact older conversation messages when the
        configured recent-message limit is exceeded.
        """

        if not self.conversation_guard.needs_compaction(
            conversation
        ):
            return

        messages_to_compact = (
            self.conversation_guard.get_messages_to_compact(
                conversation
            )
        )

        if not messages_to_compact:
            return

        summary_prompt = (
            self.concise_builder.build(
                messages=messages_to_compact,
                existing_summary=conversation.summary,
            )
        )

        if not summary_prompt:
            return

        summary = self.provider.generate(
            summary_prompt
        )

        if not summary.strip():
            raise RuntimeError(
                "LLM returned an empty conversation summary."
            )

        self.conversation_manager.update_summary(
            conversation_id=conversation.id,
            summary=summary,
        )

        self.conversation_guard.apply_summary(
            conversation=conversation,
            summary=summary,
        )