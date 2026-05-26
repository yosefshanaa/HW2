from debate_simulator.agents.debater_agent import ConDebaterAgent, ProDebaterAgent
from debate_simulator.models.agent import TurnContext
from debate_simulator.shared.constants import Stance
from debate_simulator.skills.argument_builder.skill import ArgumentBuilderSkill
from debate_simulator.skills.rebuttal_builder.skill import RebuttalBuilderSkill


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


def test_sons_have_distinct_skills() -> None:
    """Each son owns a different distinctive skill so they cannot collapse together."""
    assert ProDebaterAgent.distinctive_skill == "argument_builder"
    assert ConDebaterAgent.distinctive_skill == "rebuttal_builder"
    assert ProDebaterAgent.distinctive_skill != ConDebaterAgent.distinctive_skill


def test_pro_turn_routes_through_argument_builder() -> None:
    """When wired, the Pro turn is generated via its distinctive argument_builder skill."""
    llm = FakeLlm()
    pro = ProDebaterAgent("pro", llm, skills={"argument_builder": ArgumentBuilderSkill(llm)})

    response = pro.run_turn(TurnContext(topic="AI", stance=Stance.PRO, round_number=1))

    assert response.text == "argument"
    assert "argument_builder" in pro.last_skill_results


def test_con_turn_routes_through_rebuttal_builder() -> None:
    """When wired, the Con turn is generated via its distinctive rebuttal_builder skill."""
    llm = FakeLlm()
    con = ConDebaterAgent("con", llm, skills={"rebuttal_builder": RebuttalBuilderSkill(llm)})

    response = con.run_turn(TurnContext(topic="AI", stance=Stance.CON, round_number=1))

    assert response.text == "argument"
    assert "rebuttal_builder" in con.last_skill_results
