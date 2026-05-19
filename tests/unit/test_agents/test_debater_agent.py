from debate_simulator.agents.debater_agent import ConDebaterAgent, ProDebaterAgent
from debate_simulator.models.agent import TurnContext
from debate_simulator.shared.constants import Stance


class FakeLlm:
    """LLM test double."""

    def complete(self, prompt: str) -> str:
        """Return deterministic argument text."""
        return "argument"


def test_debater_stances_are_fixed() -> None:
    """Concrete debaters expose fixed pro and con stances."""
    pro = ProDebaterAgent(name="pro", llm_client=FakeLlm())
    con = ConDebaterAgent(name="con", llm_client=FakeLlm())

    assert pro.stance == Stance.PRO and con.stance == Stance.CON


def test_debater_run_turn_generates_response() -> None:
    """Debater uses the base template method to generate a response."""
    debater = ConDebaterAgent(name="con", llm_client=FakeLlm())

    response = debater.run_turn(TurnContext(topic="AI", stance=Stance.CON, round_number=1))

    assert response.text == "argument"
