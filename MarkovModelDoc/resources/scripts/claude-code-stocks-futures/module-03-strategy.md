# Module 03 — Strategy Sourcing

> Source: github.com/jackson-video-resources/claude-code-stocks-futures/prompts/module-03-strategy.md
> Part of: [[Stocks-Futures-Agent]]

---

## Strategy Template for Claude Code

```
I want to build a trading strategy with the following rules:

Instrument: [e.g. EUR/USD, NQ1!, SPY]
Timeframe: [e.g. 15-minute bars, daily bars]

Entry conditions (long):
- [Condition 1 — e.g. 20-period EMA crosses above 50-period EMA]
- [Condition 2 — optional additional filter]

Entry conditions (short):
- [Mirror of long conditions, or leave blank if long-only]

Exit conditions:
- Stop loss: [e.g. 1% of entry price, or 47 points below entry]
- Take profit: [e.g. 2:1 reward-to-risk ratio]
- [Any additional exit conditions]

Position sizing:
- Risk [X]% of account balance per trade

Any other rules:
- [e.g. only trade during London/NY session overlap]
- [e.g. no trades on Friday afternoon]
```

---

## Five Strategy Sources

**Source 1** — Convert an existing manual approach using the template above. Replace vague language with specific thresholds.

**Source 2** — Mine GitHub for open-source strategies:
`https://github.com/search?q=trading+strategy+backtest+python`

**Source 3** — Extract from YouTube transcripts via Apify, then ask Claude Code to structure the rules. See [[YT-StrategyAgent]].

**Source 4** — Locate strategy descriptions in SEC filings via EDGAR or Google.

**Source 5** — Build from market observations, converting qualitative insights into quantifiable triggers.

---

## Module 3 Checkpoint

Your strategy specification must answer:
- Which instrument?
- Which timeframe?
- What exact conditions signal entry?
- What mechanisms close positions?
- How does position sizing work?

This feeds directly into Module 4 backtesting.
