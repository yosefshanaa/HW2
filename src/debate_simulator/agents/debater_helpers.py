"""Pure-function helpers for debater prompt construction and limit checking."""

from __future__ import annotations

from debate_simulator.models.debate import Penalty
from debate_simulator.shared.constants import AgentRole, PenaltyType


def count_words(text: str) -> int:
    """Count words excluding URL tokens."""
    return sum(1 for w in text.split() if "://" not in w)


def apply_limits(text: str, max_words: int, max_lines: int, role: AgentRole) -> list[Penalty]:
    """Return penalties if *text* exceeds word or line limits."""
    penalties: list[Penalty] = []
    word_count = count_words(text)
    if word_count > max_words:
        penalties.append(
            Penalty(
                type=PenaltyType.EXCEED_LINES,
                points=-5,
                reason=f"response exceeded {max_words} word limit ({word_count} words, URLs excluded)",
                agent=role.value,
            )
        )
    if len(text.splitlines()) > max_lines:
        penalties.append(
            Penalty(
                type=PenaltyType.EXCEED_LINES,
                points=-5,
                reason="response exceeded the line limit",
                agent=role.value,
            )
        )
    return penalties


def build_debater_prompt(
    template: str,
    agent_name: str,
    topic: str,
    round_number: int,
    total_rounds: int,
    stance: str,
    opponent_last_argument: str | None,
    previous_arguments: list[str],
    used_sources: list[str],
    debate_history: list[str],
    research_notes: list[str],
    judge_feedback: str,
    max_lines: int,
    max_words: int,
) -> str:
    """Render the debater system prompt by filling template placeholders."""
    notes_block = "\n".join(research_notes) if research_notes else "No external notes."
    history_block = "\n---\n".join(debate_history) if debate_history else "No prior rounds."
    prev_block = (
        "\n".join(f"- {a}" for a in previous_arguments) if previous_arguments else "None yet."
    )
    src_block = "\n".join(f"- {s}" for s in used_sources) if used_sources else "None yet."
    feedback_block = ""
    if judge_feedback:
        feedback_block = (
            f"Judge feedback on your previous round:\n{judge_feedback}\n"
            "Improve based on this feedback. Do not repeat the same weaknesses."
        )
    return (
        template.replace("{agent_name}", agent_name)
        .replace("{topic}", topic)
        .replace("{round_number}", str(round_number))
        .replace("{total_rounds}", str(total_rounds))
        .replace("{stance}", stance)
        .replace(
            "{opponent_last_argument}",
            opponent_last_argument or "No previous argument. Open with your strongest case.",
        )
        .replace("{your_previous_arguments}", prev_block)
        .replace("{used_sources}", src_block)
        .replace("{debate_history}", history_block)
        .replace("{research_notes}", notes_block)
        .replace("{judge_feedback_block}", feedback_block)
        .replace("{max_lines}", str(max_lines))
        .replace("{max_words}", str(max_words))
    )


__all__ = ["apply_limits", "build_debater_prompt", "count_words"]
