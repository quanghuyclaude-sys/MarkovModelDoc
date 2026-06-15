# Claude + TradingView Bot — Automated Crypto Trading

> Back to: [[ZeroOne-ResourceHub]]
> Repo: [jackson-video-resources/claude-tradingview-mcp-trading](https://github.com/jackson-video-resources/claude-tradingview-mcp-trading)
> Video: [How To Connect Claude to TradingView](https://www.youtube.com/watch?v=vIX6ztULs4U)

---

## What It Does

Connects Claude Code to TradingView charts and executes cryptocurrency trades
automatically on BitGet. Claude reads live indicator data, evaluates strategy
conditions from rules.json, validates risk rules, and places orders — all without
manual intervention.

Full pipeline per cycle:
```
Read rules.json (your strategy)
    → Pull live price + indicator data from TradingView MCP
    → Calculate MACD and technical state
    → Evaluate market direction (bullish / bearish / neutral)
    → Apply trading limits and position sizing
    → Validate ALL entry conditions
    → If approved: execute via BitGet API
    → Log to trades.csv (tax-ready)
    → Write safety-check-log.json (decision audit trail)
```

---

## Quick Start (One-Shot)

Copy the entire contents of `prompts/02-one-shot-trade.md` into Claude Code.
Claude acts as an onboarding agent and walks through:

1. BitGet API connection
2. Strategy configuration (rules.json)
3. TradingView MCP setup
4. Optional VPS deployment for 24/7 operation

No coding required.

---

## Prerequisites

- [[TradingView-MCP]] installed and connected
- Claude Code installed
- BitGet account (or any supported exchange)
- Node.js 18+

---

## Environment Variables (.env)

```bash
# Exchange credentials
BITGET_API_KEY=your_key
BITGET_SECRET_KEY=your_secret
BITGET_PASSPHRASE=your_passphrase

# Risk controls
PORTFOLIO_VALUE_USD=1000        # total portfolio size
MAX_TRADE_SIZE_USD=100          # max per trade
MAX_TRADES_PER_DAY=3            # daily trade cap
PAPER_TRADING=true              # set false for live
```

---

## Supported Exchanges

| Exchange | Notes |
|---|---|
| BitGet | Primary integration, featured in repo |
| Binance | Cloud mode sources candle data from Binance |
| Bybit | Supported |
| OKX | Supported |
| Coinbase Advanced | Supported |
| Kraken | Supported |
| KuCoin | Supported |
| Gate.io | Supported |
| MEXC | Supported |
| Bitfinex | Supported |

For all exchanges: disable withdrawals, enable IP whitelist on the API key.

---

## Strategy Configuration

The bot reads strategy logic from `rules.json`. The default example is the
[[VWAP-RSI-EMA-Strategy]] (van de Poppe + Tone Vays BTC methodology on 1-minute BTCUSDT).

To use your own strategy:
1. Run Apify YouTube Transcript Scraper on any trading channel
2. Feed transcript into `prompts/01-extract-strategy.md`
3. Claude generates a custom rules.json
4. Replace the default file

---

## Safety Guardrails

Every trade passes through multi-layer validation before execution:

| Guardrail | Mechanism |
|---|---|
| All strategy conditions must pass | rules.json conditions evaluated in code |
| Max position size | `MAX_TRADE_SIZE_USD` env var |
| Daily trade cap | `MAX_TRADES_PER_DAY` env var |
| Portfolio risk limit | 1% max risk per trade |
| Decision audit trail | Every decision logged to safety-check-log.json |
| Paper trading mode | `PAPER_TRADING=true` — no real orders placed |

See [[Guardrails-RiskManagement]] for the full multi-layer pattern.

---

## Key Files

| File | Purpose |
|---|---|
| `bot.js` | Main execution script |
| `rules.json` | Strategy conditions |
| `.env` | Credentials and risk parameters |
| `prompts/01-extract-strategy.md` | Converts YouTube transcript to rules.json |
| `prompts/02-one-shot-trade.md` | One-shot onboarding prompt |
| `trades.csv` | Tax-ready transaction log |
| `safety-check-log.json` | Decision rationale audit trail |

---

## Cloud Deployment (24/7 VPS)

For continuous operation on Hostinger VPS (~$5/month):

```bash
# Provision VPS, SSH in, then:
git clone https://github.com/jackson-video-resources/claude-tradingview-mcp-trading
cd claude-tradingview-mcp-trading
npm install
# Create .env with credentials
# Set cron schedule matching your chart timeframe:
# 4H chart:  0 */4 * * *
# 1H chart:  0 * * * *
# 1D chart:  0 9 * * *
```

In cloud mode, candle data is sourced from Binance API — TradingView Desktop
is not required on the VPS.

---

## Tax Accounting

Every executed trade logs automatically to `trades.csv`:

```
Date, Time, Exchange, Symbol, Side, Quantity, Price, Total_USD,
Estimated_Fee, Net_Amount, Order_ID, Mode (Paper/Live)
```

Run `node bot.js --tax-summary` for a full activity overview.

---

## Connection to Broader Strategy Stack

```
[[TradingView-MCP]] → live chart data
        ↓
ClaudeTradingView-Bot (this file)
        ↓
[[VWAP-RSI-EMA-Strategy]] → rules.json conditions
        ↓
BitGet API → order execution
        ↓
trades.csv → [[TradeJournal]] pattern
        ↓
[[SelfImprovementLoop]] → weekly reflection
```

Layer the HMM regime filter on top by adding regime conditions to rules.json.
See [[HiddenMarkovTrading]] and [[RegimeFilter-RiskManagement]].

---

## Sources

- [GitHub: claude-tradingview-mcp-trading](https://github.com/jackson-video-resources/claude-tradingview-mcp-trading)
- [prompts/02-one-shot-trade.md](https://github.com/jackson-video-resources/claude-tradingview-mcp-trading/blob/main/prompts/02-one-shot-trade.md)
- [ZeroOne Systems](https://www.skool.com/zero-one)
