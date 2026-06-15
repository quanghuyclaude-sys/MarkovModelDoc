# Skill: pine-script

> Repo: [jackson-video-resources/skills](https://github.com/jackson-video-resources/skills)
> Back to: [[ClaudeCodeSkills-Trading]]

---

## Install

```bash
npx skills add jackson-video-resources/skills -s pine-script -g -y
```

## Invoke

```
"use pine-script to create an RSI(3) + VWAP indicator with buy/sell signals"
"use the pine-script skill to convert my MACD indicator into a testable strategy"
"use pine-script to add alerts to my existing script"
```

---

## What It Does

A Pine Script v5 specialist agent. Six modes.

### Mode 1 — Strategy Builder
Creates complete backtestable strategies from a trading hypothesis. Includes entries, exits, stop-losses, and position sizing.

### Mode 2 — Debugger
Diagnoses and fixes issues in existing Pine Script code. Works through problems systematically:
1. Syntax errors
2. Logic errors
3. Repainting risks
4. Lookahead bias
5. Type mismatches
6. Context errors

### Mode 3 — Indicator → Strategy Converter
Transforms a standalone indicator into a backtestable strategy with proper `strategy.entry()` and `strategy.exit()` calls.

### Mode 4 — Alert Builder
Adds TradingView alert conditions to existing scripts so signals can trigger webhooks, notifications, or automated execution.

### Mode 5 — Indicator Builder
Develops standalone visual analysis tools — overlays, oscillators, tables, regime ribbons.

### Mode 6 — Code Optimiser
Refactors existing scripts for clarity and performance. Removes redundant calculations, improves variable naming, restructures for readability.

---

## Enforced Standards

Every script produced by this skill follows these rules:

| Rule | Reason |
|---|---|
| No curve-fitting | Avoids adding complexity that only works in-sample |
| Mandatory stop losses | Every strategy must have exit protection |
| Equity-based sizing | Positions sized as % of account, never fixed amounts |
| Clean structure | Inputs → indicators → conditions → orders → plots |
| Simple entry logic | Favour 3-condition entries over 7-condition ones |

---

## Related Files

- [[TradingViewPineScript]] — the HMM regime ribbon script from the markov-hedge-fund-method repo
- [[TradingView-MCP]] — deploying scripts to TradingView via MCP
- [[VWAP-RSI-EMA-Strategy]] — example strategy this skill can implement
