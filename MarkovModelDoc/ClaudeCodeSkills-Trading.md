# Claude Code Skills Library — Trading Skills

> Back to: [[ZeroOne-ResourceHub]]
> Repo: [jackson-video-resources/skills](https://github.com/jackson-video-resources/skills)
> License: MIT

---

## What It Is

A public collection of reusable Claude Code skills built by Lewis Jackson for
trading, research, content, deployment, and agent-building. Skills are installed
once into Claude Code and then invokable in any session with a natural language command.

---

## Installation

```bash
# Install any skill globally
npx skills add jackson-video-resources/skills -s <skill-name> -g -y

# Examples:
npx skills add jackson-video-resources/skills -s backtest -g -y
npx skills add jackson-video-resources/skills -s risk-manager -g -y
npx skills add jackson-video-resources/skills -s trade-journal -g -y
npx skills add jackson-video-resources/skills -s strategy-audit -g -y
npx skills add jackson-video-resources/skills -s pine-script -g -y
npx skills add jackson-video-resources/skills -s autoresearch -g -y
npx skills add jackson-video-resources/skills -s capital-allocator -g -y
```

After installation, invoke from any Claude Code session:
```
"use the backtest skill on NVDA using an EMA crossover strategy"
"run the risk-manager skill on my current portfolio"
"use trade-journal to log today's trades"
```

---

## Full Skill List (11 Skills)

### Trading Skills

| Skill | Purpose | Relevant Files |
|---|---|---|
| `backtest` | Test trading strategies on historical data | [[Backtesting]] |
| `risk-manager` | Validate portfolio against risk thresholds | [[Guardrails-RiskManagement]] |
| `trade-journal` | Log and analyse trading decisions | [[TradeJournal]] |
| `strategy-audit` | Review and critique a trading strategy | [[SelfImprovementLoop]] |
| `capital-allocator` | Compute optimal position sizes | [[RegimeFilter-RiskManagement]] |
| `pine-script` | Write and deploy Pine Script to TradingView | [[TradingViewPineScript]] |

### Research Skills

| Skill | Purpose |
|---|---|
| `autoresearch` | Automated research across multiple sources |

### Engineering Skills

| Skill | Purpose |
|---|---|
| `code-simplifier` | Simplify and clean up code |
| `security-audit` | Review code for security vulnerabilities |
| `commit-push-pr` | Automate git workflow |
| `seo-optimizer` | Content SEO optimisation |

---

## Key Trading Skills In Detail

### `backtest`
Tests any strategy against historical data. Likely wraps the walk-forward
methodology from [[Backtesting]] and computes Sharpe ratio, max drawdown, CAGR.

Invoke: `"use the backtest skill to test an RSI mean-reversion strategy on SPY 2020-2024"`

### `risk-manager`
Validates a set of positions or a proposed trade against configured risk thresholds.
Same logic as [[Guardrails-RiskManagement]] but packaged as a reusable skill.

Invoke: `"use the risk-manager skill to check if adding 10 shares of NVDA breaches my limits"`

### `trade-journal`
Structured trade logging — matches the [[TradeJournal]] JSONL/Markdown format.
Feeds directly into the [[SelfImprovementLoop]] reflection routine.

Invoke: `"use trade-journal to log today: bought 5 NVDA at 875, sold at 881, RSI was 58"`

### `strategy-audit`
Reviews a strategy document or rules.json for weaknesses, overfitting risks,
missing edge cases, and improvement opportunities.

Invoke: `"use strategy-audit on my rules.json file"`

### `capital-allocator`
Computes position sizes using Kelly criterion or fixed-fraction methods.
Incorporates the half-Kelly with 2% hard cap from [[AI-Quant-Workbench]].

Invoke: `"use capital-allocator: I have $10k, entry at 875, stop at 845, win rate 60%"`

### `pine-script`
Writes, refines, and deploys Pine Script indicators to TradingView via [[TradingView-MCP]].
Can generate the HMM regime ribbon from [[TradingViewPineScript]] automatically.

Invoke: `"use pine-script to create an RSI(3) + VWAP indicator with buy/sell signals"`

### `autoresearch`
Runs automated research across multiple sources (YouTube, arXiv, web) for
any topic. Powers the nightly research loop in [[ZeroHumanTradingFirm]].

Invoke: `"use autoresearch to find the latest papers on momentum factor decay"`

---

## Deeper Documentation

Full skill documentation lives in the ZeroOne Skool community Skill Library —
accessible to members at [skool.com/zero-one/classroom](https://www.skool.com/zero-one/classroom).
The README notes: "detailed pages for each" skill exist within the community.

---

## Composing Skills

Skills are designed to compose — chain them in sequence:

```
"Use autoresearch to find 3 momentum strategies,
 then use backtest on each,
 then use strategy-audit on the best performer,
 then use capital-allocator for a $5k portfolio"
```

This mirrors the [[ZeroHumanTradingFirm]] agent pipeline compressed into one command.

---

## The markov-hedge-fund-method as a Skill

The HMM regime detector is itself distributed as a Claude Code skill:

```bash
/plugin marketplace add jackson-video-resources/markov-hedge-fund-method
/plugin install markov-hedge-fund-method@markov-hedge-fund-method
```

See [[MarkovHedgeFundMethod]] for full details. This is the bridge between
the ZeroOne skills library and [[HiddenMarkovTrading]].

---

## Sources

- [GitHub: jackson-video-resources/skills](https://github.com/jackson-video-resources/skills)
- [ZeroOne Systems Classroom](https://www.skool.com/zero-one/classroom)
- [GitHub: markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method)
