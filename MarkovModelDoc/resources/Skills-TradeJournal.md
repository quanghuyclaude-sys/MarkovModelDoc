# Skill: trade-journal

> Repo: [jackson-video-resources/skills](https://github.com/jackson-video-resources/skills)
> Back to: [[ClaudeCodeSkills-Trading]]

---

## Install

```bash
npx skills add jackson-video-resources/skills -s trade-journal -g -y
```

## Invoke

```
"use trade-journal to log today's trades"
"use trade-journal to log today: bought 5 NVDA at 875, sold at 881, RSI was 58"
```

---

## What It Does

Transforms trading performance through systematic journaling and pattern recognition. Six modes.

### Mode 1 — Trade Logger
Captures completed trades with 18+ data points:
- Entry / exit timestamps
- Asset, direction, strategy name
- Entry price, exit price, stop price
- Position size, fees, slippage
- Entry reason, exit reason
- P&L, hold time
- Emotional state at entry
- Rule compliance (yes/no)
- Lessons learned

### Mode 2 — Performance Review
Analyses a defined period (week / month / quarter) and produces:
- Return metrics
- Risk analysis: win rate, R-multiples, expectancy, profit factor, max drawdown
- Consistency patterns across time of day, assets, strategies
- Behavioural insights: rule compliance rate, emotional override frequency

### Mode 3 — Pattern Analyzer
Identifies hidden patterns from datasets of 20+ trades:
- Time-of-day performance
- Day-of-week effects
- Asset-specific patterns
- Setup quality correlation
- Hold time vs return correlation
- Position size psychology
- Winning/losing streak analysis
- Macro event clustering

### Mode 4 — Loss Autopsy
Deep analysis of losing trades across six diagnostic categories:
1. Setup quality
2. Timing issues
3. Risk management failures
4. Execution quality
5. Psychological factors
6. Market context

### Mode 5 — Journal Setup
Designs a customised three-level journaling system:
- **Level 1**: 30-second trade entry (minimum friction)
- **Level 2**: 5-minute daily review
- **Level 3**: 30-minute weekly analysis
Includes templates and tool recommendations.

### Mode 6 — Pre-Trade Mental Checklist
Eight checkpoint questions before entry to catch emotional errors:
1. Is the setup valid by my rules?
2. Is my risk defined?
3. Is position size correct?
4. Have I hit any limits today?
5. Are there news events I should know about?
6. What is my emotional state right now?
7. Am I overtrading to recover losses?
8. Would I take this trade if I had taken it 100 times?

---

## Core Principle

> "The journal is the data set you train your future judgement on."

---

## Related Files

- [[TradeJournal]] — JSONL/Markdown logging schema used by the agent pipeline
- [[SelfImprovementLoop]] — how journal data feeds the self-improvement cycle
- [[AgentArchitecture]] — Stage 4 of the pipeline writes to the journal every cycle
