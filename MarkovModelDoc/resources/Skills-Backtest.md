# Skill: backtest

> Repo: [jackson-video-resources/skills](https://github.com/jackson-video-resources/skills)
> Back to: [[ClaudeCodeSkills-Trading]]

---

## Install

```bash
npx skills add jackson-video-resources/skills -s backtest -g -y
```

## Invoke

```
"use the backtest skill on NVDA using an EMA crossover strategy"
"use the backtest skill to test an RSI mean-reversion strategy on SPY 2020-2024"
```

---

## What It Does

Routes to one of **12 hedge fund-level backtesting frameworks** based on strategy type and objective.

### Framework Categories

| Category | Frameworks |
|---|---|
| Strategy development | Citadel builder, RenTech patterns |
| Testing & validation | Two Sigma simulator, technical analysis |
| Risk management | Bridgewater systems, Jane Street execution |
| Analysis types | JPMorgan fundamentals, AQR factors, options strategies |
| Portfolio work | Citadel optimizer, macro dashboard |
| Conviction theses | Pershing Square positioning |

### What Each Framework Covers

- Specific market inefficiencies or behavioral patterns being exploited
- Precise entry/exit conditions with numerical thresholds
- Risk-adjusted return metrics (Sharpe ratios, drawdowns, win rates)
- Historical validation against relevant market periods
- Overfitting and survivorship bias checks
- Specific actionable recommendations

---

## How It Works

1. User invokes `/backtest` with asset, strategy style, and objectives
2. Skill asks clarifying questions if needed
3. Routes to the appropriate framework
4. Delivers analysis with specific numbers, price levels, and portfolio-appropriate recommendations — not generic guidance

Emphasis is on **quantifiable edge, mathematical rigor, and institutional-grade analysis standards**.

---

## Related Files

- [[Backtesting]] — walk-forward methodology used across all frameworks
- [[HiddenMarkovTrading]] — regime-aware backtesting context
- [[AI-Quant-Workbench]] — statistical validation of signals before backtesting
