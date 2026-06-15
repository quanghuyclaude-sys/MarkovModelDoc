# HMM Implementation in Python

> Back to strategy hub: [[HiddenMarkovTrading]]  
> Sources: [MarketCalls: Introduction to HMM for Traders](https://www.marketcalls.in/python/introduction-to-hidden-markov-models-hmm-for-traders-python-tutorial.html) · [QuantStart: Market Regime Detection using HMMs](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)

---

## Dependencies

```bash
pip install yfinance pandas numpy hmmlearn scikit-learn plotly ta
```

Or zero-config via `uv` (see [[MarkovHedgeFundMethod]]).

---

## Full Implementation

### 1. Data Fetching

```python
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def fetch_data(symbol: str, days: int = 3650, interval: str = "1d") -> pd.DataFrame:
    end = datetime.now()
    start = end - timedelta(days=days)
    data = yf.download(symbol, start=start, end=end, interval=interval)
    data["returns"] = data["Close"].pct_change()
    data["log_returns"] = np.log(data["Close"] / data["Close"].shift(1))
    data.dropna(inplace=True)
    return data
```

### 2. Feature Engineering

```python
def build_features(data: pd.DataFrame, window: int = 12) -> np.ndarray:
    """
    Returns shape (n_samples, 1) — rate of change of closing price.
    Extend with more columns for richer regime detection (see MacroFeatures).
    """
    roc = data["Close"].pct_change(periods=window).dropna()
    return roc.values.reshape(-1, 1), roc.index
```

### 3. Fitting the Gaussian HMM

```python
from hmmlearn import hmm

def fit_hmm(features: np.ndarray, n_states: int = 3, n_iter: int = 100) -> hmm.GaussianHMM:
    model = hmm.GaussianHMM(
        n_components=n_states,
        covariance_type="full",   # each state gets its own covariance matrix
        n_iter=n_iter,
        random_state=42,
    )
    model.fit(features)
    return model
```

**Covariance types:**
| Type | Description | Use when |
|---|---|---|
| `"spherical"` | Single variance per state | Fast, few data points |
| `"diag"` | Diagonal covariance | Multiple features, independent |
| `"full"` | Full covariance matrix | Multiple correlated features |
| `"tied"` | Same covariance for all states | Assumes similar dispersion |

### 4. Predicting Hidden States

```python
def predict_regimes(model: hmm.GaussianHMM, features: np.ndarray) -> np.ndarray:
    return model.predict(features)           # Viterbi — most likely sequence
    # model.predict_proba(features)          # soft probabilities per state
```

### 5. Labeling Regimes

```python
def label_regimes(model: hmm.GaussianHMM, states: np.ndarray) -> dict:
    """
    Assign human-readable labels by comparing state means.
    The state with the highest mean return = Bull.
    """
    means = model.means_.flatten()
    order = np.argsort(means)               # ascending
    labels = {}
    labels[order[0]] = "Bear"
    labels[order[-1]] = "Bull"
    if len(order) == 3:
        labels[order[1]] = "Sideways"
    return labels
```

### 6. Signal Generation

```python
def generate_signals(model, features, label_map) -> pd.Series:
    proba = model.predict_proba(features)   # shape: (n_samples, n_states)
    
    bull_states = [s for s, l in label_map.items() if l == "Bull"]
    bear_states = [s for s, l in label_map.items() if l == "Bear"]
    
    bull_prob = proba[:, bull_states].sum(axis=1)
    bear_prob = proba[:, bear_states].sum(axis=1)
    
    signal = bull_prob - bear_prob          # range [-1, +1]
    return signal
```

See [[SignalGeneration]] for full entry/exit logic.

### 7. Full Pipeline

```python
def run_hmm_strategy(ticker: str = "SPY", n_states: int = 3):
    data = fetch_data(ticker)
    features, idx = build_features(data)
    model = fit_hmm(features, n_states=n_states)
    
    states = predict_regimes(model, features)
    label_map = label_regimes(model, states)
    
    regime_series = pd.Series(
        [label_map[s] for s in states], index=idx, name="regime"
    )
    signal_series = pd.Series(
        generate_signals(model, features, label_map), index=idx, name="signal"
    )
    
    result = data.loc[idx].copy()
    result["regime"] = regime_series
    result["signal"] = signal_series
    return result, model

result, model = run_hmm_strategy("SPY", n_states=3)
print(result[["Close", "regime", "signal"]].tail(20))
```

---

## Visualization

```python
import plotly.graph_objects as go

def plot_regimes(result: pd.DataFrame):
    colors = {"Bull": "green", "Bear": "red", "Sideways": "gray"}
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=result.index, y=result["Close"],
        mode="lines", name="Price", line=dict(color="white", width=1)
    ))
    
    for regime, color in colors.items():
        mask = result["regime"] == regime
        fig.add_trace(go.Scatter(
            x=result.index[mask], y=result["Close"][mask],
            mode="markers",
            marker=dict(color=color, size=4, opacity=0.5),
            name=regime
        ))
    
    # Signal oscillator
    fig.add_trace(go.Scatter(
        x=result.index, y=result["signal"],
        mode="lines", name="Signal", yaxis="y2",
        line=dict(color="yellow", width=1)
    ))
    
    fig.update_layout(
        title="HMM Regime Detection",
        template="plotly_dark",
        yaxis2=dict(overlaying="y", side="right", range=[-1, 1])
    )
    fig.show()
```

---

## Model Selection — Choosing n_states

```python
from hmmlearn import hmm

def select_n_states(features, max_states=5):
    scores = {}
    for n in range(2, max_states + 1):
        model = hmm.GaussianHMM(n_components=n, n_iter=100, random_state=42)
        model.fit(features)
        # AIC = -2 * log_likelihood + 2 * n_params
        # BIC = -2 * log_likelihood + log(n) * n_params
        scores[n] = model.score(features)   # log-likelihood
    return scores
```

Lower AIC/BIC = better model complexity tradeoff. Typically 2–3 states work best for daily equity data.

---

## Related Files

- [[HMM-Theory]] — mathematics behind the algorithms
- [[MarketRegimes]] — how to interpret states
- [[SignalGeneration]] — turning state probabilities into trades
- [[RegimeFilter-RiskManagement]] — blocking entries in bad regimes
- [[Backtesting]] — walk-forward validation setup
- [[MacroFeatures]] — enriching the feature set

---

## Sources

- [MarketCalls: Introduction to HMM for Traders (Python Tutorial)](https://www.marketcalls.in/python/introduction-to-hidden-markov-models-hmm-for-traders-python-tutorial.html)
- [QuantStart: Market Regime Detection using HMMs in QSTrader](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)
- [QuantInsti: Market Regime using Hidden Markov Model](https://blog.quantinsti.com/regime-adaptive-trading-python/)
