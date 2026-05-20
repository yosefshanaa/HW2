from typing import Any


class LlmClient:
    """OpenAI SDK wrapper that routes calls through the API gatekeeper."""

    def __init__(
        self,
        openai_client: Any,
        gatekeeper: Any,
        model: str,
        temperature: float,
        max_tokens: int | None = None,
    ) -> None:
        """Create an LLM client."""
        self.openai_client = openai_client
        self.gatekeeper = gatekeeper
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def complete(self, prompt: str) -> str:
        """Generate text using OpenAI through the gatekeeper."""
        return self.gatekeeper.execute("openai", self._complete, prompt)

    def _complete(self, prompt: str) -> str:
        if hasattr(self.openai_client, "chat"):
            text = self._complete_chat(prompt)
        else:
            text = self._complete_responses(prompt)
        if not text:
            raise ValueError("empty llm response")
        return str(text)

    def _complete_chat(self, prompt: str) -> str:
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        choices = getattr(response, "choices", [])
        if not choices:
            return ""
        message = getattr(choices[0], "message", None)
        return str(getattr(message, "content", "") or "")

    def _complete_responses(self, prompt: str) -> str:
        response = self.openai_client.responses.create(
            model=self.model,
            input=prompt,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )
        return str(getattr(response, "output_text", "") or "")


__all__ = ["LlmClient"]
