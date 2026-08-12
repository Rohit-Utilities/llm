from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from llm.prompt.models.message import Message


class Conversation(BaseModel):
    """Represents the state of a conversation."""

    id: UUID = Field(
        default_factory=uuid4,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    summary: str = ""

    messages: list[Message] = Field(
        default_factory=list,
    )