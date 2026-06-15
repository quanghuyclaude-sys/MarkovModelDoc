# VWAP + RSI(3) + EMA(8) Scalping Strategy

> Back to: [[ZeroOne-ResourceHub]]
> Source: [rules.json — claude-tradingview-mcp-trading](https://github.com/jackson-video-resources/claude-tradingview-mcp-trading/blob/main/rules.json)
> Based on: van de Poppe + Tone Vays BTC methodology

---

## Strategy Summary

A crypto scalping strategy for BTCUSDT on 1-minute candles using three synchronized
indicators. All three conditions must align before any entry. Designed for high-frequency
mean-reversion within the dominant intraday trend.

---

## The Three Indicators

### EMA(8) — Trend Direction Filter
- Price **above** EMA(8) = bullish bias (longs only)
- Price **below** EMA(8) = bearish bias (shorts only)
- Acts as a trend gate — no counter-trend trades

### VWAP — Session Bias Anchor
- Resets at midnight UTC each session
- Price **above** VWAP = buyers in control
- Price **below** VWAP = sellers in control
- Confirms EMA direction at the session level

### RSI(3) — Entry Timer
- Uses only 3 candles — extremely sensitive
- Catches micro pullbacks within the trend
- Long trigger: RSI(3) drops **below 30** (oversold pullback)
- Short trigger: RSI(3) spikes **above 70** (overbought pullback)

---

## Entry Conditions

### Long Entry (all 3 required)
```
Price > VWAP         (session bias: buyers in control)
Price > EMA(8)       (trend direction: bullish)
RSI(3) < 30          (pullback entry: oversold on micro timeframe)
```

### Short Entry (all 3 required)
```
Price < VWAP         (session bias: sellers in control)
Price < EMA(8)       (trend direction: bearish)
RSI(3) > 70          (pullback entry: overbought on micro timeframe)
```

---

## Exit Conditions

| Exit Trigger | Description |
|---|---|
| RSI(3) crosses 50 | Primary exit — momentum normalized |
| Price touches VWAP | Take partial profit at session anchor |
| Price touches EMA(8) | Take partial profit at trend line |
| Hard stop: 0.3% from entry | Maximum loss per trade |

---

## Risk Parameters (from rules.json)

| Parameter | Value |
|---|---|
| Asset | BTCUSDT |
| Timeframe | 1-minute candles |
| Max risk per trade | 1% of portfolio |
| Max position size | `MAX_TRADE_SIZE_USD` (env variable) |
| Max trades per day | `MAX_TRADES_PER_DAY` (env variable) |
| Hard stop distance | 0.3% from entry |
| VWAP distance filter | No trade if price > 1.5% from VWAP |

The VWAP distance filter prevents entries during fast breakout moves — conditions
where this strategy is most likely to fail.

---

## rules.json Structure

```json
{
  "strategy": "VWAP + RSI(3) + EMA(8) Scalping",
  "asset": "BTCUSDT",
  "timeframe": "1m",
  "description": "EMA(8) for trend direction, VWAP for session bias, RSI(3) for entry timing",
  "indicators": {
    "ema_period": 8,
    "rsi_period": 3,
    "vwap_reset": "midnight_utc"
  },
  "long_conditions": {
    "price_above_vwap": true,
    "price_above_ema": true,
    "rsi_below": 30
  },
  "short_conditions": {
    "price_below_vwap": true,
    "price_below_ema": true,
    "rsi_above": 70
  },
  "exits": {
    "rsi_cross_50": true,
    "touch_vwap": true,
    "touch_ema": true
  },
  "risk": {
    "stop_pct": 0.003,
    "max_vwap_distance_pct": 0.015,
    "max_portfolio_risk_pct": 0.01
  }
}
```

---

## Building a Custom rules.json From Any YouTuber

Lewis Jackson provides a workflow to convert any trading YouTuber into a rules.json:

1. Use [Apify YouTube Transcript Scraper](https://apify.com) on the target channel
2. Feed the transcript into `prompts/01-extract-strategy.md` in Claude Code
3. Claude extracts the strategy and generates a rules.json
4. Drop into [[ClaudeTradingView-Bot]] or [[TradingView-MCP]] for execution

The [[YT-StrategyAgent]] automates this entire process on a 10-minute cycle.

---

## Combining With HMM Regime Filter

The VWAP/RSI(3)/EMA(8) strategy works best in trending regimes. Add the HMM
regime score as a fourth condition to block trades during Bear or Sideways periods:

```json
{
  "additional_conditions": {
    "hmm_regime": "Bull",
    "hmm_signal_score_min": 0.5
  }
}
```

See [[HiddenMarkovTrading]] for the regime detection system that generates this score.

---

## Sources

- [rules.json — claude-tradingview-mcp-trading](https://github.com/jackson-video-resources/claude-tradingview-mcp-trading/blob/main/rules.json)
- [GitHub: claude-tradingview-mcp-trading](https://github.com/jackson-video-resources/claude-tradingview-mcp-trading)
- [ZeroOne Systems](https://www.skool.com/zero-one)
