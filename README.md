# AI Court Debate Simulator

A terminal-based Python SDK application that simulates structured debates between two AI agents (Pro / Con) on a given topic, moderated and scored by a third AI agent acting as a **Judge**. The judge is **not a domain expert** — he evaluates based on **argumentation quality, rebuttal effectiveness, evidence use, and rhetorical technique**.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Debate Topics](#debate-topics)
- [Scoring System](#scoring-system)
- [Results & Output](#results--output)
- [Skills System](#skills-system)
- [Development](#development)
- [Testing](#testing)
- [License & Credits](#license--credits)

---

## Installation

### Prerequisites

- Python 3.10+
- [UV](https://github.com/astral-sh/uv) package manager
- An OpenAI API key (professor will supply via `.env`)

### Steps

```bash
# Clone the repository
git clone https://github.com/yosefshanaa/HW2.git
cd HW2

# Install dependencies (UV handles everything)
uv sync

# Configure your API key
cp .env.example .env
# Edit .env and add your API key
```

> **Note**: Never commit your real API key. `.env` is git-ignored.

---

## Quick Start

```bash
# Run a debate on a pre-configured topic
uv run python main.py --list-topics

# Run a debate on a specific topic by number
uv run python main.py --topic 1

# Run a debate with a custom topic
uv run python main.py --custom-topic "Should AI replace most jobs by 2050?"

# Run with custom number of pings
uv run python main.py --topic 1 --pings 5
```

### What You'll See

<!-- TODO: Add screenshots of terminal output here after first successful run -->

```
╭──────────────────────────────────────────────────────────────╮
│  🔔 AI Court Debate Simulator                              │
│                                                              │
│  Topic: Barcelona vs Real Madrid — greatest football club      │
│  Con Agent ████████████████████████░░░░░ Pro Agent               │
│  Judge   ████████████████████████░░░░░  (observing)           │
│                                                              │
│  Ping 1/10  ████████████████████████████████████░░░░░░░  ✓    │
│  Ping 2/10  ████████████████████████████████████░░░░░░░  ✓    │
│  ...                                                         │
│  Ping 10/10 ████████████████████████████████████░░░░░░░  ✓    │
│                                                              │
│  ═══════════════════════════════════════════════════════════  │
│  FINAL SCORES                                                │
│  Pro Agent:  ████████████████████████░░ 78%                        │
│  Con Agent:  ████████████████████████░░ 72%                        │
│  Winner: Pro Agent                                           │
│ ═══════════════════════════════════════════════════════════  │
╰──────────────────────────────────────────────────────────────╯
```

<!-- TODO: Replace with actual screenshot -->

---

## CLI Usage

```
usage: main.py [-h] [--topic TOPIC] [--custom-topic TEXT] [--pings PINGS]
               [--config CONFIG] [--list-topics] [--log-level LEVEL]

Options:
  -h, --help            Show help message and exit
  --topic TOPIC         Topic number from the pre-configured list (1-10)
  --custom-topic TEXT    Custom debate topic (auto-detects Pro/Con framing)
  --pings PINGS         Number of debate pings (default: 10)
  --config CONFIG       Path to config file (default: config/setup.json)
  --list-topics        List all available debate topics
  --log-level LEVEL     Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
```

### Examples

```bash
# List all topics
uv run python main.py --list-topics

# Specific topic with default 10 pings
uv run python main.py --topic 3

# Custom topic with 5 pings
uv run python main.py --custom-topic "Nuclear energy is the solution to climate change" --pings 5

# Debug mode with verbose logging
uv run python main.py --topic 1 --log-level DEBUG
```

---

## Architecture

### SDK-Based Design

```
CLI (main.py)
       │
       ▼
┌─────────┐
│   SDK   │  ← Single entry point for ALL logic
└────┬────┘
       │
       ▼
┌─────────────┐
│  Domain      │  ← DebateEngine, JudgeService, ScoringService
│  Services    │
└────┬────────┘
       │
       ▼
┌──────────────┐
│ Infrastructure│  ← Search, RAG, Logging, Gatekeeper, LLM Client
└──────────────┘
```

### Agent Communication (IPC)

- Each agent runs as a **separate process**
- Agents communicate via **FIFO (named pipes)** using **JSON** protocol
- Communication is **one-directional**: Sons → Father (judge only listens, never intervenes)
- **Con speaks first** in each ping, then Pro responds

### C4 Model

| Level | Description |
|-------|-------------|
| **Context** | Professor → CLI → SDK → OpenAI API + DuckDuckGo |
| **Container** | SDK → Domain Services → Infrastructure |
| **Component** | Agents (3 processes) communicating via FIFO pipes |
| **Code** | Classes: BaseAgent → DebaterAgent → ProDebaterAgent/ConDebaterAgent |

For full diagrams see [PLAN.md](docs/PLAN.md).

---

## Configuration

### `.env` (git-ignored — professor provides the API key)

```env
OPENAI_API_KEY=your_api_key_here
```

### `config/setup.json` (versioned)

All configurable parameters — **no hardcoded constants**:

| Parameter | Default | Location |
|-----------|---------|----------|
| `llm.model` | `gpt-4o-mini` | config/setup.json |
| `llm.temperature` | `0.7` | config/setup.json |
| `debate.max_pings` | `10` | config/setup.json |
| `debate.agent_timeout_seconds` | `60` | config/setup.json |
| `debate.keepalive_interval_seconds` | `10` | config/setup.json |
| `search.engine` | `duckduckgo` | config/setup.json |
| `logging.max_files` | `20` | config/setup.json |
| `logging.max_lines_per_file` | `500` | config/setup.json |
| `scoring.weights.*` | See config | config/setup.json |
| `penalties.*` | See config | config/setup.json |

### `config/rate_limits.json` (versioned)

| Service | Requests/Min | Requests/Hour | Max Concurrent |
|---------|-------------|--------------|-----------------|
| `openai` | 30 | 500 | 5 |
| `search` | 10 | 100 | 2 |
| `default` | 20 | 300 | 3 |

---

## Project Structure

```
debate-simulator/
├── src/debate_simulator/        # Main package
│   ├── sdk/                     # SDK entry point
│   ├── services/                # Business logic
│   ├── shared/                  # Gatekeeper, config, version, LLM client
│   ├── agents/                  # BaseAgent → JudgeAgent, DebaterAgent
│   ├── skills/                  # Router-Skill pattern (project-local)
│   ├── infrastructure/           # Search, RAG, Logging
│   └── models/                  # Pydantic data models
├── tests/                       # Unit + Integration tests (mirror src/ structure)
├── docs/                        # PRD, PLAN, TODO, per-mechanism PRDs
├── config/                      # setup.json, rate_limits.json
├── data/                        # topics.json
├── results/                     # JSON debate results
├── logs/                        # 20 rotating log files × 500 lines each
├── notebooks/                   # Results analysis & visualization
├── .env.example                 # API key placeholder
├── pyproject.toml               # Build, lint, test, version
├── uv.lock                      # Locked dependencies
└── README.md                   # This file
```

---

## Debate Topics

| # | Category | Topic |
|---|----------|-------|
| 1 | Sports | Barcelona vs Real Madrid — greatest football club |
| 2 | Sports | Individual sports build character better than team sports |
| 3 | Science | AI will replace most jobs by 2050 |
| 4 | Science | Nuclear energy is the solution to climate change |
| 5 | History | The British Empire did more good than harm |
| 6 | History | Ancient Rome's collapse was inevitable |
| 7 | Current Affairs | Universal Basic Income should be implemented globally |
| 8 | Current Affairs | Social media does more harm than good to democracy |
| 9 | Culture | Art should never be censored |
| 10 | Culture | Remote work weakens company culture |

Custom topics are supported via `--custom-topic` flag.

---

## Scoring System

The judge evaluates each debater on 5 weighted dimensions (0-100% each):

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Argument Strength** | 25% | Logical coherence, evidence quality, persuasiveness |
| **Rebuttal Effectiveness** | 25% | How well the debater addressed the opponent's point |
| **Evidence & Research** | 20% | Use of factual data, statistics, credible sources |
| **Rhetorical Quality** | 15% | Clarity, structure, persuasion technique |
| **Compliance** | 15% | Respect, relevance, no contradiction with own stance |

**Penalties** (deducted from final score):

| Violation | Penalty |
|-----------|---------|
| Disrespectful language | -5% per occurrence |
| Ignoring opponent's point | -10% per occurrence |
| Contradicting own stance | -15% per occurrence |
| Exceeding line limit | -5% per occurrence |
| Exceeding time limit | -10% per occurrence |

**Ties are valid** — the judge may declare a tie if both debaters perform equally well.

### Example JSON Output

```json
{
  "topic": "Barcelona vs Real Madrid",
  "pings": [ ... ],
  "final_scores": {
    "pro": { "total": 78, "argument_strength": 82, "rebuttal": 75, "evidence": 80, "rhetoric": 76, "compliance": 90, "penalties": -12 },
    "con": { "total": 72, "argument_strength": 70, "rebuttal": 78, "evidence": 68, "rhetoric": 74, "compliance": 85, "penalties": -8 }
  },
  "winner": "pro"
}
```

---

## Skills System

Each agent has **project-local skills** (not global). The **RouterSkill** reads `skill.md` files and selects the appropriate skill based on context.

| Skill | Owner | Description |
|-------|-------|-------------|
| `web_search` | All agents | Search the internet for information |
| `rag_store` | All agents | Store fetched content into vector store |
| `rag_retrieve` | All agents | Retrieve relevant context from vector store |
| `fact_check` | Judge | Verify claims made by debaters |
| `stance_check` | Judge | Detect stance contradiction |
| `respect_check` | Judge | Detect disrespectful language |
| `rebuttal_check` | Judge | Detect ignored rebuttals |
| `argument_builder` | Debaters | Construct structured arguments with evidence |
| `rebuttal_builder` | Debaters | Construct targeted rebuttals |

Skills follow the **Router-Skill pattern**: read all descriptions → select relevant one → execute. Each skill directory contains `skill.md` (description) + `skill.py` (implementation).

---

## Development

### Setup

```bash
uv sync                    # Install dependencies
uv run pytest --cov           # Run tests with coverage
uv run ruff check          # Linter check
uv run ruff format         # Auto-format code
```

### TDD Workflow

Every feature follows **RED → GREEN → REFACTOR**:
1. Write failing test (RED)
2. Implement minimum code to pass (GREEN)
3. Clean up (REFACTOR)

### Code Quality

| Standard | Requirement |
|----------|-------------|
| Max file length | **150 lines** per file |
| Linter | **Ruff** — 0 errors |
| Coverage | **≥ 85%** (statement + branch) |
| Comments | "Why" not "what" |
| Docstrings | All public functions/classes |
| Type hints | All public functions |
| Constants | From config/env only — zero hardcoded values |

### Project Standards

| Standard | Implementation |
|----------|---------------|
| Architecture | SDK-based (3 layers: SDK → Domain Services → Infrastructure) |
| Design Patterns | Template Method, Router-Skill, Mixins (one behavior each) |
| Inheritance | 2+ levels: `BaseAgent → DebaterAgent → ProDebaterAgent` |
| IPC | JSON over FIFO named pipes between processes |
| Concurrency | Multiprocessing for agents, multithreading for I/O (gatekeeper) |
| Package Manager | **UV** (not pip) |
| Version | Starts at **1.00** in all versioned files |
| Config | JSON files (config/) + .env for secrets |
| Logging | FIFO → 20 rotating files × 500 lines |
| Tests | Mirror src/ structure in tests/ (unit/ + integration/) |

### Commit Conventions

- Conventional Commits format: `type(scope): message`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Feature branches for each development phase
- Meaningful messages — explain what and why

---

## Testing

### Running Tests

```bash
# All tests with coverage
uv run pytest --cov --cov-report=term-missing

# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# Specific module
uv run pytest tests/unit/test_skills/ -v
```

### Coverage

Minimum **85%** coverage (statement + branch). Configure in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*"]

[tool.coverage.report]
fail_under = 85
```

---

## License & Credits

This project was developed as an academic exercise for the course by Dr. Yoram Segal.

### References

- [OpenAI API Guidelines](https://platform.openai.com/docs/guidelines)
- [Google Engineering Practices](https://google.github.io/eng-practices/)
- [ISO/IEC 25010 Quality Model](https://www.iso.org/standard/35733.html)
- [Nielsen's 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [MIT Software Quality Assurance Plan](https://acisweb.mit.edu/acis/sqap/sqap.r1.html)

### Credits

- **Developed by**: Yosef Shanaa
- **Course**: Dr. Yoram Segal — Agents, Subagents, Commands and Skills
- **Framework**: Python, OpenAI API, DuckDuckGo Search, ChromaDB, Sentence-Transformers
- **Package Manager**: UV
