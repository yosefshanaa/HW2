# PRD Judge Evaluation

## Purpose
The judge evaluates debate technique, not domain expertise.

## Requirements
- Judge listens only during pings and does not send messages back to debaters.
- Evaluation dimensions are argument strength, rebuttal effectiveness, evidence research, rhetorical quality, and compliance.
- Compliance includes stance consistency (Pro argues FOR, Con argues AGAINST) and argument novelty (no repetition).
- Judge receives debate history (last 4 rounds) to detect cross-round repetition.
- Penalties are applied for disrespect, ignored rebuttals, stance contradiction, line/word excess, timeout/crash, repetition, and failure to advance.
- Auto-repetition detection: bigram Jaccard overlap > 55% with any prior argument triggers REPETITION penalty (-10) when LLM judge misses it. Debater-level detection uses 50% threshold.
- Judge JSON parsing extracts JSON by finding first `{` and last `}` to handle LLM adding extra text.
- Ties are valid outcomes.

## Interface
- `JudgeAgent.observe_round(round_number, pro_argument, con_argument, debate_history=None) -> RoundEvaluation`
- `JudgeAgent.evaluate_debate(transcript) -> dict[str, Score]`
- `JudgeAgent.declare_winner(scores) -> str`

## Penalty Types
| Penalty | Points | Trigger |
|---------|--------|---------|
| disrespect | -5 | Ad hominem, insulting language |
| ignore_rebuttal | -10 | Not addressing opponent's last point |
| stance_contradiction | -15 | Pro arguing against resolution or Con arguing for it |
| exceed_lines | -5 | Over line or word limit |
| exceed_time | -10 | Timeout or crash |
| repetition | -10 | Reusing claims/phrases from prior rounds |

## Acceptance
- Integration tests verify Father non-intervention, Con-first observation, ties, penalty score paths, repetition detection, and stance verification.
