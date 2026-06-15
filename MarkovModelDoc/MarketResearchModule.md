# Market Research Module — Data Collection Layer

> Back to: [[SelfImprovingTradingAgent]]
> Sources: [MindStudio: Build a 24/7 AI Trading Agent](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca) · [Tradewink: Build an AI Trading Agent with Alpaca API](https://www.tradewink.com/learn/build-ai-agent-alpaca-tutorial)

---

## Purpose

The research module translates raw market data into a **structured JSON snapshot** that Claude can reason about. Claude never touches raw OHLCV feeds directly — it reads a clean, pre-computed summary.

This separation matters: bad data in = bad decisions out. The research module is the most important reliability layer in the system.

---

## Data Sources

| Source | Data Provided | API |
|---|---|---|
| Alpaca Data API | OHLCV bars, quotes, news | `data.alpaca.markets` |
| Polygon.io | News, fundamentals, options flow | `api.polygon.io` |
| Alpaca Trading API | Account, positions, orders | `api.alpaca.markets` |
| Computed locally | RSI, SMA, VWAP deviation | `pandas` / `ta` library |

---

## Full Implementation

### Setup

```python
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest, StockNewsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient

API_KEY    = os.environ["APCA_API_KEY_ID"]
API_SECRET = os.environ["APCA_API_SECRET_KEY"]
BASE_URL   = os.environ.get("APCA_BASE_URL", "https://paper-api.alpaca.markets")

data_client  = StockHistoricalDataClient(API_KEY, API_SECRET)
trade_client = TradingClient(API_KEY, API_SECRET, paper=True)
```

### Price Bars (60-bar cap for token efficiency)

```python
def get_price_bars(symbol: str, n_bars: int = 60) -> pd.DataFrame:
    end   = datetime.now()
    start = end - timedelta(days=n_bars + 10)   # buffer for weekends/holidays
    req   = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=start,
        end=end
    )
    bars = data_client.get_stock_bars(req).df
    return bars.tail(n_bars)
```

> Cap at 60 bars, not 500 — larger windows bloat context and cost. 60 days covers SMA-50 with room to spare.

### Technical Indicators

```python
def compute_indicators(bars: pd.DataFrame) -> dict:
    close  = bars["close"]
    volume = bars["volume"]

    # RSI-14
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss
    rsi   = 100 - (100 / (1 + rs))

    # Moving averages
    ma_20 = close.rolling(20).mean()
    ma_50 = close.rolling(50).mean()

    # VWAP deviation (daily session approximation)
    typical_price = (bars["high"] + bars["low"] + bars["close"]) / 3
    vwap          = (typical_price * volume).cumsum() / volume.cumsum()
    vwap_dev      = (close.iloc[-1] - vwap.iloc[-1]) / vwap.iloc[-1]

    return {
        "rsi_14":         round(float(rsi.iloc[-1]), 2),
        "ma_20":          round(float(ma_20.iloc[-1]), 2),
        "ma_50":          round(float(ma_50.iloc[-1]), 2),
        "ma_cross":       "bullish" if ma_20.iloc[-1] > ma_50.iloc[-1] else "bearish",
        "vwap_deviation": round(float(vwap_dev), 4),
    }
```

### News Fetching

```python
def get_news(symbol: str, limit: int = 5) -> list[dict]:
    req  = StockNewsRequest(symbols=[symbol], limit=limit)
    news = data_client.get_stock_news(req)
    return [
        {"headline": n.headline, "summary": n.summary[:200], "created_at": str(n.created_at)}
        for n in news
    ]
```

### Account State

```python
def get_account_state() -> dict:
    account   = trade_client.get_account()
    positions = trade_client.get_all_positions()
    return {
        "cash":          float(account.cash),
        "equity":        float(account.equity),
        "buying_power":  float(account.buying_power),
        "open_positions": [
            {"symbol": p.symbol, "qty": float(p.qty), "unrealized_pl": float(p.unrealized_pl)}
            for p in positions
        ]
    }
```

### Full Snapshot Builder

```python
def build_market_snapshot(symbol: str) -> dict:
    bars       = get_price_bars(symbol)
    indicators = compute_indicators(bars)
    news       = get_news(symbol)
    account    = get_account_state()

    current_price  = float(bars["close"].iloc[-1])
    prev_close     = float(bars["close"].iloc[-2])
    change_pct     = (current_price - prev_close) / prev_close * 100

    open_position = next(
        (p for p in account["open_positions"] if p["symbol"] == symbol), None
    )

    return {
        "symbol":          symbol,
        "price":           round(current_price, 2),
        "change_pct":      round(change_pct, 2),
        "volume":          int(bars["volume"].iloc[-1]),
        **indicators,
        "news":            news,
        "open_position":   open_position,
        "cash_available":  account["cash"],
        "portfolio_equity": account["equity"],
    }
```

---

## Watchlist Configuration

Define your universe in `watchlist.json` — not hardcoded in the script:

```json
{
  "symbols": [
    { "ticker": "NVDA", "max_allocation_pct": 5, "note": "AI/GPU exposure" },
    { "ticker": "AAPL", "max_allocation_pct": 5, "note": "Defensive tech" },
    { "ticker": "SPY",  "max_allocation_pct": 8, "note": "Market hedge" },
    { "ticker": "TSLA", "max_allocation_pct": 3, "note": "High vol — smaller sizing" }
  ],
  "cash_reserve_pct": 20
}
```

---

## Token Cost Control

| Technique | Impact |
|---|---|
| Cap bars at 60 (not 500) | ~70% context reduction |
| Truncate news summaries to 200 chars | ~60% news token reduction |
| Summarize journal before passing back | Keeps history manageable |
| Use structured JSON (not prose) | Reliable parsing, no ambiguity |

---

## Sources

- [MindStudio: Build a 24/7 AI Trading Agent with Claude Code and Alpaca](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca)
- [Tradewink: Build an AI Trading Agent with Alpaca API](https://www.tradewink.com/learn/build-ai-agent-alpaca-tutorial)
- [YouTube: How To Build A Self-Improving AI Trading Agent](https://www.youtube.com/watch?v=6njREUQAFdg)
