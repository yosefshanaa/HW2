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
1. Average all per-round speaker scores per side (range 50-100) → quality total.
2. Sum that side's penalty points across all rounds, then divide by the round count
   (`penalty_total / rounds`) so penalties live on the same per-round scale as quality.
3. `final_total = max(quality_total + averaged_penalty, 0)`.

This averaging is deliberate: quality is averaged across rounds, so penalties must be too.
Summing raw penalties (as a prior version did) makes them grow ~Nx and completely swamp
argument quality — a debater with a couple more infractions then loses regardless of how
well they argued.

### Decisive Verdict
The Father must return `pro` or `con`; exported ties are invalid. If totals are exactly
equal, the implementation breaks the deadlock without a fixed side preference.

## Penalty Handling
Penalties DO affect the final score and therefore the winner (see Final Score). They are
applied exactly once, in `DebateEngine.run_final_scoring`, before the winner is declared;
`build_result` no longer re-applies them. Penalties include: disrespect, ignore_rebuttal,
stance_contradiction, exceed_words, exceed_lines, exceed_time, repetition.
Penalty names returned by the judge LLM are normalized case-insensitively before mapping
to typed penalties, so prompt wording like `stance_contradiction` and legacy uppercase
outputs both produce the same penalty object.

## Bias Mitigation (why Pro no longer always wins)
- **Neutral scoring example**: `build_round_prompt` shows the judge LLM an example JSON
  with EQUAL placeholder scores for both speakers. The previous example hard-coded Pro=75
  / Con=70 every round (the alternation of order and value cancelled out), anchoring the
  low-temperature LLM and making Pro win almost every debate.
- **Alternating order**: speaker order and the in-prompt display order alternate by round.
- **Per-round jitter**: `ScoreDefault.JITTER_RANGE` adds small noise so close debates
  resolve non-deterministically across runs.

## Repetition Detection
- Auto-detection via bigram Jaccard overlap (>55% threshold) when LLM judge misses it
- Source-reuse tracking: previously cited sources detected and penalized
- Cited sources injected into debater prompt as "DO NOT cite again"

## Interface
- `JudgeAgent.observe_round(round_number, pro_argument, con_argument, debate_history=None) -> RoundEvaluation` (includes per-round speaker scores)
- `JudgeAgent.evaluate_debate(transcript) -> dict[str, Score]` (averages per-round scores)
- `JudgeAgent.declare_winner(scores) -> str` (`"pro"` or `"con"`)

## Acceptance
- Integration tests verify Father mediation, per-round scoring, decisive winner validation, penalty tracking, and stance verification.
