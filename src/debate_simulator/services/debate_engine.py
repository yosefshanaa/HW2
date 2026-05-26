from typing import Any

from debate_simulator.hooks import HookRegistry
from debate_simulator.models.agent import AgentResponse, TurnContext
from debate_simulator.models.debate import DebateResult, Round
from debate_simulator.services.engine_helpers import (
    apply_final_penalties,
    build_result,
    export_result,
    father_relay,
    is_shutdown_requested,
    load_debate_defaults,
    safe_turn,
)
from debate_simulator.shared.process_manager import ProcessManager


class DebateEngine:
    """Domain service that orchestrates research, pings, scoring, and export."""

    def __init__(
        self,
        pro_agent: Any | None = None,
        con_agent: Any | None = None,
        judge_agent: Any | None = None,
        results_path: str = "results",
        hooks: HookRegistry | None = None,
        process_manager: Any | None = None,
    ) -> None:
        """Create a debate engine with optional injected agents."""
        self.pro_agent = pro_agent
        self.con_agent = con_agent
        self.judge_agent = judge_agent
        self.results_path = results_path
        self.hooks = hooks or HookRegistry()
        self.process_manager = process_manager
        self.rounds: list[Round] = []

    def initialize_agents(self) -> None:
        if not all([self.pro_agent, self.con_agent, self.judge_agent]):
            raise RuntimeError("agents are not configured")

    def run_research_phase(self, topic: str) -> None:
        for agent in [self.judge_agent, self.con_agent, self.pro_agent]:
            if getattr(agent, "research", None):
                agent.research(topic)

    def run_debate_pings(
        self, topic: str, pings: int, max_lines: int = 2, max_words: int = 90
    ) -> list[Round]:
        """Run debate pings alternating Pro-first / Con-first to reduce speaker-order bias."""
        self.rounds = []
        debate_history: list[str] = []
        for round_number in range(1, pings + 1):
            if is_shutdown_requested():
                break
            self.hooks.emit("on_round_start", ping_num=round_number, topic=topic)
            metadata = {"max_lines": max_lines, "max_words": max_words, "total_rounds": pings}
            con_ctx = self._con_context(topic, round_number, metadata, debate_history)
            con_response = AgentResponse.from_text("", 0.0)
            if round_number % 2 == 0:
                con_response = safe_turn(self.con_agent, con_ctx, "con", self.hooks, self.process_manager)
                pro_ctx = self._pro_context(
                    topic, round_number, father_relay("Con", con_response.text), metadata, debate_history
                )
                pro_response = safe_turn(self.pro_agent, pro_ctx, "pro", self.hooks, self.process_manager)
            else:
                pro_ctx = self._pro_context(topic, round_number, "", metadata, debate_history)
                pro_response = safe_turn(self.pro_agent, pro_ctx, "pro", self.hooks, self.process_manager)
                con_ctx.opponent_last_argument = father_relay("Pro", pro_response.text)
                con_response = safe_turn(self.con_agent, con_ctx, "con", self.hooks, self.process_manager)
            evaluation = self.judge_agent.observe_round(
                round_number,
                pro_response.text,
                con_response.text,
                debate_history=list(debate_history),
            )
            first, second = ("Pro", "Con") if round_number % 2 != 0 else ("Con", "Pro")
            first_text = pro_response.text if first == "Pro" else con_response.text
            second_text = con_response.text if first == "Pro" else pro_response.text
            f_notes = evaluation.pro_notes if first == "Pro" else evaluation.con_notes
            s_notes = evaluation.con_notes if second == "Con" else evaluation.pro_notes
            debate_history.append(
                f"Round {round_number}:\n{first}: {first_text}\n{second}: {second_text}\n"
                f"Judge->{first}: {f_notes}\nJudge->{second}: {s_notes}"
            )
            self.rounds.append(Round(
                round_number=round_number, con_argument=con_response.text,
                pro_argument=pro_response.text, judge_notes=evaluation,
                penalties=[*con_response.penalties, *pro_response.penalties,
                           *evaluation.con_penalties, *evaluation.pro_penalties],
            ))
            self.hooks.emit("on_round_end", ping_num=round_number, round_model=self.rounds[-1])
        return self.rounds

    def _con_context(self, topic: str, rn: int, metadata: dict, history: list[str]) -> TurnContext:
        ctx = TurnContext(
            topic=topic, round_number=rn, metadata=metadata,
            debate_history=list(history), judge_feedback=self._last_feedback("con"),
        )
        if history:
            ctx.opponent_last_argument = father_relay("Pro", self.rounds[-1].pro_argument)
        return ctx

    def _pro_context(self, topic: str, rn: int, opp: str, metadata: dict, history: list[str]) -> TurnContext:
        return TurnContext(
            topic=topic, round_number=rn, opponent_last_argument=opp,
            metadata=metadata, debate_history=list(history), judge_feedback=self._last_feedback("pro"),
        )

    def _last_feedback(self, agent: str) -> str:
        if not self.rounds:
            return ""
        last_eval = self.rounds[-1].judge_notes
        notes = last_eval.con_notes if agent == "con" else last_eval.pro_notes
        return f"The judge's feedback on your last speech: {notes}" if notes else ""

    def run_final_scoring(self) -> tuple[dict[str, Any], str]:
        scores = self.judge_agent.evaluate_debate([r.model_dump_json() for r in self.rounds])
        apply_final_penalties(self.rounds, scores)
        rc = max(len(self.rounds), 1)
        for s in scores.values():
            s.total = max(s.total + s.penalty_total / rc, 0.0)
        return scores, self.judge_agent.declare_winner(scores)

    def start_debate(self, topic: str, config: dict[str, Any] | None = None) -> DebateResult:
        self.initialize_agents()
        debate_config = config or {}
        defaults = load_debate_defaults()
        if self.process_manager is None:
            self.process_manager = ProcessManager(
                defaults["agent_timeout_seconds"], defaults["keepalive_interval_seconds"]
            )
        pings = int(debate_config.get("pings", defaults["max_pings"]))
        max_lines = int(debate_config.get("max_lines", defaults["max_lines_per_response"]))
        max_words = int(debate_config.get("max_words", defaults["max_words_per_response"]))
        self.hooks.emit("on_debate_start", topic=topic)
        self.run_research_phase(topic)
        rounds = self.run_debate_pings(topic, pings, max_lines=max_lines, max_words=max_words)
        scores, winner = self.run_final_scoring()
        result = build_result(topic, rounds, scores, winner, debate_config)
        export_result(result, self.results_path)
        self.hooks.emit("on_debate_end", results=result)
        return result


__all__ = ["DebateEngine"]
