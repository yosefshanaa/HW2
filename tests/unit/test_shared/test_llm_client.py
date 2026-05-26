from debate_simulator.shared.llm_client import LlmClient


class FakeGatekeeper:
    """Gatekeeper test double."""

    def __init__(self) -> None:
        """Create a call log."""
        self.services: list[str] = []

    def execute(self, service: str, api_call, *args, **kwargs):
        """Execute the call and record the service."""
        self.services.append(service)
        return api_call(*args, **kwargs)


class FakeResponses:
    """OpenAI responses endpoint test double."""

    def create(self, **kwargs):
        """Return an object with output_text."""
        return type("Response", (), {"output_text": "hello"})()


class FakeOpenAI:
    """OpenAI client test double."""

    def __init__(self) -> None:
        """Create a fake responses endpoint."""
        self.responses = FakeResponses()


def test_llm_client_calls_openai_through_gatekeeper() -> None:
    """LLM client delegates external calls through the gatekeeper."""
    gatekeeper = FakeGatekeeper()
    client = LlmClient(
        openai_client=FakeOpenAI(), gatekeeper=gatekeeper, model="m", temperature=0.7
    )

    text = client.complete("prompt")

    assert text == "hello" and gatekeeper.services == ["openai"]


class FakeChatWithUsage:
    """Chat client double that reports token usage."""

    class _Completions:
        def create(self, **kwargs):
            """Return a chat response carrying a usage object."""
            usage = type("Usage", (), {"prompt_tokens": 1000, "completion_tokens": 500})()
            message = type("Msg", (), {"content": "hi"})()
            choice = type("Choice", (), {"message": message})()
            return type("Resp", (), {"choices": [choice], "usage": usage})()

    def __init__(self) -> None:
        """Expose a chat.completions endpoint."""
        self.chat = type("Chat", (), {"completions": FakeChatWithUsage._Completions()})()


def test_llm_client_tracks_tokens_and_cost() -> None:
    """Usage is accumulated and cost is derived from configured per-million pricing."""
    client = LlmClient(
        openai_client=FakeChatWithUsage(), gatekeeper=FakeGatekeeper(), model="m",
        temperature=0.7, prompt_price_per_million=0.15, completion_price_per_million=0.60,
    )

    client.complete("prompt")
    summary = client.usage_summary()

    # 1000/1e6*0.15 + 500/1e6*0.60 = 0.00015 + 0.0003 = 0.00045
    assert summary["total_prompt_tokens"] == 1000.0
    assert summary["total_completion_tokens"] == 500.0
    assert summary["total_cost_usd"] == 0.00045
