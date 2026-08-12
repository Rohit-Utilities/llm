from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Supported conversation message roles."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """Represents a single message in a conversation."""

    id: UUID = Field(
        default_factory=uuid4,
    )

    role: MessageRole

    content: str

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )