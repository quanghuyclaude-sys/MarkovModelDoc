# Module 06 — Going Live

> Source: github.com/jackson-video-resources/claude-code-stocks-futures/prompts/module-06-going-live.md
> Part of: [[Stocks-Futures-Agent]]

---

## Risk Management Setup

```
"Add three safety mechanisms:
1. Position sizing — risk exactly 1.5% of current account balance per trade
   (read balance from Alpaca before each trade, don't cache it)
2. Daily loss limit — block new entries if realized losses reach 5% of opening
   account value. Log the halt event with timestamp.
3. Emergency halt flag — add --halt command-line flag that stops all new order
   placement while preserving existing positions."
```

Customize percentages to your risk tolerance.

---

## Transitioning to Live Trading

**Before switching:**
- ✅ Completed identity verification on Alpaca
- ✅ Deployed all risk controls
- ✅ Successfully ran at least 10 automated paper trades
- ✅ Starting with minimal position sizes
- ✅ Know your kill switch command

**The switch:** In `.env`, change:
```
ALPACA_BASE_URL=https://api.alpaca.markets
```

And replace with live API keys from the Alpaca dashboard (not paper keys).

---

## Note

The system operates identically to paper trading — only the endpoint and credentials differ. Monitor initial live trades through the Alpaca dashboard before running fully hands-off.
