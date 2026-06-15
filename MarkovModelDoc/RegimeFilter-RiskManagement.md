# Regime Filter & Risk Management

> Back to strategy hub: [[HiddenMarkovTrading]]  
> Source: [QuantStart: Market Regime Detection using HMMs in QSTrader](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)

---

## The Core Idea

The regime filter does not generate signals — it **gates** them. A signal that passes through the entry logic is still rejected if the HMM predicts a high-volatility or bear regime.

This is the single most impactful addition the HMM makes to a base strategy:

| Metric | Without Filter | With Filter |
|---|---|---|
| Sharpe Ratio | 0.37 | 0.48 |
| Max Drawdown | ~56% | ~24% |
| CAGR | 6.41% | 6.88% |
| Total Trades | 41 | 31 |

The filter rejected ~25% of trades — the ones that happened during high-volatility regimes. Those were the trades responsible for the catastrophic drawdown.

---

## Risk Manager Architecture (QSTrader Pattern)

The `RegimeHMMRiskManager` intercepts order signals before they reach execution:

```python
class RegimeHMMRiskManager:
    def __init__(self, model, price_handler, low_vol_state=0):
        self.model = model
        self.price_handler = price_handler
        self.low_vol_state = low_vol_state   # the "safe" regime index
        self.invested = False

    def refine_orders(self, order_event):
        """
        Called before every order is submitted.
        Returns the order unchanged (allow) or None (block).
        """
        regime = self._predict_current_regime()

        if order_event.direction == "BOT":   # entering long
            if regime == self.low_vol_state and not self.invested:
                self.invested = True
                return order_event           # allow entry
            else:
                return None                  # block entry in bad regime

        if order_event.direction == "SLD":   # exiting
            if self.invested:
                self.invested = False
                return order_event           # always allow exits

        return None

    def _predict_current_regime(self):
        recent_returns = self.price_handler.get_recent_returns(lookback=60)
        features = np.array(recent_returns).reshape(-1, 1)
        return self.model.predict(features)[-1]
```

Key rules:
- **Entries** are only allowed in the low-volatility (Bull) regime
- **Exits** are always allowed regardless of regime (never trap in a position)
- The model is re-queried on every bar (uses rolling lookback window)

---

## Position Sizing by Regime

Beyond blocking/allowing trades, regime confidence can scale position size:

```python
def compute_position_size(
    base_size: float,
    signal: float,          # from [[SignalGeneration]], range [-1, +1]
    regime_proba: np.ndarray,
    label_map: dict,
    max_leverage: float = 1.0,
) -> float:
    bull_states = [s for s, l in label_map.items() if l == "Bull"]
    bull_confidence = regime_proba[bull_states].sum()

    # Scale: full size only at peak bull confidence
    size = base_size * bull_confidence * max(signal, 0)
    return min(size, base_size * max_leverage)
```

The follow-on video ([I Built the Viral Claude Code Trading Strategy Properly](https://www.youtube.com/watch?v=NQpAqaJrm7U)) uses **2.5× leverage** in high-confidence bull regimes with proper transaction costs.

---

## Stop-Loss Integration

The regime state can inform dynamic stop placement:

```python
def get_stop_distance(regime: str, atr: float) -> float:
    multipliers = {
        "Bull":     1.5,    # tight stops in trending market
        "Bear":     3.0,    # wider stops (or don't trade at all)
        "Sideways": 2.0,    # medium stop for range trades
    }
    return multipliers.get(regime, 2.0) * atr
```

---

## Regime-Gated Conviction Threshold

An alternative to hard blocking: require higher signal confidence in uncertain regimes.

```python
CONVICTION_THRESHOLDS = {
    "Bull":     0.53,   # low bar — regime is favorable
    "Sideways": 0.60,   # medium bar
    "Bear":     0.70,   # high bar — only very strong signals
}

def should_trade(signal_confidence: float, current_regime: str) -> bool:
    threshold = CONVICTION_THRESHOLDS.get(current_regime, 0.60)
    return signal_confidence > threshold
```

This is the approach used by the QuantInsti walk-forward implementation.

---

## 2008 Financial Crisis — Why This Matters

The HMM filter avoided most of the 2008–2009 bear market because:
1. Volatility spiked sharply in late 2007 → HMM switched to high-vol state
2. The risk manager blocked all long entries from late 2007 through early 2009
3. The SMA strategy attempted ~10 longs during this period that would have lost heavily
4. All were rejected by the filter

This is the real-world proof case for why the drawdown dropped from 56% to 24%.

---

## Related Files

- [[HMM-Theory]] — how the model identifies regimes
- [[MarketRegimes]] — Bull / Bear / Sideways definitions
- [[SignalGeneration]] — the signals being filtered
- [[Backtesting]] — validating the filter's impact out-of-sample

---

## Sources

- [QuantStart: Market Regime Detection using HMMs in QSTrader](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)
- [QuantInsti: Market Regime using Hidden Markov Model](https://blog.quantinsti.com/regime-adaptive-trading-python/)
- [YouTube: I Built the Viral Claude Code Trading Strategy Properly](https://www.youtube.com/watch?v=NQpAqaJrm7U)
