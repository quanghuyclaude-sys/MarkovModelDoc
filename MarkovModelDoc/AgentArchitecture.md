# Agent Architecture — The 4-Stage Pipeline

> Back to: [[SelfImprovingTradingAgent]]
> Source: [MindStudio: Build a 24/7 AI Trading Agent with Claude Code and Alpaca](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca)

---

## Overview

Every cycle runs exactly four stages in sequence. No stage is skipped — even a NO_TRADE cycle still writes a journal entry. That discipline is what makes the self-improvement loop possible.

```
Cycle (every 15–30 min during market hours)
│
├── Stage 1: Market Research
│   └── Fetch price bars, news, RSI, VWAP, positions
│
├── Stage 2: Signal Generation
│   └── Claude reads JSON snapshot → outputs structured decision
│
├── Stage 3: Order Execution
│   └── Code-level guardrails → Alpaca API call if approved
│
└── Stage 4: Trade Journal
    └── Append decision + reasoning + outcome to JSONL / Markdown
```

---

## Three Scheduled Routines

The agent is split into three routines, not one monolithic loop:

| Routine | Schedule (ET) | Purpose |
|---|---|---|
| Morning Research | 9:45 AM, weekdays | Overnight news, set context |
| Trading Session | Every 20 min, 10 AM–3 PM, weekdays | Decision → execution loop |
| End-of-Day Journal | 4:15 PM, weekdays | Reflection, closed-positions summary |

Defined in `.claude/routines.json`:
```json
{
  "routines": [
    { "name": "morning-research",  "schedule": "45 9 * * 1-5",      "timezone": "America/New_York" },
    { "name": "trading-session",   "schedule": "*/20 10-15 * * 1-5", "timezone": "America/New_York" },
    { "name": "eod-journal",       "schedule": "15 16 * * 1-5",      "timezone": "America/New_York" }
  ]
}
```

See [[ClaudeCodeRoutines]] for full scheduling detail.

---

## Stage 1 — Market Research Output Format

Claude never reads raw price feeds. It reads a structured JSON snapshot built by the research module:

```json
{
  "symbol": "NVDA",
  "price": 875.40,
  "change_pct": 1.23,
  "volume": 42310000,
  "rsi_14": 58.2,
  "ma_20": 860.10,
  "ma_50": 840.75,
  "vwap_deviation": 0.17,
  "news": [
    { "headline": "NVIDIA announces H200 GPU allocation increase", "sentiment": "positive" },
    { "headline": "Chip stocks face new export restrictions",      "sentiment": "negative" }
  ],
  "open_position": null,
  "cash_available": 18420.00
}
```

See [[MarketResearchModule]] for the full data fetching implementation.

---

## Stage 2 — Signal Generation Output Format

Claude returns a structured JSON decision. Any non-conforming response is treated as NO_TRADE:

```json
{
  "decision": "BUY",
  "symbol": "NVDA",
  "qty": 5,
  "reasoning": "RSI not overbought at 58. Strong GPU demand catalyst. VWAP deviation modest at 0.17%. Risk/reward favorable.",
  "confidence": "HIGH"
}
```

See [[SignalGeneration-LLM]] for system prompt design and parsing logic.

---

## Stage 3 — Guardrail Validation (Pre-Execution)

Code-level checks run before any order reaches Alpaca:

```python
def validate_order(decision, account_equity, open_positions, current_price):
    if decision["confidence"] == "LOW":
        return False, "Low confidence — rejected"
    allocation = (decision["qty"] * current_price) / account_equity
    if allocation > 0.05:
        return False, "Exceeds 5% position limit"
    if len(open_positions) >= 5:
        return False, "Max concurrent positions reached"
    return True, "Approved"
```

See [[Guardrails-RiskManagement]] for the complete multi-layer safety system.

---

## Stage 4 — Journal Entry (Every Cycle)

```jsonl
{"timestamp":"2026-06-12T10:20:03Z","symbol":"NVDA","decision":"BUY","qty":5,"price":875.40,"reasoning":"RSI not overbought...","confidence":"HIGH","order_id":"abc123"}
{"timestamp":"2026-06-12T10:40:11Z","symbol":"AAPL","decision":"NO_TRADE","reasoning":"RSI at 72 — overbought, waiting for pullback","confidence":"MEDIUM","order_id":null}
```

The journal is the memory of the agent. Without it there is no self-improvement. See [[TradeJournal]] and [[SelfImprovementLoop]].

---

## Component Map

| Component | File | Technology |
|---|---|---|
| Data fetching | [[MarketResearchModule]] | Alpaca Data API, Polygon.io |
| Claude prompt + parsing | [[SignalGeneration-LLM]] | Claude API, CLAUDE.md |
| Guardrails + order submission | [[TradeExecution]] | Alpaca Trading API |
| Logging | [[TradeJournal]] | JSONL + Markdown |
| Scheduling | [[ClaudeCodeRoutines]] | Claude Code Routines |
| Learning loop | [[SelfImprovementLoop]] | Claude re-reads journals |
| Safety | [[Guardrails-RiskManagement]] | Multi-layer rules |
| Infrastructure | [[Deployment]] | Cloud, monitoring, costs |

---

## Sources

- [MindStudio: Build a 24/7 AI Trading Agent with Claude Code and Alpaca](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca)
- [MindStudio: Claude Code Routines](https://www.mindstudio.ai/blog/how-to-build-ai-trading-agent-claude-code-routines)
- [YouTube: How To Build A Self-Improving AI Trading Agent](https://www.youtube.com/watch?v=6njREUQAFdg)
