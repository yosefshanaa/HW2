# Token And Cost Tracking

## How it works
Token usage is captured from every OpenAI response: `LlmClient._record_usage()` reads
`response.usage` (prompt/completion tokens) on each call routed through the API gatekeeper and
accumulates running totals. `LlmClient.usage_summary()` derives the dollar cost from per-million
prices defined in `config/setup.json` (`llm.prompt_price_per_million`,
`llm.completion_price_per_million`) — no hardcoded prices. The totals are written into every
exported result under `DebateResult.token_usage`.

## Pricing (config-driven)
| Model | Input ($/1M tokens) | Output ($/1M tokens) | Source |
|-------|--------------------:|---------------------:|--------|
| `gpt-4o-mini` | 0.15 | 0.60 | `config/setup.json` → `llm.*_price_per_million` |

## Measured run — full default debate (10 pings, `gpt-4o-mini`)
Captured from a live `uv run python main.py --topic 1` run (`results/*.json` → `token_usage`):

| Metric | Value |
|--------|------:|
| Prompt (input) tokens | 25,657 |
| Completion (output) tokens | 2,312 |
| Input cost | 25,657 / 1e6 × $0.15 = $0.003849 |
| Output cost | 2,312 / 1e6 × $0.60 = $0.001387 |
| **Total cost per 10-ping debate** | **≈ $0.0052** |

A budget smoke test (`--pings 1`) measured ≈ 1,307 input + 204 output tokens ≈ $0.0003,
confirming cost scales roughly linearly with the number of pings.

## Scaling
Input tokens dominate (~92% of spend) because each turn re-sends the accumulating debate
history and research notes — the cost of context. At ≈ $0.0052 per default debate:

| Debates | Approx. cost |
|--------:|-------------:|
| 1 | $0.005 |
| 100 | $0.52 |
| 1,000 | $5.24 |

**Optimization levers already in the design:** the API gatekeeper caps request rate (bounding
spend); Context Engineering (Write/Select, see `PRD_context_engineering.md`) keeps only relevant
context in the window; and `--pings` can be lowered for budget-limited runs. Switching
`llm.model` (and its prices) in config immediately re-scopes the cost estimate above.
