# PRD — AI Court Debate Simulator

## 1. Overview

**AI Court Debate Simulator** is a terminal-based Python SDK application that simulates structured debates between two AI agents (Pro / Con) on a given topic, moderated and scored by a third AI agent acting as a **Judge (Father)**. The system uses LLM-powered agents with internet search capabilities, RAG pipelines, and strict process governance (timeouts, line limits, forced termination).

The judge is **not a domain expert** — he evaluates based on **argumentation quality, logical structure, evidence use, rebuttal effectiveness, and rhetorical technique**. The same debate, run multiple times with no code changes, may produce different winners due to non-deterministic LLM outputs and varying search results.

---

## 2. Stakeholders

| Role | Description |
|------|-------------|
| **Professor / Evaluator** | Runs the system, supplies API key via `.env`, grades per checklist |
| **Judge Agent (Father)** | Listens to debate, evaluates rounds, scores each debater, declares a decisive winner |
| **Pro Agent (Son 1)** | Argues in favor of the given topic |
| **Con Agent (Son 2)** | Argues against the given topic |

---

## 3. Functional Requirements

### 3.1 Agent System

#### 3.1.1 Judge Agent (Father)
- Acts as the **debate listener and final scorer** — does **not** intervene during the debate
- Does **not** claim domain expertise in the debate topic
- At startup, the judge searches the internet for **expert debate judging criteria** and builds his evaluation rubric from those sources
- Evaluates based on **debate craft metrics** (see §3.6)
- Enforces rules: respect, relevance, reply-compliance, time limits
- Issues **penalties** for:
  - Disrespectful language or ad hominem attacks
  - Failing to address the opponent's previous point (ignoring rebuttal)
  - Contradicting own stance (e.g., Pro agent making anti arguments)
  - Exceeding time, line, or word limits
  - Repeating arguments from earlier rounds
  - Failing to advance the debate with new content
- After all rounds: assigns a **score (%)** to each debater and declares a winner (`pro` or `con`; ties are not exported)
- Outputs full scoring breakdown as JSON
- **Communication is Father-mediated**: a son's argument is relayed by the Father as context for the other son, without coaching

#### 3.1.2 Debater Agents (Sons)
- Each debater is **randomly assigned** a stance: **Pro** or **Con** (they do not choose)
- Each debater is given the topic and performs **internet research** before the debate begins
- Each debater **must maintain their assigned stance** — Pro argues FOR the resolution, Con argues AGAINST it. Stance contradiction results in a -15 penalty
- During each round, the debater **must reply to the opponent's previous argument** — not ignore it
- Each debater must **introduce at least one new argument or angle per round** — repeating prior rounds results in a -10 penalty
- Each debater has a configurable **line limit** (default 2) and **word limit** (default 90) per response
- Each debater has a configurable **time limit** per turn
- If a debater's response contradicts their assigned stance, the judge penalizes them
- Debaters must maintain a **respectful tone** — politically correct, no racism, no ad hominem
- Each debater has a **Skill** it cannot refuse to use (its core competency)

### 3.2 Debate Topics

- **10 pre-configured debate topics** are bundled with the project
- Topics span 5 categories: **History, Current Affairs, Sports, Science, Culture** (2 per category)
- Topics are designed to have clear Pro/Con positions with room for evidence-based argumentation
- Users may also pass a **custom topic** via CLI argument
- Each topic includes a brief context blurb so agents understand the framing

| # | Category | Topic | Pro Position | Con Position |
|---|----------|-------|-------------|-------------|
| 1 | Sports | Barcelona vs Real Madrid — greatest football club | Barcelona | Real Madrid |
| 2 | Sports | Individual sports build character better than team sports | For | Against |
| 3 | Science | AI will replace most jobs by 2050 | For | Against |
| 4 | Science | Nuclear energy is the solution to climate change | For | Against |
| 5 | History | The British Empire did more good than harm | For | Against |
| 6 | History | Ancient Rome's collapse was inevitable | For | Against |
| 7 | Current Affairs | Universal Basic Income should be implemented globally | For | Against |
| 8 | Current Affairs | Social media does more harm than good to democracy | For | Against |
| 9 | Culture | Art should never be censored | For | Against |
| 10 | Culture | Remote work weakens company culture | For | Against |

### 3.3 Debate Flow

```
1. User selects topic (or provides custom topic) via CLI
2. System initializes 3 agents (Judge + 2 Debaters); debater turns run through subprocess timeout control
3. Judge fetches debate judging criteria from internet (search)
4. Both debaters perform internet research on the topic in parallel
5. Debate begins — 10 Pings (rounds), each side speaks once per ping:
   Ping N:
      a. Con Agent presents argument/rebuttal — timed (timeout enforced)
      b. Pro Agent responds to Con's argument — timed (timeout enforced)
      c. Judge observes and takes notes (does NOT intervene)
6. After 10 pings:
   a. Judge reviews full debate transcript (JSON)
   b. Judge scores each debater on multiple criteria (see §3.6)
   c. Judge declares a decisive winner
   d. Full results exported as JSON to results/
```

**Critical rule**: The Father mediates the conversation but does not coach the debaters. Child output is relayed through the Father as the next child's opponent context, and the Father delivers the final verdict.

### 3.4 Blocking & Time Governance

| Parameter | Default | Configurable | Description |
|-----------|---------|-------------|-------------|
| `max_pings` | 10 | Yes | Number of debate pings (rounds) |
| `agent_timeout` | 60s | Yes | Max time per agent turn before process kill |
| `keepalive_interval` | 10s | Yes | Watchdog keep-alive ping interval |
| `max_lines_per_response` | 2 | Yes | Max lines per agent response |
| `max_words_per_response` | 90 | Yes | Max words per agent response (URLs excluded) |
| `max_tokens_per_response` | 512 | Yes | Max tokens per LLM call |
| `research_timeout` | 120s | Yes | Max time for internet research phase |

- Every agent has a **timeout** — if exceeded, the agent is killed
- **Watchdog** mechanism ensures stuck agents are detected and terminated
- **Keep-alive** pings verify each agent is still responsive
- On timeout/kill: log the event, record a penalty, provide a fallback response

### 3.5 Internet Search & RAG

- **Internet search** is a **primary** requirement — agents must search the web for facts, statistics, expert opinions
- **RAG pipeline** augments search results:
  1. Agent queries search engine (DuckDuckGo — free, no API key needed)
  2. Relevant pages are fetched and chunked
  3. Chunks are embedded and stored in a **local vector store** (session-scoped)
  4. During debate rounds, agents can retrieve relevant chunks from the store
- RAG is **not a replacement for search** — it is an enhancement layer
- The judge also uses search to find **debate expert evaluation criteria**

See also: `docs/PRD_search_engine.md`, `docs/PRD_rag_system.md`

### 3.6 Judge's Evaluation Criteria

The judge evaluates each debater per round on a **50-100 speaker score scale**, then averages across rounds for the final quality score. Three weighted categories based on World Schools Debate Championship rules:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Content** | 40% | Arguments (claim + warrant + impact), evidence quality, credibility, recency |
| **Style** | 30% | Rhetoric, clarity, rebuttal effectiveness, respectful tone |
| **Strategy** | 30% | Engagement with opponent, dropped argument detection, stance consistency, novelty |

**Per-round scoring scale:**
- 90-100: Excellent — strong claim-warrant-impact chains, devastating rebuttals
- 80-89: Good — solid arguments, effective rebuttals
- 70-79: Average — some good points but weak rebuttals or repetitive
- 60-69: Below average — ignores opponent, weak evidence
- 50-59: Poor — no rebuttal, no evidence, contradicts stance

**Penalties** are tracked separately and do NOT reduce the quality score:
- Disrespectful language: tracked
- Ignoring opponent's point: tracked
- Contradicting own stance: tracked
- Exceeding line or word limit: tracked
- Exceeding time limit (auto-kill): tracked
- Repeating arguments from earlier rounds: tracked
- Failing to advance the debate with new content: tracked

**No exported ties** — the Father must choose `pro` or `con`. Exact score equality is broken without a fixed side preference.

See also: `docs/PRD_judge_evaluation.md`

### 3.7 Results & Output

- Full debate transcript saved as **JSON** (`results/<timestamp>_<topic_slug>.json`)
- JSON is the communication protocol between agents (IPC)
- JSON structure:
```json
{
  "topic": "Barcelona vs Real Madrid",
  "pro_agent": "Agent-Pro",
  "con_agent": "Agent-Con",
  "judge": "Agent-Judge",
  "pings": [
    {
      "ping_number": 1,
      "pro_argument": { "text": "...", "lines": 30, "time_seconds": 12.5, "penalties": [] },
      "con_argument": { "text": "...", "lines": 28, "time_seconds": 14.1, "penalties": [] },
      "judge_notes": { "pro": "...", "con": "..." }
    }
  ],
  "final_scores": {
    "pro": { "total": 78, "argument_strength": 82, "rebuttal": 75, "evidence": 80, "rhetoric": 76, "compliance": 90, "penalties": -12 },
    "con": { "total": 72, "argument_strength": 70, "rebuttal": 78, "evidence": 68, "rhetoric": 74, "compliance": 85, "penalties": -8 }
  },
  "winner": "pro",
  "judge_remarks": "..."
}
```

### 3.8 Skills System

- Each agent has a set of **project-local skills** (not global)
- Skills are Python modules stored in `src/debate_simulator/skills/` directory
- Each skill has a **description** that the agent reads to understand when to use it
- Each skill consists of:
  - `skill.md` — description file (what the skill does, when to use it)
  - `skill.py` — implementation file
  - Tools — in Python files, not in `__init__.py` (avoid side-effect imports)
- Skills follow the **Router-Skill pattern**: a router reads all skill descriptions and selects the appropriate one based on the user's message

| Skill | Owner | Description |
|-------|-------|-------------|
| `web_search` | All agents | Search the internet for information |
| `rag_retrieve` | All agents | Retrieve relevant context from vector store |
| `rag_store` | All agents | Store fetched content into vector store |
| `fact_check` | Judge | Verify claims made by debaters |
| `stance_check` | Judge | Detect if a debater contradicts their assigned stance |
| `respect_check` | Judge | Detect disrespectful language |
| `rebuttal_check` | Judge | Detect if a debater ignored the opponent's previous point |
| `argument_builder` | Debaters | Construct a structured argument with evidence |
| `rebuttal_builder` | Debaters | Construct a targeted rebuttal to the opponent's point |

### 3.9 Context Engineering

- The system uses **Context Engineering** (not just Prompt Engineering) to manage the LLM context window
- Two strategies are employed:

#### Write Strategy
- The **judge** uses Write at initialization: searches internet for debate judging criteria, extracts key rubrics, and writes a condensed evaluation prompt into the context window
- This extracted document replaces raw search results — keeping only what fits in the context window

#### Select Strategy
- During debate rounds, debaters use Select: query the RAG vector store to retrieve only the most relevant chunks for their current argument
- Only top-k relevant chunks are loaded — the rest stay on disk, not in memory

### 3.10 Session Management

- Each debate run is a **Session** — a time-bounded conversation with scoped context
- Session lifecycle:
  1. **INIT** — agents initialized, system prompts loaded
  2. **RESEARCH** — agents search internet, populate RAG stores (session-scoped, deleted after debate)
  3. **DEBATE** — 10 pings exchanged, all messages stored in session history
  4. **SCORING** — judge reviews full session transcript
  5. **FINISHED** — results exported to JSON, session context cleared, RAG stores purged
- All messages within a session are stored and queryable until session ends
- Context window is managed per-session: the judge's criteria document (Write) + RAG retrieval (Select) both operate within the session's scope

### 3.11 Non-Determinism

- The system is designed so that **the same debate can produce different winners** across runs
- This is achieved through:
  - LLM temperature > 0 (default 0.7)
  - Internet search results may vary
  - Order of retrieved RAG chunks may vary
- No seed fixing, no result caching

### 3.13 Acceptance Criteria & KPIs

| # | Requirement | KPI | Acceptance Criterion |
|---|-------------|-----|-------------------|
| AC-01 | Judge evaluates debate technique, not domain knowledge | Judge uses internet-sourced rubric | Judge system prompt contains no domain expertise claims |
| AC-02 | 10 pings completed per debate | 10 JSON ping entries in output | `pings` array length == 10 |
| AC-03 | Each agent respects timeout | 0 uncontrolled hangs | Every agent turn completes within `agent_timeout` or is killed + penalized |
| AC-04 | Debaters reply to opponent's previous point | Penalty rate < 2 per debate | `rebuttal_check` flags <= 1 ignored rebuttal per agent |
| AC-05 | Non-deterministic results | Different winners across runs | Same topic run repeatedly can produce both Pro and Con wins |
| AC-06 | JSON output validity | Parseable JSON | `results/*.json` passes JSON schema validation |
| AC-07 | Score breakdown completeness | 5 dimensions scored per debater | Each `final_scores` entry has all 5 weighted dimensions |
| AC-08 | Logging pipeline | 20 files × 500 lines | `logs/log_*.log` has exactly 20 files, none exceeding 500 lines |
| AC-09 | API Gatekeeper coverage | All external calls through gatekeeper | Zero direct `openai.ChatCompletion` calls outside gatekeeper |
| AC-10 | Test coverage | >= 85% | `pytest --cov` reports >= 85% statement + branch coverage |
| AC-11 | Linter | 0 errors | `ruff check` exits with code 0 |
| AC-12 | Session cleanup | No stale data after debate | RAG store and session context are empty after FINISHED |
| AC-13 | Father-mediated debate | No direct child-to-child context | Opponent arguments are relayed as Father-provided context |
| AC-14 | Decisive verdict | No exported ties | `winner` field is `"pro"` or `"con"` |
| AC-15 | No hardcoded constants | All from config/env | Zero literal values for URLs, timeouts, API keys in source code |

### 3.14 IPC & Communication

- Agents communicate via **Inter-Process Communication (IPC)**
- Communication protocol: **JSON** (JSONL format for streaming)
- Debater turns are isolated through subprocess execution and timeout control.
- IPC mechanisms used by the project include **FIFO (named pipes)** for logging and JSON-capable process queues for timed agent turns.
- Father mediates debate context: child output is relayed through the Father before the next child receives it.

---

## 4. Non-Functional Requirements

### 4.1 Logging System (PyPI Package)

- Architecture: **LOG → FIFO → 20 rotating files → 500 lines each**
- Implemented as a **PyPI-style package** within the project
- Configuration in `config/setup.json`:
  - `max_files`: 20
  - `max_lines_per_file`: 500
  - `fifo_path`: configurable
- Implementation:
  1. All agent actions, errors, and system events are logged
  2. Logs are written to a **named pipe (FIFO)** for asynchronous processing
  3. A log consumer writes to **rotating files** (max 20 files, 500 lines each)
  4. When file 20 reaches 500 lines, file 1 is overwritten (circular buffer)
- Log format: `[ISO8601] [LEVEL] [AGENT/COMPONENT] Message`
- Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

See also: `docs/PRD_logging_pipeline.md`

### 4.2 SDK-Based Architecture

- The application is built as an **SDK** — single entry point for all logic
- External consumers (CLI, potential GUI, API) interact only through the SDK
- No business logic in the CLI layer
- Architecture layers:
  ```
  External Consumers (CLI / Terminal)
       │
       ▼
  ┌─────────┐
  │   SDK   │  ← Single entry point for ALL logic
  └────┬────┘
       │
       ▼
  ┌─────────────┐
  │  Domain      │  ← Services, models, orchestrators (debate engine, agents)
  │  Services    │
  └────┬────────┘
       │
       ▼
  ┌──────────────┐
  │ Infrastructure│  ← Search, RAG, Logging, LLM client, Gatekeeper
  └──────────────┘
  ```

### 4.3 API Gatekeeper

- **All** external API calls (LLM, search) go through a centralized **API Gatekeeper**
- Features:
  - **Rate limiting** per minute/hour (configurable in `config/rate_limits.json`)
  - **Request queueing** — FIFO queue when rate limit reached
  - **Retry logic** — exponential backoff on transient failures
  - **Logging** — every API call is logged
  - **No hardcoded credentials** — all secrets from `.env`

See also: `docs/PRD_api_gatekeeper.md`

### 4.4 Terminal-Only Interface

- Primary interface: **terminal / CLI** via `rich` library
- The SDK is the primary interface — terminal is a consumer of the SDK
- Optional GUI for visualization (not required, but allowed)
- Must run in **environments with minimal Python packages installed**

### 4.5 Configuration

- **No hardcoded constants** — all parameters from config files or `.env`
- `.env.example` submitted (no real keys) — professor adds API key
- Config structure:
  - `config/setup.json` — main application config (versioned)
  - `config/rate_limits.json` — API rate limits (versioned)
  - `.env` — secrets (git-ignored)
- Constants stored in `src/debate_simulator/shared/constants.py` (immutable)
- Enum types for fixed-value parameters

### 4.6 Process Management

- Debater turns run in isolated **subprocesses** (multiprocessing)
- **Timeout** on every debater turn — if exceeded, process is killed
- **Watchdog** mechanism with keep-alive pings to detect stuck agents
- On kill: log the event, record a penalty, use a fallback response

See also: `docs/PRD_process_management.md`

### 4.7 Error Handling & Graceful Degradation

- Every error is logged (see §4.1)
- Graceful degradation: if search fails, agents proceed with their own knowledge
- If RAG fails, agents proceed without retrieval augmentation
- If an agent crashes, the debate continues with the remaining agent receiving a default penalty
- Edge cases tested: empty input, null responses, concurrent failures

### 4.8 Code Quality Standards

| Standard | Requirement |
|----------|-------------|
| **Max file length** | 150 lines per file |
| **Linter** | Ruff — 0 errors (`ruff check`) |
| **Code comments** | "Why" not "what" — explain decisions, not obvious code |
| **Docstrings** | All functions, classes, methods must have docstrings |
| **Type hints** | All public functions must have type annotations |
| **DRY** | Don't Repeat Yourself — extract shared logic |
| **Single Responsibility** | Each function/class has one clear purpose |
| **No hardcoded constants** | All from config files or `.env` |

### 4.9 Testing Standards (TDD)

| Standard | Requirement |
|----------|-------------|
| **Methodology** | TDD — RED → GREEN → REFACTOR for every feature |
| **Coverage** | Minimum **85%** (statement, branch, path coverage) |
| **Test structure** | Mirror `src/` structure in `tests/` |
| **Test naming** | One assertion per test function |
| **Fixtures** | Shared fixtures in `conftest.py` |
| **Mocking** | Mock all external services (API, search, DB) |
| **Automated** | Tests run on every commit (CI/CD ready) |
| **Edge cases** | Tested — boundary conditions, empty inputs, failures |
| **Graceful degradation** | Tested — simulate failures, verify fallback behavior |

### 4.10 Version Management

- Version starts at **1.00** across all versioned files:
  - `src/debate_simulator/shared/version.py`
  - `config/setup.json` (`"version"` field)
  - `config/rate_limits.json` (`"rate_limits.version"` field)

### 4.11 Prompt Engineering Log

- Every prompt used in the system must be documented with:
  - **Purpose** — what the prompt achieves
  - **Context** — when and why it was designed this way
  - **Iterations** — what was changed and why (based on results)
  - **Performance** — qualitative assessment of prompt effectiveness

### 4.12 Cost & Token Tracking

- Track API token usage per model (input tokens, output tokens, total cost)
- Track per agent (Judge, Pro, Con)
- **Cost optimization strategies**:
  - Use `gpt-4o-mini` for judge check skills (fact_check, respect_check) — cheaper than main model
  - Use batch processing for research phase queries where possible
  - Minimize context window usage via Context Engineering (Write/Select)
  - Truncate RAG chunks to essential content only
- Summary table in results and README

### 4.13 Quality Model (ISO/IEC 25010)

| Quality Attribute | How Addressed | NFR Reference |
|-------------------|--------------|--------------|
| **Functional Suitability** | All debate features work end-to-end: topics, pings, scoring, penalties | §3.1–3.8 |
| **Performance Efficiency** | Agent timeouts, watchdog, rate limiting prevent resource exhaustion | §3.4, §4.3 |
| **Compatibility** | Runs on Python 3.10+, terminal-only, minimal packages | §4.4 |
| **Usability** | CLI with rich output, clear error messages, one-command install | §4.4 |
| **Reliability** | Graceful degradation, edge case handling, auto-retry, watchdog recovery | §4.7 |
| **Security** | No secrets in code, .gitignore, .env.example only, least-privilege API keys | §4.5 |
| **Maintainability** | DRY, SRP, docstrings, type hints, 150-line files, TDD, linter | §4.8, §4.9 |
| **Portability** | UV for deps, pyproject.toml, no platform-specific code | §4.5 |

---

## 5. Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python 3.10+ | Required by submission |
| Package Manager | **UV** | Required by professor — fast, modern, `uv.lock` |
| Build System | `pyproject.toml` | Required — single source of truth for dependencies |
| LLM SDK | OpenAI Python SDK | Agent orchestration |
| Search | `duckduckgo-search` | Free, no API key needed |
| RAG / Embeddings | `chromadb` + `sentence-transformers` | Local vector store, no API needed |
| Async Framework | `asyncio` + `multiprocessing` | I/O-bound (async) + CPU-bound (process) |
| CLI | `argparse` + `rich` | Terminal interface |
| Config | `pydantic` + JSON/YAML | Type-safe configuration from files |
| Logging | Custom FIFO + rotating file handler | Per §4.1 requirements |
| API Gatekeeper | Custom implementation | Rate limiting, queuing, retry |
| Testing | `pytest` + `pytest-asyncio` + `pytest-cov` | TDD with coverage |
| Linting | `ruff` | Fast Python linter |
| OOP Design | Inheritance (2+ levels), Mixins (one behavior each), Template Method | BaseAgent→DebaterAgent→ProDebaterAgent; TimeoutMixin, LoggingMixin |

---

## 6. Constraints

- **No API keys in submitted code** — `.env.example` contains only placeholders
- **No GUI required** — terminal/SDK layer only (GUI optional)
- **Python only** — no other languages
- **Must run on professor's machine** — installable via `uv sync`
- **No external paid services** beyond the LLM API (professor's key)
- **No hardcoded constants** — all from config or `.env`
- **Max 150 lines per file** — split into modules/mixins/classes/functions/constants
- **Ruff linter must pass with 0 errors**
- **Test coverage must be >= 85%**
- **Version starts at 1.00**

---

## 7. Per-Mechanism PRDs

Each major mechanism has its own dedicated PRD document:

| Document | Mechanism |
|----------|-----------|
| `docs/PRD.md` | This document — overall product requirements |
| `docs/PRD_search_engine.md` | Internet search system (DuckDuckGo integration) |
| `docs/PRD_rag_system.md` | RAG pipeline (vector store, embeddings, retrieval) |
| `docs/PRD_judge_evaluation.md` | Judge scoring system (criteria, penalties, rubric) |
| `docs/PRD_api_gatekeeper.md` | API Gatekeeper (rate limiting, queuing, retry) |
| `docs/PRD_logging_pipeline.md` | FIFO logging (20 files, 500 lines, rotation) |
| `docs/PRD_process_management.md` | Process management (timeouts, watchdog, SIGKILL) |
| `docs/PRD_skills.md` | Skills system (Router-Skill pattern, distinct skill per son) |
| `docs/PRD_context_engineering.md` | Context Engineering (Write/Select strategy, context window management) |
| `docs/PRD_session_management.md` | Session lifecycle, context scoping, message history |

Each per-mechanism PRD contains: mechanism description, functional requirements, interface definition, acceptance criteria, edge cases, and implementation constraints.
