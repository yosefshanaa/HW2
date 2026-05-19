# PRD Judge Evaluation

## Purpose
The judge evaluates debate technique, not domain expertise.

## Requirements
- Judge listens only during pings and does not send messages back to debaters.
- Evaluation dimensions are argument strength, rebuttal effectiveness, evidence research, rhetorical quality, and compliance.
- Penalties are applied for disrespect, ignored rebuttals, stance contradiction, line excess, and timeout/crash fallback.
- Ties are valid outcomes.

## Interface
- `JudgeAgent.observe_round(...) -> RoundEvaluation`
- `JudgeAgent.evaluate_debate(transcript) -> dict[str, Score]`
- `JudgeAgent.declare_winner(scores) -> str`

## Acceptance
- Integration tests verify Father non-intervention, Con-first observation, ties, and penalty score paths.
