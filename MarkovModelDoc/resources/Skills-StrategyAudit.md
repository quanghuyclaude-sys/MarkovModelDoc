# Skill: strategy-audit

> Repo: [jackson-video-resources/skills](https://github.com/jackson-video-resources/skills)
> Back to: [[ClaudeCodeSkills-Trading]]

---

## Install

```bash
npx skills add jackson-video-resources/skills -s strategy-audit -g -y
```

## Invoke

```
"use strategy-audit on my rules.json file"
"use strategy-audit to stress test my VWAP scalping strategy"
```

---

## What It Does

Rigorously tests trading strategies before deploying real capital. Six modes.

### Mode 1 — Full Stress Test
Comprehensive evaluation across six test dimensions:
1. In-sample performance
2. Walk-forward out-of-sample results
3. Monte Carlo simulation
4. Sensitivity analysis (parameter robustness)
5. Fees and slippage impact
6. Drawdown analysis

### Mode 2 — Scientific Optimiser
Tests one variable at a time to avoid curve-fitting. Prevents the trap of optimising multiple parameters simultaneously on the same data.

### Mode 3 — Rapid Verdict
10-question checklist for quick assessment. Useful for filtering strategies before committing to a full stress test.

### Mode 4 — Overfitting Detector
Identifies whether a strategy is memorising historical patterns rather than capturing a genuine edge. Flags:
- Too many parameters relative to sample size
- In-sample vs out-of-sample performance gap
- Parameter sensitivity cliffs

### Mode 5 — Backtest Interpreter
Explains what metrics mean in practical terms:
- What a Sharpe of 0.8 means for real trading
- Why max drawdown matters more than average return
- How to interpret profit factor and expectancy

### Mode 6 — Live vs Backtest Audit
Diagnoses why live performance diverges from backtests:
- Lookahead bias in historical data
- Spread and slippage not modelled
- Execution delays
- Market impact on position sizing

---

## Pass Standards

A strategy must meet all of these before capital deployment:

| Metric | Minimum |
|---|---|
| Sharpe ratio (out-of-sample) | > 1.0 |
| Max drawdown | < 20% |
| Walk-forward consistency | Stable across periods |
| Parameter robustness | ±20% variation tolerated |
| Minimum trade count | 50 trades |

> "Borderline strategies fail."

---

## Core Philosophy

> "Your job is to find every reason it might not work" — not to confirm your thesis.

The skill defaults to skepticism over confirmation bias.

---

## Related Files

- [[Backtesting]] — walk-forward methodology
- [[AI-Quant-Workbench]] — statistical tests (ADF, t-test, OLS) that complement this audit
- [[SelfImprovementLoop]] — ongoing strategy refinement after audit
