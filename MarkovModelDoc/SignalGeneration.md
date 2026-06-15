# Signal Generation — Entry & Exit Logic

> Back to strategy hub: [[HiddenMarkovTrading]]  
> Sources: [MarketCalls: Introduction to HMM for Traders](https://www.marketcalls.in/python/introduction-to-hidden-markov-models-hmm-for-traders-python-tutorial.html) · [QuantStart: Market Regime Detection using HMMs](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)

---

## Two Signal Layers

The full system combines two signal sources:

| Layer | Source | Role |
|---|---|---|
| **Primary signal** | SMA crossover / momentum indicator | Determines trade direction |
| **Regime gate** | HMM state probability | Filters whether to act on the primary signal |

Neither layer alone is sufficient. The primary signal is noisy. The regime gate alone has no timing precision.

---

## Layer 1 — Primary Signal: SMA Crossover

From the QuantStart QSTrader implementation:

```python
from collections import deque

class SMACrossoverSignal:
    def __init__(self, short_window=10, long_window=30):
        self.short_prices = deque(maxlen=short_window)
        self.long_prices  = deque(maxlen=long_window)
        self.invested = False

    def update(self, price: float) -> str | None:
        self.short_prices.append(price)
        self.long_prices.append(price)

        if len(self.long_prices) < self.long_prices.maxlen:
            return None    # not enough data yet

        sma_short = sum(self.short_prices) / len(self.short_prices)
        sma_long  = sum(self.long_prices)  / len(self.long_prices)

        if sma_short > sma_long and not self.invested:
            self.invested = True
            return "BUY"
        elif sma_long >= sma_short and self.invested:
            self.invested = False
            return "SELL"
        return None
```

**Parameters:**
- Short window: 10 days
- Long window: 30 days
- Signal: `BUY` when 10-day SMA crosses above 30-day SMA

---

## Layer 2 — Regime Signal: Directional Score

From the markov-hedge-fund-method:

```python
def compute_directional_signal(
    model,          # fitted GaussianHMM
    features,       # recent observations, shape (n, 1+)
    label_map,      # {state_index: "Bull"|"Bear"|"Sideways"}
) -> float:
    proba = model.predict_proba(features)[-1]   # latest bar's state probs

    bull_idx  = [k for k, v in label_map.items() if v == "Bull"]
    bear_idx  = [k for k, v in label_map.items() if v == "Bear"]

    bull_prob = sum(proba[i] for i in bull_idx)
    bear_prob = sum(proba[i] for i in bear_idx)

    return bull_prob - bear_prob   # range: [-1.0, +1.0]
```

---

## Combined Signal Logic

```python
CONVICTION_THRESHOLD = 0.53   # minimum net bull probability to allow a trade

def generate_final_signal(
    primary_signal: str | None,    # "BUY", "SELL", or None
    directional_score: float,       # range [-1, +1]
) -> str | None:

    if primary_signal == "BUY":
        if directional_score > CONVICTION_THRESHOLD:
            return "BUY"          # regime confirms — execute
        else:
            return None           # regime disagrees — skip

    if primary_signal == "SELL":
        return "SELL"             # always honour exits regardless of regime

    return None
```

---

## 3-State Signal Mapping (hmmlearn)

When using hmmlearn directly with 3 states, map predicted states to signals:

```python
def map_state_to_signal(state: int, label_map: dict) -> int:
    regime = label_map.get(state, "Sideways")
    mapping = {
        "Bull":     1,    # go long
        "Bear":    -1,    # go flat / short
        "Sideways": 0,    # no action
    }
    return mapping[regime]

# Example applied to a series:
signals = pd.Series(
    [map_state_to_signal(s, label_map) for s in hidden_states],
    index=feature_index
)
```

---

## Signal Smoothing

Raw HMM signals can flip frequently. Smooth with a rolling mode:

```python
def smooth_signals(signals: pd.Series, window: int = 3) -> pd.Series:
    return signals.rolling(window).apply(
        lambda x: pd.Series(x).mode()[0]
    ).fillna(0).astype(int)
```

---

## Position Entry Rules (Complete)

| Condition | Action |
|---|---|
| SMA(10) > SMA(30) AND signal score > 0.53 AND not invested | Enter Long |
| SMA(30) > SMA(10) AND invested | Exit Long |
| Signal score < -0.53 AND invested | Emergency exit |
| Signal score < 0 AND not invested | Do not enter |
| High-volatility regime detected | Block all new entries (see [[RegimeFilter-RiskManagement]]) |

---

## Exit Rules

```python
def should_exit(
    sma_signal: str,
    directional_score: float,
    current_drawdown: float,
    max_allowed_drawdown: float = 0.15,
) -> bool:
    if sma_signal == "SELL":
        return True
    if directional_score < -0.30:    # regime deteriorating fast
        return True
    if current_drawdown > max_allowed_drawdown:
        return True
    return False
```

---

## Related Files

- [[MarkovHedgeFundMethod]] — the specific implementation from the video
- [[RegimeFilter-RiskManagement]] — how signals are gated
- [[HMM-Implementation-Python]] — generating regime probabilities
- [[Backtesting]] — testing signal quality out-of-sample

---

## Sources

- [MarketCalls: Introduction to HMM for Traders (Python Tutorial)](https://www.marketcalls.in/python/introduction-to-hidden-markov-models-hmm-for-traders-python-tutorial.html)
- [QuantStart: Market Regime Detection using HMMs in QSTrader](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)
- [GitHub: markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method)
