from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from debate_simulator.hooks import HookRegistry
from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import DebateResult, Penalty, Round
from debate_simulator.shared.constants import FallbackText, PenaltyPoints, PenaltyType


class DebateEngine:
    """Domain service that orchestrates research, pings, scoring, and export."""

    def __init__(
        self,
        pro_agent: Any | None = None,
        con_agent: Any | None = None,
        judge_agent: Any | None = None,
        results_path: str | Path = "results",
        hooks: HookRegistry | None = None,
    ) -> None:
        """Create a debate engine with optional injected agents."""
        self.pro_agent = pro_agent
        self.con_agent = con_agent
        self.judge_agent = judge_agent
        self.results_path = Path(results_path)
        self.hooks = hooks or HookRegistry()
        self.rounds: list[Round] = []

    def initialize_agents(self) -> None:
        """Validate that required agents are available."""
        if not all([self.pro_agent, self.con_agent, self.judge_agent]):
            raise RuntimeError("agents are not configured")

    def run_research_phase(self, topic: str) -> None:
        """Run research for debaters when supported."""
        for agent in [self.con_agent, self.pro_agent]:
            research = getattr(agent, "research", None)
            if research:
                research(topic)

    def run_debate_pings(self, topic: str, pings: int) -> list[Round]:
        """Run debate pings in Con to Pro to Judge order."""
        self.rounds = []
        for round_number in range(1, pings + 1):
            self.hooks.emit("on_round_start", ping_num=round_number, topic=topic)
            con_response = self._safe_turn(
                self.con_agent,
                TurnContext(topic=topic, round_number=round_number),
                "con",
            )
            pro_response = self._safe_turn(
                self.pro_agent,
                TurnContext(
                    topic=topic,
                    round_number=round_number,
                    opponent_last_argument=con_response.text,
                ),
                "pro",
            )
            evaluation = self.judge_agent.observe_round(round_number, pro_response.text, con_response.text)
            round_model = Round(
                round_number=round_number,
                con_argument=con_response.text,
                pro_argument=pro_response.text,
                judge_notes=evaluation,
                penalties=[*con_response.penalties, *pro_response.penalties],
            )
            self.rounds.append(round_model)
            self.hooks.emit("on_round_end", ping_num=round_number, notes=evaluation)
        return self.rounds

    def run_final_scoring(self) -> tuple[dict[str, Any], str]:
        """Run final judge scoring."""
        scores = self.judge_agent.evaluate_debate([round_model.model_dump_json() for round_model in self.rounds])
        return scores, self.judge_agent.declare_winner(scores)

    def export_results(self, result: DebateResult) -> Path:
        """Export a debate result to JSON."""
        self.results_path.mkdir(parents=True, exist_ok=True)
        path = self.results_path / f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{result.debate_id}.json"
        path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        return path

    def start_debate(self, topic: str, config: dict[str, Any] | None = None) -> DebateResult:
        """Run a complete debate and export the result."""
        self.initialize_agents()
        debate_config = config or {}
        pings = int(debate_config.get("pings", 10))
        self.hooks.emit("on_debate_start", topic=topic)
        self.run_research_phase(topic)
        rounds = self.run_debate_pings(topic, pings)
        scores, winner = self.run_final_scoring()
        result = DebateResult(topic=topic, rounds=rounds, final_scores=scores, winner=winner, config=debate_config)
        self.export_results(result)
        self.hooks.emit("on_debate_end", results=result)
        return result

    def _safe_turn(self, agent: Any, context: TurnContext, agent_name: str) -> AgentResponse:
        try:
            return agent.run_turn(context)
        except Exception as error:
            penalty = Penalty(
                type=PenaltyType.EXCEED_TIME,
                points=PenaltyPoints.EXCEED_TIME.value,
                reason=str(error),
                agent=agent_name,
            )
            self.hooks.emit("on_penalty", agent=agent_name, penalty=penalty)
            return AgentResponse.from_text(FallbackText.AGENT_CRASH.value, 0.0, [penalty])


__all__ = ["DebateEngine"]
