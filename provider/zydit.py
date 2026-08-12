import time

from openai import OpenAI

from llm.base import LLMProvider
from llm.config import get_settings


class ZyditClient(LLMProvider):
    """Zydit implementation of the LLM provider."""

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.zydit_api_key:
            raise ValueError(
                "ZYDIT_API_KEY is not configured."
            )

        if not settings.zydit_base_url:
            raise ValueError(
                "ZYDIT_BASE_URL is not configured."
            )

        if not settings.zydit_model:
            raise ValueError(
                "ZYDIT_MODEL is not configured."
            )

        self.max_output_tokens = (
            settings.max_output_tokens
        )

        self.request_timeout = (
            settings.request_timeout
        )

        self.client = OpenAI(
            api_key=settings.zydit_api_key,
            base_url=settings.zydit_base_url,
            timeout=self.request_timeout,
        )

        self.default_model = settings.zydit_model

    def generate(
        self,
        prompt: str,
        model: str | None = None,
    ) -> str:
        """
        Send a completed prompt to Zydit and return the
        generated assistant response.

        The provider does not:
        - manage conversations
        - build prompts
        - summarize history
        - perform retrieval
        - manage memory
        """

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        selected_model = (
            model or self.default_model
        )

        print(
            f"[Zydit] Sending request "
            f"model={selected_model}"
        )

        start_time = time.perf_counter()

        try:
            response = (
                self.client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    max_tokens=self.max_output_tokens,
                )
            )

        except Exception as exc:
            elapsed_time = (
                time.perf_counter()
                - start_time
            )

            print(
                f"[Zydit ERROR] "
                f"type={type(exc).__name__} "
                f"latency={elapsed_time:.3f}s"
            )

            print(
                f"[Zydit ERROR] message={exc}"
            )

            if hasattr(exc, "status_code"):
                print(
                    f"[Zydit ERROR] "
                    f"status_code={exc.status_code}"
                )

            if hasattr(exc, "body"):
                print(
                    f"[Zydit ERROR] "
                    f"body={exc.body}"
                )

            raise

        elapsed_time = (
            time.perf_counter()
            - start_time
        )

        if not response.choices:
            raise RuntimeError(
                "Zydit returned no choices."
            )

        choice = response.choices[0]
        message = choice.message

        print(
            f"[Zydit] model={selected_model} "
            f"latency={elapsed_time:.3f}s "
            f"finish_reason={choice.finish_reason}"
        )

        if response.usage:
            print(
                f"[Zydit] "
                f"prompt_tokens="
                f"{response.usage.prompt_tokens} "
                f"completion_tokens="
                f"{response.usage.completion_tokens} "
                f"total_tokens="
                f"{response.usage.total_tokens}"
            )

        if message.content:
            return message.content.strip()

        raise RuntimeError(
            "Zydit returned no final response content."
        )