from debate_simulator.agents.base_agent import BaseAgent
from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.shared.constants import AgentRole
from debate_simulator.skills.base_skill import SkillResult


class HelperAgent(BaseAgent):
    """Concrete agent for Template Method testing."""

    def _build_prompt(self, context: TurnContext) -> str:
        return context.topic

    def _execute_skills(self, context: TurnContext) -> dict[str, SkillResult]:
        return {"skill": SkillResult.ok({"value": context.round_number})}

    def _call_llm(self, prompt: str) -> str:
        return f"{prompt}\nanswer"

    def _validate_response(self, response: str) -> AgentResponse:
        return AgentResponse.from_text(response, time_seconds=0.1)


def test_base_agent_run_turn_uses_template_method() -> None:
    """BaseAgent.run_turn executes hooks and stores memory."""
    agent = HelperAgent(name="tester", role=AgentRole.PRO, llm_client=None)

    response = agent.run_turn(TurnContext(topic="AI", round_number=1))

    assert response.text == "AI\nanswer" and len(agent.memory) == 1
