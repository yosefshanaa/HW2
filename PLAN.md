# PLAN — AI Court Debate Simulator

## 1. Project Structure

```
debate-simulator/
├── src/
│   └── debate_simulator/
│       ├── __init__.py
│       ├── constants.py
│       ├── sdk/
│       │   ├── __init__.py
│       │   └── sdk.py                  # SDK entry point — single entry for ALL logic
│       ├── services/
│       │   ├── __init__.py
│       │   ├── debate_engine.py        # Orchestrates full debate flow
│       │   ├── judge_service.py        # Judge agent logic
│       │   ├── debater_service.py      # Debater agent logic
│       │   └── scoring_service.py      # Final scoring computation
│       ├── shared/
│       │   ├── __init__.py
│       │   ├── gatekeeper.py           # API Gatekeeper (rate limit, queue, retry)
│       │   ├── config.py               # Configuration manager
│       │   ├── version.py              # Version tracking (1.00)
│       │   ├── llm_client.py           # LLM API wrapper
│       │   └── process_manager.py      # Subprocess management, timeouts, watchdog
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base_agent.py           # Abstract base agent class
│       │   ├── judge_agent.py          # Judge (Father) implementation
│       │   └── debater_agent.py        # Debater (Son) implementation
│       ├── skills/
│       │   ├── __init__.py
│       │   ├── base_skill.py           # Skill interface / abstract class
│       │   ├── router_skill.py         # Router — selects skill based on context
│       │   ├── web_search/
│       │   │   ├── __init__.py
│       │   │   ├── skill.md            # Skill description
│       │   │   └── skill.py            # Implementation
│       │   ├── rag_store/
│       │   │   ├── __init__.py
│       │   │   ├── skill.md
│       │   │   └── skill.py
│       │   ├── rag_retrieve/
│       │   │   ├── __init__.py
│       │   │   ├── skill.md
│       │   │   └── skill.py
│       │   ├── fact_check/
│       │   │   ├── __init__.py
│       │   │   ├── skill.md
│       │   │   └── skill.py
│       │   ├── stance_check/
│       │   │   ├── __init__.py
│       │   │   ├── skill.md
│       │   │   └── skill.py
│       │   ├── respect_check/
│       │   │   ├── __init__.py
│       │   │   ├── skill.md
│       │   │   └── skill.py
│       │   ├── rebuttal_check/
│       │   │   ├── __init__.py
│       │   │   ├── skill.md
│       │   │   └── skill.py
│       │   ├── argument_builder/
│       │   │   ├── __init__.py
│       │   │   ├── skill.md
│       │   │   └── skill.py
│       │   └── rebuttal_builder/
│       │       ├── __init__.py
│       │       ├── skill.md
│       │       └── skill.py
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── search/
│       │   │   ├── __init__.py
│       │   │   ├── searcher.py         # DuckDuckGo search abstraction
│       │   │   └── fetcher.py          # URL content fetcher + parser
│       │   ├── rag/
│       │   │   ├── __init__.py
│       │   │   ├── vector_store.py     # ChromaDB wrapper
│       │   │   ├── embedder.py         # Embedding model wrapper
│       │   │   └── chunker.py          # Document chunking utility
│       │   └── logging/
│       │       ├── __init__.py
│       │       ├── fifo_logger.py      # FIFO-based async logger
│       │       ├── rotating_writer.py  # 20-file rotating writer (500 lines each)
│       │       └── log_consumer.py     # Reads from FIFO → dispatches to writer
│       └── models/
│           ├── __init__.py
│           ├── agent.py                # Agent data models (Message, TurnContext, etc.)
│           ├── debate.py               # Debate models (Round, Score, Penalty, etc.)
│           └── config_models.py        # Pydantic config models
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_agents/
│   │   │   ├── __init__.py
│   │   │   ├── test_base_agent.py
│   │   │   ├── test_judge_agent.py
│   │   │   └── test_debater_agent.py
│   │   ├── test_skills/
│   │   │   ├── __init__.py
│   │   │   ├── test_base_skill.py
│   │   │   ├── test_web_search.py
│   │   │   ├── test_rag.py
│   │   │   └── test_check_skills.py
│   │   ├── test_services/
│   │   │   ├── __init__.py
│   │   │   ├── test_debate_engine.py
│   │   │   ├── test_scoring.py
│   │   │   └── test_gatekeeper.py
│   │   ├── test_infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── test_search.py
│   │   │   ├── test_rag_pipeline.py
│   │   │   └── test_logging.py
│   │   └── test_shared/
│   │       ├── __init__.py
│   │       ├── test_config.py
│   │       ├── test_process_manager.py
│   │       └── test_llm_client.py
│   └── integration/
│       ├── __init__.py
│       ├── test_debate_flow.py
│       ├── test_logging_pipeline.py
│       └── test_sdk.py
├── docs/
│   ├── PRD.md                         # This document (symlink or copy)
│   ├── PLAN.md                        # Architecture & Planning
│   ├── TODO.md                         # Task tracking
│   ├── PRD_search_engine.md            # Search mechanism PRD
│   ├── PRD_rag_system.md               # RAG mechanism PRD
│   ├── PRD_judge_evaluation.md         # Judge evaluation PRD
│   ├── PRD_api_gatekeeper.md           # API Gatekeeper PRD
│   ├── PRD_logging_pipeline.md         # Logging pipeline PRD
│   └── PRD_process_management.md       # Process management PRD
├── config/
│   ├── setup.json                     # Main app config (versioned)
│   └── rate_limits.json               # API rate limits (versioned)
├── data/
│   └── topics.json                    # 10 pre-configured debate topics
├── results/                            # JSON debate results
├── assets/                             # Images, diagrams
├── notebooks/                          # Analysis notebooks (sensitivity, results)
├── logs/                               # Rotating log files (20 × 500 lines)
├── .env.example                        # Secret placeholders (committed)
├── .env                                # Actual secrets (git-ignored)
├── .gitignore
├── pyproject.toml                      # Build, lint, test, version
├── uv.lock                             # Locked dependencies
├── README.md                           # MANDATORY — comprehensive docs
└── main.py                             # CLI entry point
```

---

## 2. Architecture — C4 Model

### 2.1 Context Diagram

```
┌──────────────────┐        ┌──────────────────────────┐
│                  │        │                          │
│    Professor     │───────▶│    Debate Simulator SDK   │
│  (Evaluator)     │  CLI   │                          │
│                  │        │  ┌────────────────────┐  │
└──────────────────┘        │  │  Debate Engine     │  │
                            │  │  ┌───┐  ┌───┐     │  │
┌──────────────────┐        │  │  │Judge│  │Son1│    │  │
│                  │  API   │  │  └───┘  └───┘     │  │
│  OpenAI API      │◀───────│  │       ┌───┐         │  │
│  (LLM Provider)  │        │  │       │Son2│         │  │
│                  │        │  │       └───┘         │  │
└──────────────────┘        │  └────────────────────┘  │
                            │                          │
┌──────────────────┐        │  ┌────────────────────┐  │
│                  │ Search │  │  Infrastructure     │  │
│  DuckDuckGo      │◀───────│  │  Search | RAG | Log │  │
│  (Search Engine) │        │  └────────────────────┘  │
└──────────────────┘        └──────────────────────────┘
```

### 2.2 Container Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI (main.py)                            │
│                     argparse + rich output                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SDK Layer (sdk.py)                            │
│              Single entry point for ALL logic                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐
│ Domain Services │ │   Models     │ │ Shared Utilities │
│                 │ │              │ │                  │
│ • DebateEngine  │ │ • Agent      │ │ • Gatekeeper     │
│ • JudgeService  │ │ • Debate     │ │ • Config         │
│ • DebaterSvc    │ │ • Score      │ │ • Version (1.00) │
│ • ScoringService│ │ • Penalty    │ │ • LLMClient      │
│                 │ │ • Config     │ │ • ProcessMgr     │
└────────┬────────┘ └──────────────┘ └──────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Agents │ │ Skills │
│        │ │        │
│ Judge  │ │ Router │
│ Son1   │ │ Search │
│ Son2   │ │ RAG    │
└────────┘ │ Checks │
           │ Build  │
           └────────┘
              │
              ▼
┌──────────────────────────────────────┐
│          Infrastructure              │
│                                      │
│  ┌────────┐ ┌─────┐ ┌────────────┐  │
│  │ Search │ │ RAG │ │  Logging   │  │
│  │ DDG    │ │Chroma│ │ FIFO→20f  │  │
│  └────────┘ └─────┘ └────────────┘  │
└──────────────────────────────────────┘
```

### 2.3 Component Diagram — Agent Communication (IPC)

```
┌──────────────────┐     JSON/FIFO     ┌──────────────────┐
│   Pro Agent      │───────────────────▶│                  │
│   (Son 1)        │                    │   Judge Agent    │
│   Process 1      │                    │   (Father)       │
└──────────────────┘                    │   Process 3      │
                                        │                  │
┌──────────────────┐     JSON/FIFO     │  [Listens only]  │
│   Con Agent      │───────────────────▶│  [No reply]      │
│   (Son 2)        │                    │                  │
│   Process 2      │                    │                  │
└──────────────────┘                    └────────┬─────────┘
         ▲                                       │
         │              JSON/FIFO                │
         └───────────────────────────────────────┘
         [Pro ↔ Con alternate each ping]
         [Judge only receives from both]
```

### 2.4 Code Diagram — Key Classes

```
BaseAgent (ABC)
├── JudgeAgent
│   ├── skills: [fact_check, stance_check, respect_check, rebuttal_check]
│   └── methods: evaluate_round(), score_debate(), declare_winner()
└── DebaterAgent
    ├── skills: [web_search, rag_store, rag_retrieve, argument_builder, rebuttal_builder]
    └── methods: research(), build_argument(), build_rebuttal()

BaseSkill (ABC)
├── RouterSkill
├── WebSearchSkill
├── RAGStoreSkill
├── RAGRetrieveSkill
├── FactCheckSkill
├── StanceCheckSkill
├── RespectCheckSkill
├── RebuttalCheckSkill
├── ArgumentBuilderSkill
└── RebuttalBuilderSkill

ApiGatekeeper
├── execute(api_call, *args, **kwargs)
├── _check_rate_limit()
├── _enqueue_if_needed()
├── _retry_on_failure()
└── get_queue_status()

DebateEngine
├── initialize_agents()
├── run_research_phase()
├── run_debate_pings()
├── run_final_scoring()
└── export_results()

ProcessManager
├── spawn_agent(agent)
├── enforce_timeout(task, timeout)
├── watchdog_ping(process)
└── kill_agent(process)

RotatingWriter
├── write(entry)
├── _rotate_if_needed()
└── _get_active_file()
```

---

## 3. Architecture Decision Records (ADRs)

### ADR-001: SDK-Based Architecture
- **Decision**: All business logic accessible through a single SDK entry point
- **Context**: Professor requires SDK as primary interface for AI agent interaction
- **Trade-offs**: +Clean separation, +testability, +extensibility; -more boilerplate
- **Alternatives considered**: Direct CLI coupling, monolithic script

### ADR-002: Multiprocessing for Agents
- **Decision**: Each agent runs as a separate process (not thread)
- **Context**: Agents need hard process boundaries for timeout/SIGKILL
- **Trade-offs**: +true isolation, +SIGKILL works; -higher memory, -IPC overhead
- **Alternatives considered**: asyncio threads (can't SIGKILL), single process

### ADR-003: FIFO for IPC and Logging
- **Decision**: Use named pipes (FIFO) for both agent communication and logging
- **Context**: Professor requires FIFO-based logging with 20 files × 500 lines
- **Trade-offs**: +async, +decoupled; -platform-dependent, -buffer management
- **Alternatives considered**: queues (in-process only), sockets (overkill)

### ADR-004: ChromaDB for RAG
- **Decision**: Use ChromaDB as local vector store
- **Context**: No external services allowed, must run locally
- **Trade-offs**: +easy setup, +local, +no API key; -limited scale
- **Alternatives considered**: FAISS (no metadata), Weaviate (external service)

### ADR-005: DuckDuckGo for Search
- **Decision**: Use DuckDuckGo search (free, no API key)
- **Context**: Must not require additional API keys beyond LLM
- **Trade-offs**: +free, +no key; -may be rate-limited, -less precise than Google
- **Alternatives considered**: Google Search API (needs key), Bing (needs key)

### ADR-006: UV as Package Manager
- **Decision**: Use UV for dependency management
- **Context**: Professor explicitly requires UV, not pip
- **Trade-offs**: +fast, +modern, +lock file; -newer tool, less familiar
- **Alternatives considered**: pip (disallowed), poetry (heavier)

### ADR-007: OOP with Inheritance + Mixins
- **Decision**: Use OOP where appropriate — not strictly, use mixins for shared behavior
- **Context**: Professor allows but doesn't mandate strict OOP
- **Trade-offs**: +reusability via mixins, +clear hierarchy; -complexity
- **Alternatives considered**: Pure functions, strict OOP everywhere

### ADR-008: JSON as Communication Protocol
- **Decision**: All IPC between agents uses JSON (JSONL for streaming)
- **Context**: Professor requires JSON as the communication medium
- **Trade-offs**: +structured, +parseable, +loggable; -verbose
- **Alternatives considered**: pickle (security risk), plain text (unstructured)

---

## 4. Detailed Module Design

### 4.1 `sdk/sdk.py` — SDK Entry Point

```
Responsibilities:
- Single entry point for ALL debate logic
- Expose: start_debate(topic, config), list_topics(), get_results()
- No business logic — delegates to services
- CLI consumes this SDK (not the other way around)
```

### 4.2 `agents/base_agent.py` — Base Agent

```
Responsibilities:
- Define the Agent interface (ABC)
- Manage LLM client connection (via shared/llm_client.py)
- Manage skill registry (RouterSkill pattern)
- Handle prompt construction (Context Engineering)
- Track memory / conversation history
- Enforce response limits (lines, tokens)

Key Design:
- System prompts loaded from skill.md files
- use_skill(name, **kwargs) method
- Each agent runs in its own process via ProcessManager
```

### 4.3 `agents/judge_agent.py`

```
System prompt responsibilities:
- Judge is debate technique evaluator (NOT domain expert)
- Use research-backed evaluation criteria
- Define scoring rubric (5 dimensions, weighted)
- Define penalty triggers and severity
- Judge does NOT intervene in debate — only listens

Initialization:
1. Search internet for "competitive debate judging criteria"
2. Search for "debate tournament scoring rubric"
3. Build evaluation prompt from gathered criteria
4. Load judge-specific skills

Per-round: observe + take notes (no intervention)
Final: score each debater on 5 dimensions, apply penalties, declare winner/tie
```

### 4.4 `agents/debater_agent.py`

```
System prompt responsibilities:
- Define the assigned stance (Pro or Con) — randomly assigned
- Must reply to opponent's last point
- Respectful tone, politically correct
- Evidence-based argumentation
- Use research materials from RAG

Research phase: search → fetch → chunk → embed → store → summarize
Per-round: retrieve RAG → build argument/rebuttal → validate limits
```

### 4.5 `shared/gatekeeper.py` — API Gatekeeper

```
Responsibilities:
- Centralized execution of ALL external API calls
- Rate limiting: requests_per_minute, requests_per_hour, concurrent_max
- FIFO queue when rate limit reached
- Retry with exponential backoff on transient failures
- Log every API call
- Queue status monitoring
- No hardcoded credentials

Implementation:
- Thread-safe with queue.Queue
- Config from config/rate_limits.json
- Backpressure mechanism when queue is full
```

### 4.6 `shared/process_manager.py`

```
Responsibilities:
- Spawn each agent as a separate process (multiprocessing)
- Enforce per-turn timeout (asyncio.wait_for)
- Watchdog: periodic keep-alive pings to detect stuck processes
- On timeout: SIGKILL the process, log event, record penalty
- Track cumulative penalties per agent
```

### 4.7 `skills/` Module — Router-Skill Pattern

```
RouterSkill:
1. Reads all skill.md descriptions in the skills/ directory
2. Adds skill descriptions to the System Prompt context
3. Based on the user's current need, selects the appropriate skill
4. Minimizes token usage by only loading relevant skill descriptions

Each skill directory contains:
- skill.md: Description file (what it does, when to use it)
- skill.py: Implementation (no side-effect imports)
- __init__.py: Package marker (with __all__ export)
```

### 4.8 `infrastructure/logging/` Module

```
fifo_logger.py:
- Creates named pipe (FIFO) at configured path
- Provides log(level, agent, message) method
- Non-blocking writes to FIFO

log_consumer.py:
- Background thread reading from FIFO
- Formats: [ISO8601] [LEVEL] [AGENT] message
- Dispatches to RotatingWriter

rotating_writer.py:
- 20 files, max 500 lines each
- Circular: when file 20 is full, file 1 is overwritten
- Thread-safe writes
- File naming: log_001.log through log_020.log
```

---

## 5. Configuration Design

### `config/setup.json`

```json
{
  "version": "1.00",
  "llm": {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 1024,
    "api_key_env": "OPENAI_API_KEY"
  },
  "debate": {
    "max_pings": 10,
    "agent_timeout_seconds": 60,
    "keepalive_interval_seconds": 10,
    "max_lines_per_response": 50,
    "max_tokens_per_response": 1024,
    "research_timeout_seconds": 120
  },
  "search": {
    "engine": "duckduckgo",
    "max_results_per_query": 5,
    "max_research_queries": 10
  },
  "rag": {
    "embedding_model": "all-MiniLM-L6-v2",
    "chunk_size": 500,
    "chunk_overlap": 50,
    "top_k_retrieval": 5,
    "persist_directory": ".rag_store"
  },
  "logging": {
    "fifo_path": "logs/debate_fifo",
    "max_files": 20,
    "max_lines_per_file": 500,
    "log_level": "INFO"
  },
  "penalties": {
    "disrespect": 5,
    "ignore_rebuttal": 10,
    "stance_contradiction": 15,
    "exceed_lines": 5,
    "exceed_time": 10
  },
  "scoring": {
    "weights": {
      "argument_strength": 0.25,
      "rebuttal_effectiveness": 0.25,
      "evidence_research": 0.20,
      "rhetorical_quality": 0.15,
      "compliance": 0.15
    }
  }
}
```

### `config/rate_limits.json`

```json
{
  "version": "1.00",
  "rate_limits": {
    "openai": {
      "requests_per_minute": 30,
      "requests_per_hour": 500,
      "concurrent_max": 5,
      "retry_after_seconds": 30,
      "max_retries": 3
    },
    "search": {
      "requests_per_minute": 10,
      "requests_per_hour": 100,
      "concurrent_max": 2,
      "retry_after_seconds": 60,
      "max_retries": 2
    },
    "default": {
      "requests_per_minute": 20,
      "requests_per_hour": 300,
      "concurrent_max": 3,
      "retry_after_seconds": 30,
      "max_retries": 3
    }
  }
}
```

### `.env.example`

```env
OPENAI_API_KEY=your_api_key_here
```

### `pyproject.toml` (key sections)

```toml
[project]
name = "debate-simulator"
version = "1.00"
requires-python = ">=3.10"

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]
ignore = ["E501"]

[tool.coverage.run]
source = ["src"]
omit = ["src/debate_simulator/__main__.py", "*/tests/*"]

[tool.coverage.report]
fail_under = 85
```

---

## 6. Development Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1: Foundation** | Day 1 | UV init, pyproject.toml, project structure, config system, version.py |
| **Phase 2: Logging Pipeline** | Day 1-2 | FIFO logger, rotating writer, log consumer (PyPI package) |
| **Phase 3: API Gatekeeper** | Day 2 | Rate limiting, queuing, retry, logging |
| **Phase 4: Search & RAG** | Day 2-3 | DuckDuckGo search, ChromaDB, embedder, chunker |
| **Phase 5: Skills Framework** | Day 3-4 | BaseSkill, RouterSkill, all skill implementations |
| **Phase 6: Agent System** | Day 4-5 | BaseAgent, JudgeAgent, DebaterAgent, system prompts |
| **Phase 7: SDK + Services** | Day 5-6 | SDK entry point, DebateEngine, ScoringService |
| **Phase 8: Process Management** | Day 6 | ProcessManager, watchdog, timeouts, SIGKILL |
| **Phase 9: Integration** | Day 6-7 | End-to-end flow, IPC, JSON output, CLI |
| **Phase 10: Testing (TDD)** | Day 7-9 | Unit + integration tests, 85% coverage, edge cases |
| **Phase 11: Documentation** | Day 9-10 | Per-mechanism PRDs, prompt logs, README, diagrams |
| **Phase 12: Final Review** | Day 10 | Ruff 0 errors, non-determinism test, cost table, submission |

---

## 7. Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| LLM API rate limits | Medium | High | API Gatekeeper with queuing + backoff |
| Search engine blocks | Low | Medium | DuckDuckGo lenient; fallback to cached results |
| Agent stuck in loop | Medium | High | Watchdog + timeout + SIGKILL |
| Judge biased scores | Low | Medium | Structured rubric, research-backed criteria |
| ChromaDB compatibility | Low | Medium | Pin versions in uv.lock, test early |
| Token limit exceeded | Medium | Low | Truncation + configurable limits |
| FIFO pipe issues | Medium | Medium | Graceful fallback to file logging |
| UV compatibility | Low | Medium | UV is well-supported on Python 3.10+ |
