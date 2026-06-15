# Claude Code Routines — Scheduling the Agent

> Back to: [[SelfImprovingTradingAgent]]
> Source: [MindStudio: How to Build a 24/7 AI Trading Agent with Claude Code Routines](https://www.mindstudio.ai/blog/how-to-build-ai-trading-agent-claude-code-routines)

---

## What Are Claude Code Routines?

Routines are Claude Code's built-in mechanism for running agent workflows on a repeating schedule — no external cron daemon, no AWS EventBridge, no pm2 required. You define the schedule in a JSON config file and Claude Code handles the rest.

Each routine fires a prompt to Claude at the specified time. Claude then has access to all its tools (file reads, shell commands, API calls) to complete the task autonomously.

---

## Routines Config File

Location: `.claude/routines.json` in your project root.

```json
{
  "routines": [
    {
      "name": "morning-research",
      "description": "Fetch overnight news and set market context before trading opens",
      "schedule": "45 9 * * 1-5",
      "timezone": "America/New_York",
      "prompt": "Run morning market research. Fetch latest news for each symbol in the watchlist. Summarize overnight developments. Write findings to morning-brief.md."
    },
    {
      "name": "trading-session",
      "description": "Core decision-execution loop during market hours",
      "schedule": "*/20 10-15 * * 1-5",
      "timezone": "America/New_York",
      "prompt": "Run one trading cycle: research all watchlist symbols, generate trading decisions, validate against risk rules, execute approved orders, write journal entry."
    },
    {
      "name": "eod-journal",
      "description": "End-of-day reflection and performance logging",
      "schedule": "15 16 * * 1-5",
      "timezone": "America/New_York",
      "prompt": "Run end-of-day routine. Fetch closed positions and P&L. Write daily journal summary. Identify any patterns or systematic errors from today's decisions."
    },
    {
      "name": "weekly-reflection",
      "description": "Self-improvement loop — reads past week of journals",
      "schedule": "0 17 * * 5",
      "timezone": "America/New_York",
      "prompt": "Read the last 5 days of trade journals. Identify systematic patterns, mistakes, and opportunities. Propose updates to CLAUDE.md rules. Write a weekly performance report."
    }
  ]
}
```

---

## Cron Expression Reference

```
┌─────────── minute (0–59)
│ ┌───────── hour (0–23)
│ │ ┌─────── day of month (1–31)
│ │ │ ┌───── month (1–12)
│ │ │ │ ┌─── day of week (0=Sun, 1=Mon … 5=Fri, 6=Sat)
│ │ │ │ │
* * * * *

Examples:
*/20 10-15 * * 1-5   → every 20 min, 10 AM–3 PM, Mon–Fri
45 9 * * 1-5         → 9:45 AM every weekday
15 16 * * 1-5        → 4:15 PM every weekday
0 17 * * 5           → 5:00 PM every Friday
```

---

## Market Hours Awareness

Always check market status before executing — even if the routine fires, the market may be closed (holidays, early close):

```python
import requests

def is_market_open() -> bool:
    resp = requests.get(
        "https://api.alpaca.markets/v2/clock",
        headers={"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": API_SECRET}
    )
    return resp.json()["is_open"]

# In the trading routine prompt, instruct Claude:
# "First call is_market_open(). If False, log 'Market closed' and exit."
```

---

## Routine Prompt Design Principles

The prompt is what Claude reads when the routine fires. It must be self-contained — Claude has no memory of the previous cycle.

**Good routine prompt:**
```
Run one trading cycle for the watchlist defined in watchlist.json.

Steps (in order):
1. Call get_market_snapshot() for each symbol
2. For each symbol, call claude_decide(snapshot) to get a decision
3. For each BUY/SELL decision, call validate_and_execute(decision)
4. Append one JSONL entry to journals/YYYY-MM-DD.jsonl for every decision
5. If any order was filled, send a notification via heartbeat.json

Do not trade if market is closed. Do not exceed 5% allocation per position.
```

**Bad routine prompt:**
```
Trade stocks and make money
```

---

## CLAUDE.md — The Agent's Standing Instructions

`CLAUDE.md` in your project root is read by Claude at the start of every routine. It contains the agent's persistent rules:

```markdown
# Trading Agent Rules

## Risk Rules (NEVER violate these)
- Never invest more than 5% of portfolio in a single position
- Never place market orders — always limit orders within 0.2% of ask
- Close any position that drops 8% from entry immediately
- Keep at least 20% cash reserve at all times
- Stop all trading if daily loss exceeds 3% of portfolio

## Trading Philosophy
- Default to NO_TRADE on uncertainty — cash is a position
- RSI above 75: avoid new longs unless strong contrarian thesis
- RSI below 25: avoid new shorts unless strong contrarian thesis
- Always journal the reasoning, especially NO_TRADE decisions

## Market Hours
- Only trade 10:00 AM – 3:30 PM ET
- Always verify market is open via Alpaca clock API before acting
```

This is the **self-improvement target** — when the reflection loop identifies a systematic mistake, the proposed fix is a new rule added here. See [[SelfImprovementLoop]].

---

## Routine Execution Context

Each routine fires with access to:
- All files in the project directory (watchlist, journals, CLAUDE.md)
- All tools Claude Code normally has (file read/write, shell, MCP tools)
- Environment variables (API keys set in `.env` or shell)

Claude does **not** retain memory between routine firings — each cycle starts fresh. The journal files are the persistence layer.

---

## Frequency Recommendations

| Strategy type | Cycle frequency | Rationale |
|---|---|---|
| Swing trading (days–weeks) | Once per day | No intraday noise |
| Momentum / breakout | Every 30 min | Catch moves, limit API cost |
| Mean reversion | Every 15 min | Need tighter timing |
| Scalping | Not recommended | LLM latency too high |

"For most strategies, every 15–30 minutes during market hours is a reasonable starting point."
— [MindStudio](https://www.mindstudio.ai/blog/how-to-build-ai-trading-agent-claude-code-routines)

---

## Sources

- [MindStudio: How to Build a 24/7 AI Trading Agent with Claude Code Routines](https://www.mindstudio.ai/blog/how-to-build-ai-trading-agent-claude-code-routines)
- [MindStudio: Build a 24/7 AI Trading Agent with Claude Code and Alpaca](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca)
- [YouTube: How To Build A Self-Improving AI Trading Agent](https://www.youtube.com/watch?v=6njREUQAFdg)
