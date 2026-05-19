# Prompt Engineering Log

## Judge Prompt
- Purpose: Evaluate debate technique without claiming domain expertise.
- Current form: `JudgeAgent` builds a concise prompt scoped to debate technique.
- Rationale: Keeps Father in a listener/scorer role and avoids bidirectional debate intervention.
- Iteration notes: Future real-API calibration should add internet-sourced rubric excerpts during judge initialization.

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
