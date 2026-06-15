# Self-Improvement Loop — How the Agent Learns From Itself

> Back to: [[SelfImprovingTradingAgent]]
> Sources: [MindStudio: Claude Code Routines](https://www.mindstudio.ai/blog/how-to-build-ai-trading-agent-claude-code-routines) · [Self-improving CLAUDE.md files](https://martinalderson.com/posts/self-improving-claude-md-files/) · [QuantAgent Paper](https://arxiv.org/abs/2402.03755)

---

## The Core Idea

The agent's outputs become its next inputs. Every journal entry is a data point. Over time, the journal accumulates enough signal to identify:

- Systematic entry/exit timing errors
- Confidence miscalibration (HIGH confidence trades that lost money)
- News sentiment biases (overreacting to negative headlines)
- Symbol-specific blind spots (always trading tech, ignoring energy)
- Rules that should be added to `CLAUDE.md`

This is **not** automatic retraining of a model weight. It is Claude reading its own history and proposing rule updates that a human reviews before committing to `CLAUDE.md`.

---

## The Improvement Cycle

```
Daily Trading Cycles
        │
        ▼ (accumulates)
  Trade Journal
  (JSONL + Markdown)
        │
        │  weekly
        ▼
  Reflection Routine
  (Claude reads 5 days of journals)
        │
        ▼
  Pattern Report
  (identifies systematic errors)
        │
        │  human reviews
        ▼
  CLAUDE.md Updated
  (new rules added / old rules refined)
        │
        ▼
  Next week's cycles
  run with improved rules
```

---

## Weekly Reflection Routine Prompt

Defined in `.claude/routines.json` as a Friday 5 PM routine:

```
Read all journal entries from the past 5 trading days in the journals/ directory.

Analyze the following:
1. Win rate: how many BUY decisions were profitable vs. unprofitable?
2. Confidence calibration: did HIGH confidence correlate with better outcomes?
3. NO_TRADE quality: were there moves we should have caught but missed?
4. Systematic patterns: any recurring mistake (always selling too early, news overreaction)?
5. Symbol bias: are we over-concentrated in any sector or name?

After analysis, produce:
- A "Weekly Performance Report" section summarizing metrics
- A "Proposed CLAUDE.md Updates" section with specific new or modified rules
- A "Next Week Focus" section with 2-3 things to watch

Write the report to journals/weekly-YYYY-MM-DD.md
Do NOT automatically update CLAUDE.md — list proposed changes only.
```

---

## Example Reflection Output

```markdown
# Weekly Performance Report — 2026-06-12

## Metrics
- Total cycles: 130
- Trades executed: 18
- Profitable trades: 11 (61% win rate)
- HIGH confidence trades: 10 → 8 profitable (80%)
- MEDIUM confidence trades: 8 → 3 profitable (38%)
- NO_TRADE decisions: 112

## Systematic Patterns Found

**Pattern 1 — Selling too early on momentum stocks**
NVDA was sold 3 times this week at +0.8% when it continued to +2.5%.
The exit signal (MA crossover) triggers too early on high-momentum names.

**Pattern 2 — Overreacting to negative news**
4 NO_TRADE decisions cited negative news as a reason. In 3 of those 4 cases,
the stock recovered the same day and we missed a profitable long setup.

**Pattern 3 — MEDIUM confidence underperforms**
38% win rate at MEDIUM confidence is below the 50% breakeven threshold
given our risk/reward setup. Consider requiring HIGH confidence only.

## Proposed CLAUDE.md Updates

1. ADD: "For stocks with RSI > 60 and positive trend, require 2 consecutive MA
   crossover signals before exiting — not just one bar."

2. ADD: "Negative news alone is insufficient for NO_TRADE unless RSI is also
   above 70 or the news is company-specific (earnings miss, fraud, etc.)."

3. MODIFY: Change confidence threshold from MEDIUM to HIGH for new BUY entries.
   Current rule: "Execute MEDIUM and HIGH confidence." 
   Proposed: "Execute HIGH confidence only. Log MEDIUM as observation."

## Next Week Focus
- Watch AAPL for RSI pullback below 65 — missed entry this week
- Monitor NVDA exit timing — test new 2-bar rule
- Track whether eliminating MEDIUM confidence trades improves Sharpe
```

---

## Promoting Observations to Rules (Maturity Model)

```
Level 1: Observation (in journal)
"I notice I keep selling NVDA too early"

Level 2: Pattern (in weekly report)
"NVDA exits triggered early 3/4 times this week — possible rule issue"

Level 3: Proposed rule (in weekly report)
"Require 2 MA crossover bars before exit on high-momentum stocks"

Level 4: Enforced rule (in CLAUDE.md)
"For RSI > 60 stocks, require 2 consecutive exit signals before closing"
```

The human decides when to promote from Level 3 to Level 4. This is the safety gate.

---

## Feeding Journal History Back to Claude

When the reflection routine fires, it needs to read past journals efficiently. Summarize before passing to avoid bloating context:

```python
def summarize_week_for_reflection(days: int = 5) -> str:
    df = load_journal(days=days)

    trades    = df[df["decision"].isin(["BUY", "SELL"])]
    no_trades = df[df["decision"] == "NO_TRADE"]

    lines = [
        f"Period: last {days} trading days",
        f"Total cycles: {len(df)}",
        f"Trades: {len(trades)} | NO_TRADEs: {len(no_trades)}",
        "",
        "=== TRADE LOG (last 20) ===",
    ]

    for _, row in trades.tail(20).iterrows():
        lines.append(
            f"{row['timestamp'][:10]} | {row['symbol']} | {row['decision']} | "
            f"conf={row['confidence']} | {row['reasoning'][:120]}"
        )

    lines.append("\n=== SAMPLE NO_TRADE REASONING ===")
    for _, row in no_trades.sample(min(10, len(no_trades))).iterrows():
        lines.append(f"{row['timestamp'][:10]} | {row['symbol']} | {row['reasoning'][:120]}")

    return "\n".join(lines)
```

---

## QuantAgent's Two-Layer Self-Improvement

The academic version of this pattern (see [[QuantAgent-Paper]]) formalizes the loop:

```
Inner Loop (per signal):
  Agent generates signal code
      → Draws from knowledge base for prior similar signals
      → Refines output based on knowledge base context

Outer Loop (per backtest cycle):
  Generated signal is backtested
      → Performance metrics computed automatically
      → Knowledge base updated with:
          - Signal implementation code
          - Underlying trading idea
          - Performance metrics
          - Expert review notes
      → Next inner loop cycle has richer knowledge base
```

The journal-based approach in this video is the practical, no-infrastructure version of this pattern.

---

## What the Self-Improvement Loop Does NOT Do

| Misconception | Reality |
|---|---|
| Automatically rewrites CLAUDE.md | No — it proposes changes, human approves |
| Retrains Claude's weights | No — Claude's model is fixed |
| Guarantees improvement every week | No — bad patterns need enough data to surface |
| Replaces backtesting | No — retrospective analysis ≠ forward validation |

---

## Sources

- [MindStudio: How to Build a 24/7 AI Trading Agent with Claude Code Routines](https://www.mindstudio.ai/blog/how-to-build-ai-trading-agent-claude-code-routines)
- [Self-improving CLAUDE.md files (Martin Alderson)](https://martinalderson.com/posts/self-improving-claude-md-files/)
- [QuantAgent: Seeking Holy Grail in Trading by Self-Improving LLM](https://arxiv.org/abs/2402.03755)
- [YouTube: How To Build A Self-Improving AI Trading Agent](https://www.youtube.com/watch?v=6njREUQAFdg)
