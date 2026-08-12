from datetime import datetime, timezone
from uuid import UUID

from llm.prompt.models.conversation import Conversation
from llm.prompt.models.message import Message, MessageRole


class ConversationManager:
    """
    Manages the lifecycle and state of conversations.

    Responsible for:
    - creating conversations
    - retrieving conversations
    - adding messages
    - updating summaries
    - checking conversation existence
    - deleting conversations

    This class does not:
    - call an LLM
    - build prompts
    - summarize messages
    - perform retrieval
    - access Qdrant
    - enforce conversation limits
    """

    def __init__(self) -> None:
        self._conversations: dict[
            UUID,
            Conversation,
        ] = {}

    def create(self) -> Conversation:
        """Create and register a new conversation."""

        conversation = Conversation()

        self._conversations[
            conversation.id
        ] = conversation

        return conversation

    def get(
        self,
        conversation_id: UUID,
    ) -> Conversation:
        """
        Retrieve an existing conversation.

        Raises:
            ValueError:
                If the conversation does not exist.
        """

        conversation = self._conversations.get(
            conversation_id
        )

        if conversation is None:
            raise ValueError(
                f"Conversation not found: "
                f"{conversation_id}"
            )

        return conversation

    def exists(
        self,
        conversation_id: UUID,
    ) -> bool:
        """Return whether a conversation exists."""

        return conversation_id in self._conversations

    def add_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
    ) -> Message:
        """
        Add a message to an existing conversation.
        """

        if not content.strip():
            raise ValueError(
                "Message content cannot be empty."
            )

        conversation = self.get(
            conversation_id
        )

        message = Message(
            role=role,
            content=content,
        )

        conversation.messages.append(
            message
        )

        conversation.updated_at = (
            datetime.now(timezone.utc)
        )

        return message

    def update_summary(
        self,
        conversation_id: UUID,
        summary: str,
    ) -> None:
        """
        Update the compacted summary of a conversation.

        The summary is generated outside the manager.
        The manager only stores it.
        """

        if not summary.strip():
            raise ValueError(
                "Conversation summary cannot be empty."
            )

        conversation = self.get(
            conversation_id
        )

        conversation.summary = summary.strip()

        conversation.updated_at = (
            datetime.now(timezone.utc)
        )

    def get_messages(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        """Return all currently retained messages."""

        conversation = self.get(
            conversation_id
        )

        return conversation.messages

    def delete(
        self,
        conversation_id: UUID,
    ) -> None:
        """Delete an existing conversation."""

        if conversation_id not in self._conversations:
            raise ValueError(
                f"Conversation not found: "
                f"{conversation_id}"
            )

        del self._conversations[
            conversation_id
        ]

    def clear(self) -> None:
        """Delete all in-memory conversations."""

        self._conversations.clear()