# Skill: risk-manager

> Repo: [jackson-video-resources/skills](https://github.com/jackson-video-resources/skills)
> Back to: [[ClaudeCodeSkills-Trading]]

---

## Install

```bash
npx skills add jackson-video-resources/skills -s risk-manager -g -y
```

## Invoke

```
"run the risk-manager skill on my current portfolio"
"use the risk-manager skill to check if adding 10 shares of NVDA breaches my limits"
```

---

## What It Does

A **pre-trade risk management framework** with six operational modes.

### Mode 1 — Pre-Trade Gate
Evaluates proposed trades against a checklist before execution:
- Daily loss limit check
- Position concentration check
- Risk-reward ratio validation

### Mode 2 — Risk Rule Builder
Constructs a personalised risk framework covering:
- Daily / weekly / monthly loss limits
- Position sizing caps
- Mandatory stop-loss protocols

### Mode 3 — Circuit Breaker Setup
Establishes hard stops that automatically suspend trading when loss thresholds trigger. These are non-negotiable — they cannot be overridden in the moment.

### Mode 4 — Portfolio Risk Audit
Analyses all open positions for:
- Concentration risk
- Correlation overlap between positions
- Worst-case loss scenarios across the full portfolio

### Mode 5 — Position Sizing Calculator
Computes correct trade size using:
- Dollar risk per trade
- Risk per unit (entry vs stop distance)
- Account exposure percentage

### Mode 6 — Daily Risk Dashboard
- Pre-session checklist: distance to loss limits, setup quality
- Post-session checklist: trade adherence review, rule compliance score

---

## Core Principle

> "The purpose of risk management is to make decisions in advance so emotion can't override them in the moment."

---

## Related Files

- [[Guardrails-RiskManagement]] — the same logic packaged as code
- [[RegimeFilter-RiskManagement]] — regime-aware position sizing
- [[TradeExecution]] — how guardrails are enforced at order time
