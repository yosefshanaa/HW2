# PRD Judge Evaluation

## Purpose
The judge evaluates debate technique, not domain expertise.

## Scoring System
Based on World Schools Debate Championship rules with per-round speaker scoring.

### Per-Round Speaker Scores (50-100 scale)
Each speaker is scored every round on three categories:
- **Content (40%)**: Arguments with claim-warrant-impact chains, evidence quality and credibility, recency of sources, new analysis each round
- **Style (30%)**: Rhetoric, clarity, concise persuasion, rebuttal effectiveness, respectful tone
- **Strategy (30%)**: Engagement with opponent, dropped argument detection, stance consistency, novelty, offense generation

### Final Score
Average of all per-round speaker scores. Range: 50-100.

### Ties
A tie is declared when scores are within 2 points of each other.

## Penalty Handling
Penalties are tracked SEPARATELY from quality scores. They do NOT reduce the 50-100 score.
Penalties include: disrespect, ignore_rebuttal, stance_contradiction, exceed_lines, exceed_time, repetition.

## Repetition Detection
- Auto-detection via bigram Jaccard overlap (>55% threshold) when LLM judge misses it
- Source-reuse tracking: previously cited sources detected and penalized
- Cited sources injected into debater prompt as "DO NOT cite again"

## Interface
- `JudgeAgent.observe_round(round_number, pro_argument, con_argument, debate_history=None) -> RoundEvaluation` (includes per-round speaker scores)
- `JudgeAgent.evaluate_debate(transcript) -> dict[str, Score]` (averages per-round scores)
- `JudgeAgent.declare_winner(scores) -> str`

## Acceptance
- Integration tests verify Father non-intervention, per-round scoring, ties, penalty tracking, and stance verification.
