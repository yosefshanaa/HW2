# PRD Context Engineering

## Purpose
Manage the LLM context window deliberately (Context Engineering), not just by crafting a
single prompt (Prompt Engineering). The goal is to keep only the information that is relevant
*right now* inside the window, holding everything else outside it, to control token cost and
keep agents focused — the central theme of the course lecture.

## Background
Transformers carry no memory between calls: the whole context is re-supplied every turn. Two
complementary strategies bound what enters the window:
- **Write** — extract/condense external information and keep the distilled version, discarding
  the raw source once summarized.
- **Select** — keep large material on the side (disk / vector store) and pull only the pieces
  needed for the current step.

## Requirements
- **Write (Judge):** at initialization the Judge searches the internet for debate-judging
  criteria and works from a condensed rubric, rather than carrying raw search dumps in every
  scoring call.
- **Select (Debaters):** during rounds, retrieval returns only the top-k relevant chunks from
  the RAG store; the remainder stays out of the window.
- **Router-Skill minimalism:** only the relevant skill description is loaded into the system
  prompt (see [PRD_skills.md](PRD_skills.md)), not every skill's description.
- Per-round prompts include only the necessary slices — topic, round number, research notes,
  the opponent's last speech, and prior judge feedback — never the full raw transcript.
- All context-shaping parameters (top-k, result counts) come from `config/setup.json`.

## Interface
- `DebaterAgent.research(topic)` — Write: gathers and condenses research notes.
- `RagRetrieveSkill.execute({"query", "top_k"})` — Select: returns top-k chunks only.
- `RouterSkill.select(query)` — loads only the relevant skill into context.

## Acceptance
- Retrieval returns at most `top_k` chunks and leaves the rest in the store.
- Debater prompts are assembled from scoped fields, not the entire history blob.
- The Router selects a single relevant skill rather than concatenating all descriptions.
- Token-shaping values are read from config, with zero hardcoded limits.
