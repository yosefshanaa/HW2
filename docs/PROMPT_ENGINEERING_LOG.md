# Prompt Engineering Log

## Judge Prompt
- Purpose: Evaluate debate technique without claiming domain expertise.
- Current form: `JudgeAgent` builds a concise prompt scoped to debate technique.
- Rationale: Keeps Father in a listener/scorer role and avoids bidirectional debate intervention.
- Iteration notes: Future real-API calibration should add internet-sourced rubric excerpts during judge initialization.

### Iteration: Neutral scoring example (bias fix)
- **Symptom**: Pro won almost every debate; per-round speaker scores landed ~75 (Pro) vs
  ~70 (Con) regardless of argument content.
- **Cause**: The round prompt's example JSON hard-coded `pro_speaker_score:75,
  con_speaker_score:70`. An attempt to "alternate" it swapped both the speaker order and
  the 75/70 values by round parity, so the two swaps cancelled and the example *always*
  showed Pro higher. The low-temperature judge LLM anchored to those example numbers.
- **Fix**: The example now uses the SAME placeholder score for both speakers
  (`ScoreDefault.DEFAULT_SPEAKER_SCORE`), carrying no signal about which side wins. Order
  still alternates; only the asymmetric numbers were removed.
- **Lesson**: Numbers placed in a JSON output template are not neutral illustration — a
  low-temperature model treats them as the expected answer. Keep example values symmetric.

## Debater Prompt
- Purpose: Produce stance-aligned arguments and rebuttals.
- Current form: `DebaterAgent` includes stance, topic, and opponent-last-argument context.
- Rationale: Keeps the Template Method stable while allowing skills to enrich context.
- Iteration notes: Future real-API calibration should add retrieved RAG snippets and line-limit reminders.

## Skill Prompts
- `fact_check`: verifies one claim against context.
- `argument_builder`: builds a structured argument from topic, stance, and evidence.
- `rebuttal_builder`: targets the opponent argument with context.

## Performance Notes
- Unit and integration tests use deterministic test doubles.
- Real prompt quality should be evaluated during E2E runs with `OPENAI_API_KEY`.
