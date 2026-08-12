from llm.prompt.models.conversation import Conversation
from llm.prompt.models.message import Message


class PromptBuilder:
    """Build prompts for Augustus language-model requests."""

    DEFAULT_SYSTEM_PROMPT = (
        "You are Augustus, an intelligent AI assistant. "
        "Answer clearly, accurately, and concisely. "
        "Do not expose internal reasoning or hidden chain-of-thought."
    )

    def __init__(
        self,
        system_prompt: str | None = None,
    ) -> None:
        self.system_prompt = (
            system_prompt
            or self.DEFAULT_SYSTEM_PROMPT
        )

    def build(
        self,
        conversation: Conversation,
    ) -> str:
        """
        Build the final prompt for an LLM request.

        The conversation contains:
        - the compacted summary of older history
        - the retained recent messages
        - the current user message

        This class only builds the prompt.
        It does not call an LLM provider.
        """

        sections: list[str] = [
            self.system_prompt,
        ]

        if conversation.summary.strip():
            sections.append(
                self._format_summary(
                    conversation.summary
                )
            )

        recent_messages = self._format_messages(
            conversation.messages
        )

        if recent_messages:
            sections.append(
                recent_messages
            )

        return "\n\n".join(sections)

    @staticmethod
    def _format_summary(
        summary: str,
    ) -> str:
        """Format the compacted conversation summary."""

        return (
            "CONVERSATION SUMMARY:\n"
            f"{summary.strip()}"
        )

    @staticmethod
    def _format_messages(
        messages: list[Message],
    ) -> str:
        """Format the retained conversation messages."""

        formatted: list[str] = []

        for message in messages:
            content = message.content.strip()

            if not content:
                continue

            formatted.append(
                f"{message.role.value.upper()}:\n"
                f"{content}"
            )

        if not formatted:
            return ""

        return (
            "RECENT CONVERSATION:\n"
            + "\n\n".join(formatted)
        )