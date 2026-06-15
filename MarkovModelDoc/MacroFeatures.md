# Macro Features — Enriching HMM Inputs

> Back to strategy hub: [[HiddenMarkovTrading]]
> Source: [PyQuantLab: Regime-Aware Trading with HMMs and Macro Features](https://pyquantlab.medium.com/regime-aware-trading-with-hidden-markov-models-hmms-and-macro-features-c75f6d357880)

---

## Why More Features Than Just Returns?

A single-feature HMM (daily returns only) misses cross-asset information that is visible to macro traders. Adding macro features allows the model to distinguish regimes that look similar in price alone but are structurally different.

Example: Two low-volatility periods — one with VIX at 12, one with VIX at 28 (artificially suppressed). A returns-only HMM labels both "Bull." A macro-aware HMM can separate them.

---

## The Five Core Features (PyQuantLab Setup)

| Feature | What It Measures | Why It Helps |
|---|---|---|
| **Returns** | Daily price change | Core regime signal |
| **Volatility** | Rolling std of returns | Distinguishes Bull from noise |
| **VIX** | Implied volatility index | Forward-looking fear gauge |
| **Trend spread** | MA50 − MA200 | Structural trend direction |
| **10-year yield** | US Treasury yield | Risk-on / risk-off macro regime |

---

## Data Acquisition

```python
import yfinance as yf
import pandas as pd
import numpy as np

def fetch_macro_features(equity_ticker: str = "SPY", start: str = "2010-01-01") -> pd.DataFrame:
    equity = yf.download(equity_ticker, start=start)["Close"]
    vix    = yf.download("^VIX",       start=start)["Close"]
    yields = yf.download("^TNX",       start=start)["Close"]  # 10-yr yield proxy

    df = pd.DataFrame()
    df["returns"]    = equity.pct_change()
    df["volatility"] = df["returns"].rolling(20).std()
    df["vix"]        = vix.reindex(df.index, method="ffill")
    df["ma50"]       = equity.rolling(50).mean()
    df["ma200"]      = equity.rolling(200).mean()
    df["trend"]      = (df["ma50"] - df["ma200"]) / df["ma200"]  # normalised
    df["yield_10y"]  = yields.reindex(df.index, method="ffill")
    df.dropna(inplace=True)
    return df
```

---

## Stationarity Check

Non-stationary features cause the HMM to drift. Test each feature:

```python
from statsmodels.tsa.stattools import adfuller

def check_stationarity(df: pd.DataFrame, significance: float = 0.05) -> dict:
    results = {}
    for col in df.columns:
        p_value = adfuller(df[col].dropna())[1]
        stationary = p_value < significance
        if not stationary:
            # Convert to percentage change to induce stationarity
            df[col] = df[col].pct_change()
        results[col] = {"stationary": stationary, "p_value": round(p_value, 4)}
    df.dropna(inplace=True)
    return results

stationarity_report = check_stationarity(df)
```

---

## Feature Matrix for HMM

```python
FEATURES = ["returns", "volatility", "vix", "trend", "yield_10y"]

def build_feature_matrix(df: pd.DataFrame) -> np.ndarray:
    from sklearn.preprocessing import StandardScaler
    X = df[FEATURES].dropna().values
    scaler = StandardScaler()
    return scaler.fit_transform(X), scaler
```

Always standardize features before fitting a Gaussian HMM — otherwise high-variance features dominate the covariance estimation.

---

## Fitting with Multi-Dimensional Features

```python
from hmmlearn import hmm

def fit_macro_hmm(X: np.ndarray, n_states: int = 3) -> hmm.GaussianHMM:
    model = hmm.GaussianHMM(
        n_components=n_states,
        covariance_type="full",   # captures feature correlations
        n_iter=200,
        random_state=42
    )
    model.fit(X)
    return model
```

With 5 features and `covariance_type="full"`, the model learns a 5×5 covariance matrix per state — capturing the correlation structure within each regime.

---

## Regime Interpretation with Macro Features

After fitting, inspect each state's mean vector:

```python
def interpret_states(model, feature_names: list) -> pd.DataFrame:
    means = pd.DataFrame(
        model.means_,
        columns=feature_names,
        index=[f"State {i}" for i in range(model.n_components)]
    )
    return means

# Example output:
#           returns  volatility    vix   trend  yield_10y
# State 0     0.08        0.01   14.2   0.035       2.1    ← Bull
# State 1    -0.12        0.03   28.7  -0.042       3.8    ← Bear
# State 2     0.01        0.01   18.4   0.002       2.6    ← Sideways
```

High VIX + negative trend + high yield = Bear. Low VIX + positive trend = Bull. This confirms the model is learning real macro regimes.

---

## Technical Indicators as Additional Features

```python
from ta import add_all_ta_features

def add_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    enriched = add_all_ta_features(
        df, open="Open", high="High", low="Low",
        close="Close", volume="Volume", fillna=True
    )
    # Select relevant ones:
    features = enriched[["momentum_rsi", "trend_macd", "volatility_bbw"]]
    return features
```

These were used in the QuantInsti walk-forward backtest alongside HMM regime detection.

---

## Feature Importance Insight

| Feature | Regime Separation Power |
|---|---|
| VIX | Very high — best single discriminator |
| Volatility | High |
| Trend spread | Medium — lags reality |
| Returns | Medium — noisy in isolation |
| 10yr yield | Context-dependent (matters in rate cycles) |

---

## Related Files

- [[HMM-Implementation-Python]] — base single-feature implementation
- [[MarketRegimes]] — what the enriched model is detecting
- [[Backtesting]] — walk-forward validation with multi-feature inputs
- [[HMM-Theory]] — why multi-dimensional Gaussians work

---

## Sources

- [PyQuantLab: Regime-Aware Trading with HMMs and Macro Features](https://pyquantlab.medium.com/regime-aware-trading-with-hidden-markov-models-hmms-and-macro-features-c75f6d357880)
- [QuantInsti: Market Regime using Hidden Markov Model](https://blog.quantinsti.com/regime-adaptive-trading-python/)
- [QuantConnect: Intraday Application of Hidden Markov Models](https://www.quantconnect.com/research/17900/intraday-application-of-hidden-markov-models/)
