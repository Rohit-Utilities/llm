from collections.abc import Sequence

from llm.config import get_settings
from llm.prompt.models.message import Message


class ConciseBuilder:
    """Build prompts for compacting older conversation history."""

    def __init__(self) -> None:
        settings = get_settings()

        self.max_summary_tokens = (
            settings.conversation_summary_max_tokens
        )

    def build(
        self,
        messages: Sequence[Message],
        existing_summary: str = "",
    ) -> str:
        """
        Build a prompt for compacting older conversation history.

        This class only builds the summarization prompt.

        It does not:
        - call an LLM
        - modify the conversation
        - manage conversation state
        - access long-term memory
        """

        if not messages and not existing_summary.strip():
            return ""

        conversation_text = self._format_messages(
            messages
        )

        return self._build_prompt(
            conversation_text=conversation_text,
            existing_summary=existing_summary,
        )

    @staticmethod
    def _format_messages(
        messages: Sequence[Message],
    ) -> str:
        """Convert Message objects into readable conversation text."""

        formatted: list[str] = []

        for message in messages:
            content = message.content.strip()

            if not content:
                continue

            formatted.append(
                f"{message.role.value.upper()}: {content}"
            )

        return "\n\n".join(formatted)

    def _build_prompt(
        self,
        conversation_text: str,
        existing_summary: str,
    ) -> str:
        """Build the complete summarization prompt."""

        sections: list[str] = [
            """
You are the conversation-memory summarizer for Augustus.

Your job is to create a compact, factual summary of older
conversation history so it can be used as conversation context
in future requests.
""".strip()
        ]

        if existing_summary.strip():
            sections.append(
                f"""
PREVIOUS SUMMARY:
{existing_summary}

Update this summary using the new conversation information.
Do not unnecessarily repeat information that is already
captured.
""".strip()
            )

        if conversation_text:
            sections.append(
                f"""
CONVERSATION TO COMPACT:
{conversation_text}
""".strip()
            )

        sections.append(
            f"""
Create a concise summary containing only information that could
matter for understanding future messages.

Preserve:

- important decisions
- user requirements
- technical architecture
- constraints
- relevant preferences
- unresolved tasks
- important facts established during the conversation
- important corrections or changes
- names of components, models, files, or technologies
- relevant implementation details

Do NOT preserve:

- greetings
- conversational filler
- repeated explanations
- unnecessary wording
- temporary debugging output
- irrelevant details

Do not invent information.

The summary must be no longer than
{self.max_summary_tokens} tokens.

Return ONLY the summary.
""".strip()
        )

        return "\n\n".join(sections)