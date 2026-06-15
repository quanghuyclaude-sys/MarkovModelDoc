# Backtesting — Walk-Forward Validation

> Back to strategy hub: [[HiddenMarkovTrading]]
> Sources: [QuantStart: Market Regime Detection using HMMs](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/) · [QuantInsti: Market Regime using HMM](https://blog.quantinsti.com/regime-adaptive-trading-python/)

---

## Why Walk-Forward (Not Simple Backtest)

A simple train/test split overfits because market regimes are non-stationary. Walk-forward backtesting rolls a training window through history and retests on each unseen slice — the closest approximation to live trading.

- Model trained on 2000–2010 may not describe 2020–2024 regimes
- Walk-forward simulates how the strategy actually retrains in production

---

## Walk-Forward Architecture

```
|--- Training Window (4 years) ---|-- Test Slice (1 yr) --|
                 |--- Training Window (4 years) ---|-- Test Slice --|
                              |--- Training Window ---|-- Test Slice --|
```

At each step: fit HMM on training window → predict regimes on test slice → run signals → record metrics → slide forward.

---

## Implementation

```python
import numpy as np
import pandas as pd
from hmmlearn import hmm

def walk_forward_backtest(
    data: pd.DataFrame,
    train_years: int = 4,
    test_years: int = 1,
    n_states: int = 3,
    transaction_cost: float = 0.001,
) -> pd.Series:

    DAYS = 252
    train_size = train_years * DAYS
    test_size  = test_years  * DAYS
    returns    = data["Close"].pct_change().dropna()
    results    = []

    start = 0
    while start + train_size + test_size <= len(returns):
        X_train = returns.iloc[start:start + train_size].values.reshape(-1, 1)

        model = hmm.GaussianHMM(
            n_components=n_states, covariance_type="full",
            n_iter=100, random_state=42
        )
        model.fit(X_train)

        test_slice = returns.iloc[start + train_size:start + train_size + test_size]
        X_full     = np.vstack([X_train, test_slice.values.reshape(-1, 1)])
        states     = model.predict(X_full)[train_size:]
        bull_state = int(np.argsort(model.means_.flatten())[-1])

        positions = pd.Series(
            [1.0 if s == bull_state else 0.0 for s in states],
            index=test_slice.index
        )
        trades           = positions.diff().abs().fillna(0)
        strategy_returns = (positions.shift(1) * test_slice) - (trades * transaction_cost)
        results.append(strategy_returns)
        start += test_size

    return pd.concat(results)
```

---

## Performance Metrics

```python
def compute_metrics(r: pd.Series) -> dict:
    annual_return = (1 + r).prod() ** (252 / len(r)) - 1
    annual_vol    = r.std() * 252 ** 0.5
    sharpe        = annual_return / annual_vol if annual_vol else 0
    cum           = (1 + r).cumprod()
    max_dd        = ((cum - cum.cummax()) / cum.cummax()).min()
    return {"sharpe": round(sharpe, 3), "max_dd": round(max_dd, 3),
            "cagr": round(annual_return, 3), "trades": int((r != 0).sum())}
```

---

## Published Results Benchmark

| Setup | Sharpe | Max Drawdown | CAGR | Trades |
|---|---|---|---|---|
| SMA crossover only | 0.37 | -56% | 6.41% | 41 |
| SMA + HMM filter | 0.48 | -24% | 6.88% | 31 |

Source: [QuantStart](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)

---

## Transaction Costs (Real Binance Costs)

```python
TAKER_FEE      = 0.001    # 0.10% per side
SLIPPAGE       = 0.0005   # 0.05%
ROUND_TRIP     = TAKER_FEE * 2 + SLIPPAGE   # 0.25%
```

From: [I Built the Viral Claude Code Trading Strategy Properly](https://www.youtube.com/watch?v=NQpAqaJrm7U)

---

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Look-ahead bias | Only use data available at each bar |
| Fitting on full history | Walk-forward only — retrain on past data |
| Ignoring costs | Include 0.1%+ round-trip |
| Single-asset testing | Validate on held-out asset or period |

---

## Related Files

- [[MarkovHedgeFundMethod]] — strategy being backtested
- [[RegimeFilter-RiskManagement]] — filter being validated
- [[SignalGeneration]] — signals being tested
- [[HMM-Implementation-Python]] — model fitting inside the loop

---

## Sources

- [QuantStart: Market Regime Detection using HMMs in QSTrader](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)
- [QuantInsti: Market Regime using Hidden Markov Model](https://blog.quantinsti.com/regime-adaptive-trading-python/)
- [YouTube: I Built the Viral Claude Code Trading Strategy Properly](https://www.youtube.com/watch?v=NQpAqaJrm7U)
