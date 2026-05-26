# TODO — AI Court Debate Simulator

## Legend

- [ ] = Not started
- [~] = In progress
- [x] = Done
- Priority: **P0** (critical) | **P1** (high) | **P2** (medium) | **P3** (low)
- DoD = Definition of Done per task

### Definition of Done Template

Every task in this TODO is "done" when **all** of the following are true:
1. The task's deliverable exists in the codebase (code, test, doc, or config file)
2. All associated tests pass (`uv run pytest` — no failures)
3. `ruff check` passes with 0 errors on the new code
4. The file is **<= 150 lines** (if it's a Python file)
5. The task's commit has a meaningful message following conventional commits format
6. No hardcoded constants — all from config/env/constants

---

## Phase 1: Project Foundation & UV Setup

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 1.1 | Initialize project with `uv init` — create `pyproject.toml` | P0 | [x] | — |
| 1.2 | Create full directory structure per PLAN §1 (src/, tests/, docs/, config/, data/, results/, assets/, notebooks/, logs/) | P0 | [x] | 1.1 |
| 1.3 | Create all `__init__.py` files with `__all__` and `__version__` exports | P0 | [x] | 1.2 |
| 1.4 | Set version to **1.00** in `shared/version.py` | P0 | [x] | 1.3 |
| 1.5 | Create `.env.example` with `OPENAI_API_KEY=your_api_key_here` | P0 | [x] | — |
| 1.6 | Create `.gitignore` (exclude `.env`, `logs/`, `.rag_store/`, `__pycache__/`, `results/`, `.venv/`, `*.pyc`) | P0 | [x] | — |
| 1.7 | Create `config/setup.json` with all defaults (version 1.00) | P0 | [x] | 1.2 |
| 1.8 | Create `config/rate_limits.json` with rate limits (version 1.00) | P0 | [x] | 1.2 |
| 1.9 | Create `data/topics.json` with 10 debate topics across 5 categories | P0 | [x] | — |
| 1.10 | Implement `shared/config.py` — load JSON configs + env vars via pydantic | P0 | [x] | 1.7, 1.8 |
| 1.11 | Implement `shared/constants.py` — all immutable project constants as Enums | P0 | [x] | 1.3 |
| 1.12 | Add all project dependencies to `pyproject.toml` via `uv add` | P0 | [x] | 1.1 |
| 1.13 | Run `uv lock` to generate `uv.lock` | P0 | [x] | 1.12 |
| 1.14 | Verify `uv sync` installs everything on clean environment | P0 | [x] | 1.13 |
| 1.15 | Create `src/debate_simulator/__main__.py` — enable `python -m debate_simulator` execution | P0 | [x] | 1.1 |
| 1.16 | Design shared test fixtures in `tests/conftest.py` — mock LLM, mock search, mock RAG, sample topics, sample agents | P0 | [x] | 1.3 |

---

## Phase 2: Logging Pipeline (PyPI Package)

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 2.1 | Implement `infrastructure/logging/rotating_writer.py` — 20 files, 500 lines, thread-safe, circular overwrite | P0 | [x] | 1.2 |
| 2.2 | Implement `infrastructure/logging/fifo_logger.py` — named pipe creation, non-blocking writes | P0 | [x] | 2.1 |
| 2.3 | Implement `infrastructure/logging/log_consumer.py` — background thread, FIFO → format → RotatingWriter | P0 | [x] | 2.1, 2.2 |
| 2.4 | Add log format: `[ISO8601] [LEVEL] [AGENT/COMPONENT] Message` | P0 | [x] | 2.3 |
| 2.5 | Write per-mechanism PRD: `docs/PRD_logging_pipeline.md` | P1 | [x] | 2.4 |
| 2.6 | Unit test (RED): rotating writer — test 20-file rotation, 500-line limit, circular overwrite | P0 | [x] | 2.1 |
| 2.7 | Unit test (RED): FIFO logger — test pipe creation, non-blocking writes | P0 | [x] | 2.2 |
| 2.8 | Unit test (RED): log consumer — test formatting, dispatch to writer | P0 | [x] | 2.3 |
| 2.9 | Integration test (RED): multiple concurrent loggers → FIFO → no data loss | P1 | [x] | 2.8 |
| 2.10 | GREEN: implement all tests to pass | P0 | [x] | 2.6–2.9 |
| 2.11 | REFACTOR: clean up logging code | P1 | [x] | 2.10 |

---

## Phase 3: API Gatekeeper

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 3.1 | Implement `shared/gatekeeper.py` — ApiGatekeeper class with `execute()` method | P0 | [x] | 1.8, 1.10 |
| 3.2 | Implement rate limiting: requests_per_minute, requests_per_hour, concurrent_max | P0 | [x] | 3.1 |
| 3.3 | Implement FIFO queue for requests when rate limit reached | P0 | [x] | 3.2 |
| 3.4 | Implement retry with exponential backoff on transient failures | P0 | [x] | 3.1 |
| 3.5 | Implement logging for every API call through gatekeeper | P0 | [x] | 3.1 |
| 3.6 | Implement queue status monitoring (`get_queue_status()`) | P1 | [x] | 3.3 |
| 3.7 | Implement backpressure when queue is full | P1 | [x] | 3.3 |
| 3.8 | Write per-mechanism PRD: `docs/PRD_api_gatekeeper.md` | P1 | [x] | 3.7 |
| 3.9 | Unit test (RED): rate limiting — verify limits enforced, verify queue used | P0 | [x] | 3.2 |
| 3.10 | Unit test (RED): retry logic — verify backoff, verify max retries | P0 | [x] | 3.4 |
| 3.11 | Unit test (RED): queue test — verify FIFO ordering, verify backpressure | P1 | [x] | 3.3 |
| 3.12 | GREEN: implement all gatekeeper tests to pass | P0 | [x] | 3.9–3.11 |
| 3.13 | REFACTOR: clean up gatekeeper code | P1 | [x] | 3.12 |

---

## Phase 4: Search & RAG Pipeline

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 4.1 | Implement `infrastructure/search/searcher.py` — DuckDuckGo search abstraction | P0 | [x] | 1.12 |
| 4.2 | Implement `infrastructure/search/fetcher.py` — fetch URL, extract text, clean HTML | P0 | [x] | 1.12 |
| 4.3 | Implement `infrastructure/rag/vector_store.py` — ChromaDB wrapper (init, add, query, reset) | P0 | [x] | 1.12 |
| 4.4 | Implement `infrastructure/rag/embedder.py` — sentence-transformers wrapper | P0 | [x] | 1.12 |
| 4.5 | Implement `infrastructure/rag/chunker.py` — document chunking (configurable size + overlap) | P0 | [x] | — |
| 4.6 | Write per-mechanism PRD: `docs/PRD_search_engine.md` | P1 | [x] | 4.2 |
| 4.7 | Write per-mechanism PRD: `docs/PRD_rag_system.md` | P1 | [x] | 4.5 |
| 4.8 | Unit test (RED): searcher — mock DDG, verify query → results | P0 | [x] | 4.1 |
| 4.9 | Unit test (RED): fetcher — mock HTTP, verify text extraction | P0 | [x] | 4.2 |
| 4.10 | Unit test (RED): vector store — mock ChromaDB, verify add/query/reset | P0 | [x] | 4.3 |
| 4.11 | Unit test (RED): chunker — verify size, overlap, no data loss | P0 | [x] | 4.5 |
| 4.12 | Integration test (RED): search → fetch → chunk → embed → store → retrieve round-trip | P1 | [x] | 4.1–4.5 |
| 4.13 | GREEN: implement all search/RAG tests to pass | P0 | [x] | 4.8–4.12 |
| 4.14 | REFACTOR: clean up search/RAG code | P1 | [x] | 4.13 |

---

## Phase 5: Skills Framework

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 5.1 | Implement `skills/base_skill.py` — abstract `BaseSkill` with `execute()` and `SkillResult` | P0 | [x] | 1.3 |
| 5.2 | Implement `skills/router_skill.py` — reads skill.md files, selects appropriate skill | P0 | [x] | 5.1 |
| 5.3 | Implement `skills/web_search/` — skill.md + skill.py (DuckDuckGo search) | P0 | [x] | 5.1, 4.1 |
| 5.4 | Implement `skills/rag_store/` — skill.md + skill.py | P0 | [x] | 5.1, 4.3 |
| 5.5 | Implement `skills/rag_retrieve/` — skill.md + skill.py | P0 | [x] | 5.1, 4.3 |
| 5.6 | Implement `skills/fact_check/` — skill.md + skill.py (LLM-powered) | P1 | [x] | 5.1 |
| 5.7 | Implement `skills/stance_check/` — skill.md + skill.py | P1 | [x] | 5.1 |
| 5.8 | Implement `skills/respect_check/` — skill.md + skill.py | P1 | [x] | 5.1 |
| 5.9 | Implement `skills/rebuttal_check/` — skill.md + skill.py | P1 | [x] | 5.1 |
| 5.10 | Implement `skills/argument_builder/` — skill.md + skill.py | P1 | [x] | 5.1 |
| 5.11 | Implement `skills/rebuttal_builder/` — skill.md + skill.py | P1 | [x] | 5.1 |
| 5.12 | Unit test (RED): BaseSkill — verify interface, verify SkillResult | P0 | [x] | 5.1 |
| 5.13 | Unit test (RED): RouterSkill — verify skill selection based on context | P0 | [x] | 5.2 |
| 5.14 | Unit test (RED): each skill — mock dependencies, verify execute() | P0 | [x] | 5.3–5.11 |
| 5.15 | GREEN: implement all skill tests to pass | P0 | [x] | 5.12–5.14 |
| 5.16 | REFACTOR: clean up skills code | P1 | [x] | 5.15 |

---

## Phase 6: Agent System

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 6.1 | Implement `shared/llm_client.py` — OpenAI SDK wrapper with retry, error handling | P0 | [x] | 1.10, 3.1 |
| 6.2 | Implement `models/agent.py` — data models (Message, TurnContext, AgentResponse) | P0 | [x] | 1.3 |
| 6.3 | Implement `models/debate.py` — data models (Round, Score, Penalty, DebateResult) | P0 | [x] | 1.3 |
| 6.4 | Implement `models/config_models.py` — pydantic models for config validation | P0 | [x] | 1.10 |
| 6.5 | Implement `agents/base_agent.py` — abstract BaseAgent (skill registry, memory, prompt builder) | P0 | [x] | 5.1, 6.1, 6.2 |
| 6.6 | Design judge system prompt — debate technique evaluator, NOT domain expert | P0 | [x] | — |
| 6.7 | Implement `agents/judge_agent.py` — research criteria, evaluate rounds, score debate | P0 | [x] | 6.5, 6.6, 5.6–5.9 |
| 6.8 | Design debater system prompt — stance, evidence-based, must-reply, respectful | P0 | [x] | — |
| 6.9 | Implement `agents/debater_agent.py` — research, argument, rebuttal with RAG + search | P0 | [x] | 6.5, 6.8, 5.3–5.5, 5.10–5.11 |
| 6.10 | Write per-mechanism PRD: `docs/PRD_judge_evaluation.md` | P1 | [x] | 6.7 |
| 6.11 | Write per-mechanism PRD: `docs/PRD_process_management.md` | P1 | [x] | 7.1 |
| 6.12 | Unit test (RED): BaseAgent — initialization, skill registry, prompt construction | P0 | [x] | 6.5 |
| 6.13 | Unit test (RED): JudgeAgent — scoring, penalty detection (mock LLM) | P0 | [x] | 6.7 |
| 6.14 | Unit test (RED): DebaterAgent — research phase, response generation (mock LLM) | P0 | [x] | 6.9 |
| 6.15 | Unit test (RED): models — verify data model validation | P0 | [x] | 6.2–6.4 |
| 6.16 | GREEN: implement all agent tests to pass | P0 | [x] | 6.12–6.15 |
| 6.17 | REFACTOR: clean up agent code | P1 | [x] | 6.16 |

---

## Phase 7: Process Management & SDK

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 7.1 | Implement `shared/process_manager.py` — spawn agents as processes, enforce timeouts | P0 | [x] | — |
| 7.2 | Implement watchdog mechanism — keep-alive pings, detect stuck processes | P0 | [x] | 7.1 |
| 7.3 | Implement SIGKILL on timeout — log event, record penalty, fallback response | P0 | [x] | 7.1 |
| 7.4 | Implement cumulative penalty tracking per agent | P1 | [x] | 7.1 |
| 7.5 | Implement JSON-capable IPC helpers for agent/process communication | P0 | [x] | 7.1 |
| 7.6 | Implement `sdk/sdk.py` — SDK entry point: start_debate(), list_topics(), get_results() | P0 | [x] | 8.1 |
| 7.7 | Unit test (RED): ProcessManager — timeout triggers kill, penalty recorded | P0 | [x] | 7.1 |
| 7.8 | Unit test (RED): Watchdog — detect stuck process, trigger kill | P1 | [x] | 7.2 |
| 7.9 | Unit test (RED): IPC — verify JSON communication between mock processes | P0 | [x] | 7.5 |
| 7.10 | GREEN: implement all process management tests to pass | P0 | [x] | 7.7–7.9 |
| 7.11 | REFACTOR: clean up process management code | P1 | [x] | 7.10 |

---

## Phase 8: Services & Debate Engine

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 8.1 | Implement `services/debate_engine.py` — topic loading, agent initialization | P0 | [x] | 6.7, 6.9, 1.9 |
| 8.2 | Implement research phase — parallel search for all 3 agents | P0 | [x] | 8.1, 4.1–4.5 |
| 8.3 | Implement debate ping loop — alternating speaker order, Father-mediated relay, 10 pings | P0 | [x] | 8.1 |
| 8.4 | Implement final scoring — judge reviews transcript, outputs scores + decisive winner | P0 | [x] | 8.3, 6.7 |
| 8.5 | Implement JSON export to `results/<timestamp>_<topic>.json` | P0 | [x] | 8.4 |
| 8.6 | Implement `services/scoring_service.py` — weighted score computation, penalty application | P0 | [x] | 6.3 |
| 8.7 | Implement `main.py` — CLI entry point consuming SDK (argparse + rich) | P0 | [x] | 7.6 |
| 8.8 | Implement CLI flags: `--topic`, `--custom-topic`, `--pings`, `--config`, `--list-topics` | P0 | [x] | 8.7 |
| 8.9 | Implement rich terminal output — round headers, agent names, progress bars | P2 | [x] | 8.7 |
| 8.10 | Unit test (RED): DebateEngine — mock agents, verify flow, verify JSON output | P0 | [x] | 8.1 |
| 8.11 | Unit test (RED): ScoringService — verify weighted scoring, penalty deduction, decisive tiebreaking | P0 | [x] | 8.6 |
| 8.12 | Unit test (RED): CLI — verify argument parsing | P1 | [x] | 8.8 |
| 8.13 | GREEN: implement all service tests to pass | P0 | [x] | 8.10–8.12 |
| 8.14 | REFACTOR: clean up services code | P1 | [x] | 8.13 |

---

## Phase 9: Custom Topic & Edge Cases

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 9.1 | Add `--custom-topic` CLI flag | P1 | [x] | 8.8 |
| 9.2 | Handle LLM API errors — rate limit, auth error, server error → retry with backoff | P0 | [x] | 6.1 |
| 9.3 | Handle search failure — proceed with agent's knowledge, log warning | P1 | [x] | 4.1 |
| 9.4 | Handle RAG failure — proceed without retrieval, log warning | P1 | [x] | 4.3 |
| 9.5 | Handle agent crash mid-debate — continue, apply penalty to crashed agent | P1 | [x] | 8.3 |
| 9.6 | Handle graceful shutdown (Ctrl+C) — save partial results, cleanup FIFO | P1 | [x] | 8.7 |
| 9.7 | Handle missing `.env` / missing API key — clear error on startup | P0 | [x] | 1.5 |
| 9.8 | Handle edge cases: empty input, null LLM response, concurrent failures | P1 | [x] | 8.3 |

---

## Phase 10: Integration & E2E Testing

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 10.1 | Integration test (RED): full debate with mocked LLM (verify flow, JSON output) | P0 | [x] | 8.7 |
| 10.2 | Integration test (RED): logging pipeline end-to-end | P1 | [x] | 2.11 |
| 10.3 | Integration test (RED): SDK entry point — verify CLI → SDK → Services chain | P0 | [x] | 8.7 |
| 10.4 | E2E test: real debate with real API — verify non-determinism across 3+ runs | P0 | [ ] | 8.7 |
| 10.5 | Test: verify penalties correctly applied and reflected in final scores | P1 | [x] | 10.1 |
| 10.6 | Test: verify timeout kills agent and records penalty | P1 | [x] | 7.10 |
| 10.7 | Test: verify equal scores still produce a decisive winner | P1 | [x] | 10.1 |
| 10.8 | Test: verify Father observes without coaching during debate | P1 | [x] | 10.1 |
| 10.9 | Test: verify child arguments are Father-mediated, not direct child-to-child context | P1 | [x] | 10.1 |
| 10.10 | GREEN: implement all integration/E2E tests to pass | P0 | [x] | 10.1–10.9 |
| 10.11 | REFACTOR: clean up integration code | P1 | [x] | 10.10 |

---

## Phase 11: Code Quality & Coverage

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 11.1 | Run `ruff check` — fix all linter errors → **0 errors** | P0 | [x] | All code |
| 11.2 | Run `ruff format` — auto-format all code | P0 | [x] | 11.1 |
| 11.3 | Run `uv run pytest --cov` — measure coverage | P0 | [x] | All tests |
| 11.4 | Achieve **>= 85% coverage** (statement + branch + path) | P0 | [x] | 11.3 |
| 11.5 | Add missing tests to reach 85% threshold | P0 | [x] | 11.4 |
| 11.6 | Verify all files are **<= 150 lines** — split large files | P0 | [x] | All code |
| 11.7 | Verify no hardcoded constants — all from config/env | P0 | [x] | All code |
| 11.8 | Verify no secrets/API keys in codebase | P0 | [x] | All code |
| 11.9 | Verify docstrings on all public functions and classes | P1 | [x] | All code |
| 11.10 | Verify type hints on all public functions | P1 | [x] | All code |
| 11.11 | Verify DRY — extract shared logic, remove duplication | P1 | [x] | All code |

---

## Phase 12: Documentation

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 12.1 | Move PRD.md, PLAN.md, TODO.md to `docs/` | P0 | [x] | — |
| 12.2 | Write `docs/PRD_search_engine.md` — per-mechanism PRD | P1 | [x] | 4.6 |
| 12.3 | Write `docs/PRD_rag_system.md` — per-mechanism PRD | P1 | [x] | 4.7 |
| 12.4 | Write `docs/PRD_judge_evaluation.md` — per-mechanism PRD | P1 | [x] | 6.10 |
| 12.5 | Write `docs/PRD_api_gatekeeper.md` — per-mechanism PRD | P1 | [x] | 3.8 |
| 12.6 | Write `docs/PRD_logging_pipeline.md` — per-mechanism PRD | P1 | [x] | 2.5 |
| 12.7 | Write `docs/PRD_process_management.md` — per-mechanism PRD | P1 | [x] | 6.11 |
| 12.8 | Create Prompt Engineering Log — document all system prompts with rationale, iterations, performance | P0 | [x] | 6.6, 6.8 |
| 12.9 | Create token/cost tracking table — per model, per agent | P1 | [x] | 10.4 |
| 12.10 | Create `README.md` — installation, usage, examples, architecture, config reference | P0 | [x] | 8.7 |
| 12.11 | Add C4 architecture diagrams to README (ASCII or mermaid) | P0 | [x] | 12.10 |
| 12.12 | Add screenshots of terminal debate output to README | P0 | [~] | 10.4 |
| 12.13 | Add example JSON output to README | P1 | [x] | 8.5 |
| 12.16 | Create results analysis notebook — per-agent score tables, cross-run comparisons, statistics | P1 | [x] | 10.4 |
| 12.17 | Generate visualizations — bar charts (score comparison), line charts (cross-run variance), heatmaps (criteria correlation) | P1 | [x] | 12.16 |
| 12.18 | Add License & Credits section to README | P1 | [x] | 12.10 |
| 12.19 | Include assignment PDF from Moodle + student photos in submission package | P1 | [ ] | 14.16 |

---

## Phase 13: Git Practices

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 13.1 | Initialize git repository with meaningful initial commit | P0 | [x] | 1.6 |
| 13.2 | Use feature branches for each phase | P1 | [ ] | 13.1 |
| 13.3 | Write meaningful commit messages (conventional commits format) | P0 | [x] | All |
| 13.4 | Tag version **1.00** | P0 | [x] | All |
| 13.5 | Verify git history shows clean development progression | P1 | [x] | All |

---

## Phase 14: Final Review & Submission
| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 14.1 | Verify `.env.example` has placeholder only, no real keys | P0 | [x] | 1.5 |
| 14.2 | Verify no `.env` committed (only `.env.example`) | P0 | [x] | 1.6 |
| 14.3 | Run `uv sync` on clean environment → verify all installs | P0 | [x] | 1.14 |
| 14.4 | Run `ruff check` → verify **0 errors** | P0 | [x] | 11.1 |
| 14.5 | Run `uv run pytest --cov` → verify **>= 85% coverage** | P0 | [x] | 11.4 |
| 14.6 | Verify all files **<= 150 lines** | P0 | [x] | 11.6 |
| 14.7 | Verify version is **1.00** in all versioned files | P0 | [x] | 1.4 |
| 14.8 | Verify logging: 20 files created, 500 lines each, FIFO working | P1 | [x] | 2.11 |
| 14.9 | Verify JSON output is valid and complete | P0 | [x] | 8.5 |
| 14.10 | Verify non-determinism: same debate 5 times, results vary | P0 | [ ] | 10.4 |
| 14.11 | Verify all penalties work (respect, rebuttal, stance, timeout, lines) | P1 | [x] | 10.5 |
| 14.12 | Final code cleanup — remove debug prints, unused imports, dead code | P1 | [x] | All |
| 14.13 | Verify README is comprehensive with screenshots, diagrams, examples | P0 | [x] | 12.10 |
| 14.14 | Verify all `docs/` PRDs are complete | P0 | [x] | 12.2–12.7 |
| 14.15 | Verify Prompt Engineering Log is documented | P0 | [x] | 12.8 |
| 14.16 | Package for submission | P0 | [ ] | All |

---

## Phase 15: Debate Quality Overhaul

Issues identified from manual test: agents repeat arguments, Pro argues Con's position, arguments too long, judge doesn't penalize repetition, judge fallback triggers on round 3.

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 15.1 | Add `REPETITION` penalty type to `PenaltyType` enum in constants.py | P0 | [x] | — |
| 15.2 | Add `REPETITION = -10` to `PenaltyPoints` enum in constants.py | P0 | [x] | 15.1 |
| 15.3 | Add `repetition: 10` penalty to `config/setup.json` penalties section | P0 | [x] | 15.1 |
| 15.4 | Add `max_words_per_response: 60` to `DebateConfig` in `shared/config.py` | P0 | [x] | — |
| 15.5 | Keep assignment default at 10 pings in `config/setup.json` | P0 | [x] | — |
| 15.6 | Reduce `max_lines_per_response` from 3 to 2 in `config/setup.json` | P0 | [x] | — |
| 15.7 | Reduce `max_tokens_per_response` from 1024 to 512 in `config/setup.json` | P0 | [x] | — |
| 15.8 | Rewrite `debater_system.md` — explicit stance rules with examples, no-repetition rule, word/line caps, new-argument-per-round rule, previous-arguments block | P0 | [x] | 15.1 |
| 15.9 | Rewrite `judge_system.md` — add stance verification section, repetition/failure-to-advance penalties, instruction to compare against history, stricter feedback | P0 | [x] | 15.1 |
| 15.10 | Update `debater_agent.py` — add `previous_arguments` list, inject into prompt, add `_check_repetition()` with 60% Jaccard overlap, add word-count penalty | P0 | [x] | 15.1 |
| 15.11 | Update `judge_agent.py` — accept `debate_history` in `observe_round()`, pass last 4 rounds to judge prompt, add `_auto_repetition_penalties()` with 70% Jaccard, handle `REPETITION` in `_penalties()` | P0 | [x] | 15.1 |
| 15.12 | Update `debate_engine.py` — pass `debate_history` to judge, add `max_words` param, update defaults | P0 | [x] | 15.11 |
| 15.13 | Update `judge_service.py` — pass through `debate_history` to agent | P1 | [x] | 15.11 |
| 15.14 | Update `docs/TODO.md` with Phase 15 tasks | P0 | [x] | — |
| 15.15 | Update `docs/PRD.md` — add repetition penalty, word limit, stance enforcement | P1 | [x] | 15.12 |
| 15.16 | Update `docs/PLAN.md` — update config defaults, add ADR-011 | P1 | [x] | 15.12 |
| 15.17 | Update `docs/PRD_judge_evaluation.md` — add repetition detection and stance verification | P1 | [x] | 15.11 |
| 15.18 | Run `uv run pytest` — all existing tests pass with new signatures | P0 | [x] | 15.1–15.13 |
| 15.19 | Run `uv run ruff check src/` — 0 errors | P0 | [x] | 15.1–15.13 |
| 15.20 | Second manual test: raise word cap 60→75, upgrade repetition to bigram overlap, fix judge JSON parse, improve fallback notes, ban repeated citations in prompt | P0 | [x] | 15.18 |
| 15.21 | Third manual test: raise word cap 75→90, exclude URLs from word count, add source-reuse detection, inject used sources into prompt | P0 | [x] | 15.20 |
| 15.22 | Redesign judge system: align with World Schools rubric (Content 40% + Style 30% + Strategy 30%), add per-round 50-100 speaker scoring, separate penalties from quality scores, add dropped argument tracking | P0 | [x] | 15.21 |

---

## Phase 16: Judge Bias Fix & Penalty Normalization

Issue from manual testing: the **Pro agent won almost every debate**. Root cause was an
asymmetric scoring example anchoring the judge LLM toward Pro every round, compounded by a
penalty unit-mismatch (summed vs averaged) and penalties never reaching the winner decision.
See PLAN ADR-012 and PRD_judge_evaluation §Bias Mitigation.

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 16.1 | Make `build_round_prompt` example use EQUAL placeholder scores (remove Pro=75/Con=70 anchor) | P0 | [x] | — |
| 16.2 | Fold penalties into `Score.total`, averaged per round, in `run_final_scoring` | P0 | [x] | 16.1 |
| 16.3 | `declare_winner` compares penalty-adjusted totals and returns only `pro` or `con` | P0 | [x] | 16.2 |
| 16.4 | Remove bogus range-midpoint normalization in `evaluate_debate` | P0 | [x] | — |
| 16.5 | Remove double penalty application (drop throwaway `build_result` in `run_final_scoring`; remove `apply_final_penalties` from `build_result`) | P0 | [x] | 16.2 |
| 16.6 | Remove tie-margin winner behavior to match the lecture's no-tie rule | P1 | [x] | 16.3 |
| 16.7 | `tests/test_bias.py` — tally Pro/Con across N debates | P0 | [x] | — |
| 16.8 | Verify: `ruff check` 0 errors, `pytest` 148 passed / 1 skipped, coverage 91.37% | P0 | [x] | 16.1–16.6 |
| 16.9 | E2E bias verification: `test_bias.py -n 20` shows no systematic lean | P0 | [~] | 16.7 |
| 16.10 | (follow-up) Make judge spread quality scores more (reduce ~70 clustering) so quality, not jitter, drives close calls | P1 | [ ] | 16.9 |
| 16.11 | Move `test_bias.py` under `tests/` | P2 | [x] | 16.7 |
| 16.12 | Remove obsolete `tie_margin` config after decisive-winner correction | P2 | [x] | 16.6 |

This also advances the previously-open non-determinism items: **10.4**, **10.10**, **14.10**.

---

## Phase 17: Assignment Compliance Hardening

Corrections after re-reading the lecture summary and software submission guidelines.

| # | Task | Priority | Status | Depends On |
|---|------|----------|--------|-----------|
| 17.1 | Stop the long-running `tests/test_bias.py -n 20` API run before changing semantics | P0 | [x] | — |
| 17.2 | Enforce no exported ties in `DebateResult`, `JudgeAgent`, and `ScoringService` | P0 | [x] | 16.2 |
| 17.3 | Keep default debate length at the required 10 pings across config and docs | P0 | [x] | 15.5 |
| 17.4 | Run debater turns through subprocess timeout management and preserve parent-side agent state | P0 | [x] | 7.1 |
| 17.5 | Relay opponent messages through Father context instead of direct child-to-child wording | P0 | [x] | 8.3 |
| 17.6 | Give the Father agent internet search for debate-judging criteria | P0 | [x] | 4.1 |
| 17.7 | Start FIFO log consumer from the SDK so gatekeeper calls reach rotating logs | P1 | [x] | 2.3 |
| 17.8 | Update README/PRDs/PLAN/TODO to match decisive-winner and 10-ping rules | P0 | [x] | 17.2 |
| 17.9 | Normalize judge penalty names case-insensitively so LLM outputs like `STANCE_CONTRADICTION` are not dropped | P0 | [x] | 15.9 |
| 17.10 | Split oversized judge-helper tests so all Python files stay at or below 150 lines | P1 | [x] | 17.8 |
| 17.11 | Wire CLI `--config` into the SDK settings loader instead of ignoring the public flag | P0 | [x] | 8.8 |
| 17.12 | Add `/tmp` FIFO fallback for WSL `/mnt/c` and other filesystems that reject `mkfifo` | P0 | [x] | 2.3 |
| 17.13 | Live smoke test: `main.py --topic 1 --pings 1` completes after FIFO fallback | P1 | [x] | 17.12 |

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Total tasks | **156** |
| P0 (critical) | **102** |
| P1 (high) | **45** |
| P2 (medium) | **9** |
| P3 (low) | **0** |
| Phases | **17** |

### Professor's Grading Checklist (from submission guidelines V3)

| Requirement | Where | Status |
|-------------|-------|--------|
| SDK architecture — single entry point for ALL logic | `sdk/sdk.py` | Covered: 7.6 |
| OOP 2+ inheritance levels | `agents/base_agent.py` → `DebaterAgent` → `ProDebaterAgent/ConDebaterAgent` | Covered: 6.5 |
| Template Method pattern | `BaseAgent.run_turn()` with hooks | Covered: ADR-009 |
| Mixins (one behavior each) | `TimeoutMixin`, `LoggingMixin`, `SkillRegistryMixin` | Covered: ADR-009 |
| Plugin lifecycle hooks | `hooks/` — on_debate_start, on_round_start, on_penalty, on_round_end, on_debate_end | Covered: 4.9 PLAN, 7.5 TODO |
| Context Engineering (Write/Select) | `docs/PRD_context_engineering.md` | Covered: PRD §3.9 |
| Session management | Per-debate scoped context, 5 lifecycle states | Covered: PRD §3.10 |
| ISO/IEC 25010 quality | PRD §4.13 | Covered: PRD §4.13 |
| Results visualization | `notebooks/` + bar/line/heatmap charts | Covered: 12.16, 12.17 |
| License & Credits | README §License | Covered: 12.18 |
| Submission artifact | Assignment PDF + photos | Covered: 12.19 |
| conftest.py shared fixtures | `tests/conftest.py` | Covered: 1.16 |
| __main__.py | `src/debate_simulator/__main__.py` | Covered: 1.15 |
| Speaker order fairness | Alternating Pro-first / Con-first ping loop | Covered: 8.3 |
| API Gatekeeper for all external calls | `shared/gatekeeper.py` | Covered: 3.1–3.7 |
| Rate limiting from config file | `config/rate_limits.json` | Covered: 1.8, 3.2 |
| Queue testing | Phase 3 tests | Covered: 3.11 |
| Version at 1.00 | `version.py` + configs | Covered: 1.4 |
| TDD RED-GREEN-REFACTOR | Every phase | Covered: Phase 2–8 |
| Automated tests >= 85% coverage | `pytest --cov` | Covered: 11.3–11.5 |
| Ruff linter 0 errors | `ruff check` | Covered: 11.1 |
| No hardcoded constants | config files + constants.py | Covered: 11.7 |
| `.env.example` no secrets | `.env.example` | Covered: 1.5 |
| UV package manager | `pyproject.toml` + `uv.lock` | Covered: 1.1, 1.13 |
| Meaningful git history | Conventional commits | Covered: 13.1–13.5 |
| Max 150 lines per file | All files | Covered: 11.6 |
| Prompt engineering log | `docs/` + README | Covered: 12.8 |
| README with screenshots + diagrams | `README.md` | Covered: 12.10–12.12 |
| FIFO logging 20 files × 500 lines | `infrastructure/logging/` | Covered: Phase 2 |
| docs/PRD.md + PLAN.md + TODO.md | `docs/` | Covered: 12.1 |
| Per-mechanism PRDs | `docs/PRD_*.md` | Covered: 12.2–12.7 |
| No API keys in code | `.gitignore` + checks | Covered: 11.8, 14.2 |

### Critical Path

```
1.1 → 1.12 → 1.13 → 2.1 → 3.1 → 4.1 → 5.1 → 6.1 → 6.5 → 7.1 → 8.1 → 8.7 → 10.4 → 11.1 → 11.4 → 14.16
```

### Parallel Tracks

```
Track A (Logging):     2.1 → 2.2 → 2.3 → 2.10 → 2.11
Track B (Gatekeeper):  3.1 → 3.2 → 3.3 → 3.12 → 3.13
Track C (Search/RAG):  4.1 → 4.2 → 4.3 → 4.13 → 4.14
Track D (Skills):      5.1 → 5.2 → 5.3 → 5.15 → 5.16
Track E (Agents):      6.1 → 6.5 → 6.7 → 6.16 → 6.17
Track F (Process):     7.1 → 7.2 → 7.10 → 7.11
Track G (Docs):        12.1 → 12.8 → 12.10 → 12.13
```
