# Stocks, Futures & Forex Agent — Alpaca Automated Trading

> Back to: [[ZeroOne-ResourceHub]]
> Repo: [jackson-video-resources/claude-code-stocks-futures](https://github.com/jackson-video-resources/claude-code-stocks-futures)

---

## What It Is

A free, open-source course and one-shot prompt that builds a live automated
trading system for stocks, futures, and Forex using Claude Code + Alpaca Markets.
No coding required — describe your trading needs in plain English.

This is the equity/futures equivalent of [[ClaudeTradingView-Bot]] (which targets crypto via BitGet).

---

## What It Builds

A fully automated system that:
- Retrieves real-time pricing via Alpaca API (stocks, futures, Forex)
- Generates trade signals using configurable logic (EMA crossover, RSI, mean reversion)
- Sizes positions automatically from fixed risk percentages
- Executes orders without manual intervention
- Runs 24/7 via PM2 process management with auto-restart
- Sends Telegram alerts for fills and errors
- Includes automated ML parameter retraining loop

---

## Strategy Sourcing (Five Methods)

Claude Code builds the signal logic from whichever source you provide:

| Method | Details |
|---|---|
| Your existing strategy | Describe your rules in plain English |
| GitHub open-source strategies | Point Claude at any algo repo |
| YouTube transcript mining | Via Apify — see [[YT-StrategyAgent]] |
| Hedge fund pitch decks | Reverse-engineer via SEC EDGAR filings |
| First principles | Describe the market thesis, Claude codes it |

---

## Supported Markets

All via Alpaca Markets API:

| Market | Examples |
|---|---|
| US Stocks | NVDA, AAPL, SPY, QQQ |
| Futures | ES (S&P 500), NQ (Nasdaq), CL (Crude Oil), GC (Gold) |
| Forex | EUR/USD, GBP/USD, USD/JPY |

Alpaca is commission-free for stocks. Paper trading is free and unlimited.

---

## Technical Components

| Component | Technology |
|---|---|
| Market data | WebSocket live feeds via Alpaca |
| Backtesting | Scientific methodology with iteration loops |
| Signal generation | EMA crossover, RSI, mean reversion, custom |
| Position sizing | Fixed % risk per trade |
| Order execution | Alpaca Trading API |
| Deployment | PM2 process manager (24/7, auto-restart) |
| Alerts | Telegram bot integration |
| ML retraining | Automated parameter optimisation loop |

---

## Course Structure (8 Modules)

| Module | Content |
|---|---|
| 1. Setup | Environment, API keys, paper account |
| 2. Signal Generation | EMA, RSI, mean reversion logic |
| 3. Strategy Sourcing | 5 methods above |
| 4. Backtesting | Walk-forward methodology with ML loops |
| 5. Paper Trading | Execution without real money |
| 6. Live Deployment | Switch to live capital |
| 7. PM2 Automation | 24/7 process management |
| 8. Multi-Market | Expand to futures, Forex |

---

## ML Retraining Loop

Unlike a static strategy, this system periodically re-optimises parameters:

```
Live trading data accumulates
    └──► ML loop evaluates recent performance
    └──► Adjusts indicator parameters (RSI period, EMA length, etc.)
    └──► Re-validates on out-of-sample data
    └──► Deploys updated parameters
    └──► Continues live trading with improved settings
```

This is the same principle as [[SelfImprovementLoop]] — outputs feed back in as inputs.

---

## Integration With Your Strategy Stack

This agent is the equity/futures execution layer of your full stack:

```
[[HiddenMarkovTrading]] → regime signal (Bull/Bear/Sideways)
        │
        ▼
Stocks-Futures-Agent (this file)
        │ only trades in Bull regime
        ▼
[[Guardrails-RiskManagement]] → position sizing, stop-loss
        │
        ▼
Alpaca API → order execution
        │
        ▼
[[TradeJournal]] → log decision + outcome
        │
        ▼
[[SelfImprovementLoop]] → weekly reflection
```

---

## Deployment

```bash
# PM2 keeps the bot running 24/7
npm install -g pm2
pm2 start bot.js --name trading-bot
pm2 startup  # auto-restart on server reboot
pm2 save
```

Telegram alert setup:
1. Create a Telegram bot via @BotFather
2. Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to .env
3. Bot sends alerts on fills, errors, and daily P&L summary

---

## Before Going Live

Follow the same progression as [[Deployment]]:
- Paper trade for 90+ days
- Confirm ML retraining works correctly
- Test Telegram alerts
- Verify PM2 auto-restart after simulated crash
- Check Alpaca PDT rules if account under $25K

---

## Sources

- [GitHub: claude-code-stocks-futures](https://github.com/jackson-video-resources/claude-code-stocks-futures)
- [ZeroOne Systems](https://www.skool.com/zero-one)
- [Alpaca Markets](https://alpaca.markets)
