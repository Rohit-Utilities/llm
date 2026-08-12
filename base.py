from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract interface for language model providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: str | None = None,
    ) -> str:
        """Generate a response from the language model."""
        raise NotImplementedError