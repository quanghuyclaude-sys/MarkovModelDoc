# Skill: capital-allocator

> Repo: [jackson-video-resources/skills](https://github.com/jackson-video-resources/skills)
> Back to: [[ClaudeCodeSkills-Trading]]

---

## Install

```bash
npx skills add jackson-video-resources/skills -s capital-allocator -g -y
```

## Invoke

```
"use capital-allocator: I have $10k, entry at 875, stop at 845, win rate 60%"
"use the capital-allocator to check if my current allocations are safe"
```

---

## What It Does

Optimises how capital is distributed across strategies and assets. Six modes.

### Mode 1 — Framework Builder
Creates complete allocation rules:
- Per-strategy position limits
- Asset concentration caps
- Portfolio-level exposure targets
- Drawdown scaling triggers (reduce size as drawdown increases)

### Mode 2 — New Strategy Sizing
Calculates initial allocation for a new strategy:
- Starts small, ramps based on live trade performance
- Checks correlation conflicts with existing strategies before allocating

### Mode 3 — Allocation Audit
Reviews current allocations and flags issues using a traffic-light system:
- 🔴 Concentration risk
- 🔴 Drawdown limit violations
- 🟡 Allocation drift from targets
- 🟡 Performance misalignment

### Mode 4 — Rebalancing Engine
Computes the exact trades needed to move from current to target allocation. Prioritises by drift magnitude — largest deviations rebalanced first.

### Mode 5 — Kelly Calculator
Determines position sizing using Kelly Criterion:

| Method | Description |
|---|---|
| Full Kelly | Maximum mathematically optimal size |
| Half Kelly | 50% of full Kelly — recommended for live trading |
| Quarter Kelly | 25% — very conservative, used in uncertain conditions |

Includes drawdown probability analysis at each Kelly fraction.

### Mode 6 — Multi-Strategy Manager
Designs frameworks for running multiple strategies simultaneously:
- Maps correlation between strategies
- Prevents interference (e.g., two strategies entering opposite directions)
- Establishes daily coordination routines between strategy outputs

---

## Conservative Defaults

| Limit | Default |
|---|---|
| Max allocation per strategy | 20% |
| Max allocation per asset | 30% |
| Minimum cash reserve | 20–40% |

---

## Core Principle

> "Capital allocation is the single most important thing a trader controls. Entries and exits determine individual trade wins. Allocation determines survival and long-term success."

---

## Related Files

- [[RegimeFilter-RiskManagement]] — position sizing scaled by regime confidence
- [[AI-Quant-Workbench]] — half-Kelly with 2% hard cap implementation
- [[Guardrails-RiskManagement]] — hard limits that cap what the allocator can produce
