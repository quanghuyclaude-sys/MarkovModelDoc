# Module 08 — Expansion & Multi-Market

> Source: github.com/jackson-video-resources/claude-code-stocks-futures/prompts/module-08-multi-market.md
> Part of: [[Stocks-Futures-Agent]]

---

## Section 8.1 — Multiple Instruments in Parallel

**Step 1 — Parameterise the instrument:**
```
"Extend the trading system so the instrument is accepted as a command-line argument
rather than hardcoded. Ensure trade log filenames and PM2 process names include
the instrument identifier to prevent file overwrites."
```

**Step 2 — Add a second instrument to PM2:**
```
"Add a second PM2 process for NQ1! futures named trend-nq, keeping configuration
identical to the EUR/USD process."
```

```bash
pm2 restart ecosystem.config.js --update-env
```

**PM2 ecosystem.config.js example:**
```js
module.exports = {
  apps: [
    { name: "trend-eur-usd", script: "trading-system.py", interpreter: "python3", args: "--instrument EURUSD" },
    { name: "trend-nq",      script: "trading-system.py", interpreter: "python3", args: "--instrument NQ1!" },
  ]
}
```

---

## Section 8.2 — Second Strategy (Mean Reversion)

```
"Build a mean reversion strategy for NQ1!:
Long entries:  RSI below 30 AND price more than 1 ATR below the 20-period EMA
Long exits:    RSI crosses above 50, or stop loss at 1.5 ATR below entry
Short entries: RSI above 70 AND price more than 1 ATR above the 20 EMA
Short exits:   RSI crosses below 50

Add as a third PM2 process (mean-rev-nq) using existing market data and execution infrastructure."
```

**Troubleshooting:** `pm2 logs mean-rev-nq --lines 20` — check for symbol formatting or missing RSI library.

---

## Final State: Three Active Processes

| PM2 Process | Strategy | Instrument |
|---|---|---|
| trend-eur-usd | EMA crossover (trend) | EUR/USD |
| trend-nq | EMA crossover (trend) | NQ1! |
| mean-rev-nq | RSI mean reversion | NQ1! |

Two distinct strategy types with non-overlapping performance cycles.

---

## Section 8.3 — Extension Ideas

- Add news sentiment scoring via Claude Code to adjust position sizing
- Implement multi-timeframe confirmation (1-hour trend + 5-minute entries)
- Portfolio-level risk: pause all entries if total exposure exceeds 5% of account
- Add HMM regime filter — see [[RegimeFilter-RiskManagement]] and [[Skills-MarkovRegime]]
