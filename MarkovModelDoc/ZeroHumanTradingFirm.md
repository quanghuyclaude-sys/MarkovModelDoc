# Zero-Human Trading Firm — 6-Agent Autonomous System

> Back to: [[ZeroOne-ResourceHub]]
> Repo: [jackson-video-resources/paperclip-zero-human-trading-firm](https://github.com/jackson-video-resources/paperclip-zero-human-trading-firm)
> Video: [I Built a Zero-Human Trading Team with Claude](https://www.youtube.com/watch?v=cXhEw2jF4go)

---

## What It Is

A single one-shot prompt that builds a fully autonomous AI trading organisation
using Paperclip (MIT license) + Claude Code + TradingView MCP. Paste one prompt
into Claude Code — it deploys a 6-agent firm that researches, backtests, validates
risk, and executes trades without human intervention.

---

## The Six Agents

### CEO Agent
- Direct report to the user only
- Manages team delegation and weekly board briefings
- Sole authority to approve strategy activation for live trading
- Hiring authority for any custom roles added during onboarding

### Research Agent
- Runs **nightly** scans across: YouTube, arXiv, TradingView ideas, Reddit
- Delivers weekly strategy briefs to the team
- Feeds intelligence into Backtest and Risk agents
- Equivalent to a full-time analyst working overnight

### Backtest Agent
- Tests every strategy proposed by Research using historical data
- Maintains permanent result logs (institutional memory)
- Uses [[TradingView-MCP]] for historical OHLCV access
- Strategies that fail backtesting never reach Risk Agent

### Risk Management Agent
- Gatekeeper between Backtest results and Execution
- Validates every strategy against `risk-thresholds.json` (immutable)
- Blocks any strategy that fails risk parameters
- No agent can modify its own risk enforcement rules (Rule 1)

### Execution Agent
- Places trades when Risk Agent clears a strategy
- Paper trading mode by default
- Live mode activated only by user instruction to the CEO
- Operates via [[TradingView-MCP]] or exchange API

### Cost Optimizer Agent
- Monitors token usage weekly across all agents
- Identifies and eliminates unnecessary token consumption
- Keeps API costs manageable as the firm scales

---

## Onboarding: 8-Phase Automated Setup

Paste the contents of `/prompts/mac.md` (or windows.md / linux.md) into Claude Code:

| Phase | What Happens |
|---|---|
| 1. Environment Check | Verifies OS, Node.js, Git |
| 2. Intake Interview | 5 questions: firm name, goals, strategy source, team size, risk tolerance |
| 3. Paperclip Install | Auto-runs `npx paperclip@latest` |
| 4. File Structure | Creates `~/[firm-name]/agents/`, `strategies/`, `logs/`, `memory/`, `config/` |
| 5. TradingView MCP | Installs [[TradingView-MCP]] without disrupting existing servers |
| 6. Team Hiring | CEO receives full mandate briefs and delegates to agents |
| 7. Dashboard | Auto-opens Paperclip workspace |
| 8. Confirmation | Displays firm summary and next steps |

---

## Risk Thresholds File

Located at `~/[firm-name]/config/risk-thresholds.json`.
Described as "the law" — only the user can modify it.

```json
{
  "max_drawdown_pct": 10,
  "max_position_size_pct": 5,
  "max_daily_loss_pct": 3,
  "min_backtest_sharpe": 0.5,
  "min_backtest_days": 30,
  "paper_trading_days_required": 30,
  "max_concurrent_strategies": 3
}
```

The Risk Agent enforces these thresholds. No agent can access the systems
that enforce its own limits (the three operational rules).

---

## Three Operational Rules (Hardcoded)

1. No agent receives access to systems enforcing its own risk limits
2. The risk-thresholds.json is immutable except by the user
3. If anomalies emerge, fix the strategy — never lower thresholds to
   accommodate poor performance

---

## Live Trading Activation Sequence

```
Strategy completes 30+ days paper trading
    └──► Backtest Agent validates with full historical data
    └──► Risk Agent confirms thresholds passed
    └──► User tells CEO: "Activate live money trading"
    └──► CEO confirms details and briefs Execution Agent
    └──► Execution Agent switches from paper to live
```

This is the only gate between simulation and real capital.

---

## Bringing Your Own Strategy

During the intake interview, Claude accepts strategy input via:
- Plain language description
- Document or rules file path
- PDF/text upload to Claude Code

The strategy context flows into all agent briefs and decision frameworks.
You can drop in a rules.json from [[YT-StrategyAgent]] or [[VWAP-RSI-EMA-Strategy]].

---

## Requirements

- Claude Code (running)
- Node.js (auto-installed if missing)
- Git (auto-installed if missing)
- TradingView Desktop with paid subscription
- Active Claude Code subscription

No extra Paperclip cost — it is MIT licensed and open source.

---

## Mapping to Your Existing Stack

```
ZeroHumanTradingFirm
    │
    ├── Research Agent nightly scan
    │       └── feeds [[YT-StrategyAgent]] output
    │
    ├── Backtest Agent
    │       └── uses [[AI-Quant-Workbench]] for statistical validation
    │
    ├── Risk Agent
    │       └── same logic as [[Guardrails-RiskManagement]]
    │
    ├── Execution Agent
    │       └── same pattern as [[TradeExecution]]
    │
    └── All agents use [[TradingView-MCP]] for chart data
```

The HMM regime filter ([[HiddenMarkovTrading]]) slots in as an additional
condition in the Risk Agent's threshold file — only allow execution when
the HMM is in Bull regime.

---

## Sources

- [GitHub: paperclip-zero-human-trading-firm](https://github.com/jackson-video-resources/paperclip-zero-human-trading-firm)
- [YouTube: I Built a Zero-Human Trading Team with Claude](https://www.youtube.com/watch?v=cXhEw2jF4go)
- [ZeroOne Systems](https://www.skool.com/zero-one)
