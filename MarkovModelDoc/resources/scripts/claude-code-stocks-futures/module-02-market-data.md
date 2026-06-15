# Module 02 — Market Data & Signal Generation

> Source: github.com/jackson-video-resources/claude-code-stocks-futures/prompts/module-02-market-data.md
> Part of: [[Stocks-Futures-Agent]]

---

## Section 2.1 — Live Market Data

```
"Create a Python script connecting to Alpaca's real-time API via websocket.
Subscribe to live trades and quotes for NQ1! (continuous front-month NASDAQ futures).
Print timestamp, symbol, bid and ask prices using APCA_API_KEY_ID and
APCA_API_SECRET_KEY environment variables with the paper trading base URL."
```

**Stocks traders:** Use `SPY` instead of `NQ1!`.

**Stream error fix:**
```
"Which Alpaca data stream handles futures, and can you rewrite this script accordingly?"
```

---

## Section 2.2 — Signal Engine

```
"Develop a signal engine receiving live 15-minute bar data from the Alpaca websocket.
Calculate 20-period and 50-period EMAs using pandas-ta or ta-lib.
Generate BUY SIGNAL when the 20 EMA crossed above 50 EMA on 15m.
Generate SELL SIGNAL for crossovers below.
Maintain a rolling window of 100+ bars."
```

**Key requirement:** Minimum 50 completed bars before calculating the 50-period EMA.

**Backtesting mode:**
```
"Implement backtesting mode running the signal engine against the last 200 historical
bars from Alpaca instead of live data to verify signal logic."
```
