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
        prompt_price_per_million: float = 0.0,
        completion_price_per_million: float = 0.0,
    ) -> None:
        """Create an LLM client."""
        self.openai_client = openai_client
        self.gatekeeper = gatekeeper
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.prompt_price_per_million = prompt_price_per_million
        self.completion_price_per_million = completion_price_per_million
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

    def complete(self, prompt: str) -> str:
        """Generate text using OpenAI through the gatekeeper."""
        return self.gatekeeper.execute("openai", self._complete, prompt)

    def _record_usage(self, response: Any) -> None:
        """Accumulate prompt/completion tokens from an OpenAI response, if present."""
        usage = getattr(response, "usage", None)
        if usage is None:
            return
        prompt_tokens = getattr(usage, "prompt_tokens", 0) or getattr(usage, "input_tokens", 0)
        completion = getattr(usage, "completion_tokens", 0) or getattr(usage, "output_tokens", 0)
        self.total_prompt_tokens += int(prompt_tokens or 0)
        self.total_completion_tokens += int(completion or 0)

    def usage_summary(self) -> dict[str, float]:
        """Return accumulated token totals and the cost derived from config pricing."""
        cost = (
            self.total_prompt_tokens / 1_000_000 * self.prompt_price_per_million
            + self.total_completion_tokens / 1_000_000 * self.completion_price_per_million
        )
        return {
            "total_prompt_tokens": float(self.total_prompt_tokens),
            "total_completion_tokens": float(self.total_completion_tokens),
            "total_cost_usd": round(cost, 6),
        }

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
        self._record_usage(response)
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
        self._record_usage(response)
        return str(getattr(response, "output_text", "") or "")


__all__ = ["LlmClient"]
