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
    client = LlmClient(openai_client=FakeOpenAI(), gatekeeper=gatekeeper, model="m", temperature=0.7)

    text = client.complete("prompt")

    assert text == "hello" and gatekeeper.services == ["openai"]
