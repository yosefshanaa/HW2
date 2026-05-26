# PRD Session Management

## Purpose
Treat each debate run as a single time-bounded **session** with scoped context and a clear
lifecycle, so state does not leak between debates and context stays bounded per run.

## Background
A session is one conversation that lives until it is reset; while it runs, context only grows.
Scoping research, history, and any vector-store data to the session keeps runs independent and
reproducible-to-export, and lets the per-session context window be managed deliberately
(see [PRD_context_engineering.md](PRD_context_engineering.md)).

## Lifecycle
1. **INIT** — agents are constructed and system prompts loaded (`initialize_agents`).
2. **RESEARCH** — agents search the internet and populate session-scoped notes/stores
   (`run_research_phase`).
3. **DEBATE** — the configured number of pings are exchanged; each round is appended to the
   session history (`run_debate_pings`).
4. **SCORING** — the Judge reviews the full session transcript and assigns final scores
   (`run_final_scoring`).
5. **FINISHED** — the result is exported to JSON; session-scoped data is no longer reused
   (`export_result`).

## Requirements
- One session per `start_debate` call; agents and history are owned by the engine instance.
- Round history accumulates within the session and is passed forward as scoped context.
- Research data is gathered per session, not shared across debates.
- The final export is a self-contained JSON record of the session (id, timestamp, rounds,
  scores, winner).
- The number of pings and limits are read from `config/setup.json`, not hardcoded.

## Interface
- `DebateEngine.start_debate(topic, config) -> DebateResult` — drives the full lifecycle.
- `DebateEngine.run_research_phase(topic)` / `run_debate_pings(...)` / `run_final_scoring()`.
- `export_result(result, results_path)` — persists the finished session.

## Acceptance
- A completed session exports a valid `DebateResult` JSON with a decisive winner.
- Round count in the exported record equals the configured pings.
- A fresh engine run does not reuse the previous session's history or scores.
- Lifecycle phases run in order: research → pings → scoring → export.
