# markov-hedge-fund-method — One-Shot Install Prompt

> Source: github.com/jackson-video-resources/markov-hedge-fund-method
> Paste into Claude Code agent mode to install the skill.

---

Running in agent mode — markov-hedge-fund-method install starting.

Installing the markov-hedge-fund-method skill into `~/.claude/skills/markov-hedge-fund-method/`. About 90 seconds on Mac and Linux, up to 2–3 minutes on Windows. No keys, no accounts, no admin password.

## Install via Plugin Marketplace

```
/plugin marketplace add jackson-video-resources/markov-hedge-fund-method
/plugin install markov-hedge-fund-method@markov-hedge-fund-method
```

## Or: Build Locally (Transparent Path)

Use `markov-hedge-fund-method.md` as a one-shot prompt in Claude Code. Every line is generated in front of you.

## Plugin Metadata

```json
{
  "name": "markov-hedge-fund-method",
  "description": "Markov regime detection for any asset. Labels each day Bull/Bear/Sideways from a rolling-return rule, builds the maximum-likelihood transition matrix, forecasts n-step ahead via Chapman-Kolmogorov, solves the stationary distribution, and runs a no-lookahead walk-forward backtest reporting Sharpe and max drawdown. Composes into any trading agent on any asset as a confirmation, signal, or tail-risk layer. Optional Hidden Markov Model upgrade. Framework by Roan (@RohOnChain).",
  "version": "1.0.0",
  "author": { "name": "Lewis Jackson" }
}
```

## After Install — Invocation Examples

```
"run the regime skill on SPY"
"use the markov skill on BTC-USD and give me the 5-day forecast"
"load the regime skill and tell me if NVDA is in a Bull or Bear regime"
"use the regime skill on my CSV file at ~/data/prices.csv"
```
