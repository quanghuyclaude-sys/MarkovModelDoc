# Markov Hedge Fund Method — The Video Strategy

> Back to strategy hub: [[HiddenMarkovTrading]]  
> Original video (Claude Code): [I Re-Created A Quant Trading Strategy With Claude Code](https://www.youtube.com/watch?v=ZVMTeDBmSrI&t=1134s)  
> Rebuild video (Fable 5): [I Re-Built A Quant Trading Strategy With Fable 5](https://www.youtube.com/watch?v=Z-hU97WO30I)  
> GitHub: [jackson-video-resources/markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method)  
> Original framework by Roan ([@RohOnChain](https://x.com/RohOnChain)) — quant trader, 47.3K followers on X

---

## About Roan (@RohOnChain)

Roan is a quant trader building around institutional-level quant systems in **prediction markets and crypto**. He joined X in September 2025 and has 47.3K followers. His published work spans:

| Topic | What He Shared |
|---|---|
| **Markov regime detection** | The original framework packaged in this repo |
| **NN + HMM hybrid** | Research showing $100k → $182,761 (83% return) using Neural Networks + Hidden Markov Models on live markets — [X post](https://x.com/RohOnChain/status/2052798873371037833) |
| **MIT Financial Mathematics** | Rewired MIT course content for Polymarket traders |
| **Polymarket arbitrage** | Frank-Wolfe + Bregman Projection algorithm; Kelly Criterion position sizing; Gurobi integer programming for multi-market arb |
| **Quant research** | Shared "151 Trading Strategies" (Kakushadze & Serur, 361 pages, 550+ formulas, covers NN/Bayes/k-NN strategies) |
| **Insider detection** | USC mathematicians paper — 43-page game theory framework for detecting smart-money moves before announcements |

His X content style: shares academic/institutional research and breaks it down with explicit math and tradeable systems.

---

## Fable 5 Rebuild (June 2026)

Lewis Jackson re-built this same strategy using **Claude Fable 5** (`claude-fable-5`, released June 9, 2026). Key model specs relevant to running this skill:

| Property | Value |
|---|---|
| Model ID | `claude-fable-5` |
| Context window | 1M tokens |
| Max output | 128k tokens |
| Pricing | $10 / M input · $50 / M output |
| Thinking | Adaptive (always on, cannot disable) |
| Safety | Classifiers active — may return `stop_reason: "refusal"` |

The strategy logic, GitHub repo, and skill files are unchanged from the original. Fable 5 can build the skill faster and handles longer backtesting sessions within a single context.

---

## Overview

This is the specific strategy reconstructed in the video using Claude Code. It is a **Markov regime detection skill** that:

1. Classifies daily returns into Bull / Bear / Sideways
2. Builds a state transition matrix from historical data
3. Forecasts future regime probabilities via Chapman-Kolmogorov
4. Generates a directional signal (bull probability − bear probability)
5. Runs walk-forward backtests reporting Sharpe ratio and max drawdown
6. Optionally fits a full Gaussian HMM for deeper inference

---

## Installation

### Option A — Claude Code Plugin (Recommended)
```
/plugin marketplace add jackson-video-resources/markov-hedge-fund-method
/plugin install markov-hedge-fund-method@markov-hedge-fund-method
```

### Option B — Manual Build from Prompt
Use the `markov-hedge-fund-method.md` file in the repo as a one-shot prompt in Claude Code. It builds the skill from scratch, giving full transparency into what is being created.

**Zero external dependency install** — uses `uv` with inline PEP 723 metadata for automatic dependency resolution. No manual `pip install` required.

---

## Inputs

| Input | Description |
|---|---|
| Ticker symbol | Any symbol supported by `yfinance` (e.g., `SPY`, `BTC-USD`) |
| Custom CSV | Must contain `date` and `close` columns |
| Window size | Rolling window for regime classification (default: 20 days) |
| Thresholds | ±5% for Bull/Bear classification (configurable) |

---

## Core Pipeline

### Step 1 — Data Fetch
```python
import yfinance as yf
data = yf.download("SPY", start="2010-01-01", end="2024-01-01")
returns = data["Close"].pct_change().dropna()
```

### Step 2 — Regime Classification (Rolling Window)
```python
window = 20
rolling_return = returns.rolling(window).sum()

regimes = pd.Series(index=returns.index, dtype=str)
regimes[rolling_return > 0.05]  = "Bull"
regimes[rolling_return < -0.05] = "Bear"
regimes[
    (rolling_return >= -0.05) & (rolling_return <= 0.05)
] = "Sideways"
```

### Step 3 — Build Transition Matrix
```python
# Count transitions between consecutive regime labels
from collections import defaultdict
transitions = defaultdict(lambda: defaultdict(int))

prev = None
for state in regimes.dropna():
    if prev:
        transitions[prev][state] += 1
    prev = state

# Normalize rows to get probabilities
states = ["Bull", "Bear", "Sideways"]
A = pd.DataFrame(index=states, columns=states, dtype=float)
for s in states:
    total = sum(transitions[s].values())
    for t in states:
        A.loc[s, t] = transitions[s][t] / total if total > 0 else 0
```

### Step 4 — Chapman-Kolmogorov Forecast
```python
import numpy as np

A_matrix = A.values
current_state_vector = np.array([1, 0, 0])  # currently in Bull

# Probability distribution N steps ahead
def forecast(state_vec, A, steps):
    for _ in range(steps):
        state_vec = state_vec @ A
    return state_vec

probs_5d = forecast(current_state_vector, A_matrix, steps=5)
# probs_5d = [P(Bull), P(Bear), P(Sideways)] in 5 days
```

### Step 5 — Directional Signal
```python
signal = probs_5d[0] - probs_5d[1]   # Bull prob - Bear prob
# signal > 0: bullish lean
# signal < 0: bearish lean
```

### Step 6 — Stationary Distribution
```python
from numpy.linalg import eig

vals, vecs = eig(A_matrix.T)
stationary = np.real(vecs[:, np.isclose(vals, 1)])
stationary = stationary / stationary.sum()
print(dict(zip(states, stationary.flatten())))
```

---

## Outputs

| Output | Description |
|---|---|
| Regime labels | Historical Bull/Bear/Sideways label per bar |
| Transition matrix | 3×3 probability table |
| Stationary distribution | Long-run time in each regime |
| Directional signal | Scalar from -1 to +1 |
| Sharpe ratio | Backtest performance metric |
| Max drawdown | Worst peak-to-trough loss |

---

## Companion TradingView Indicator

A Pine Script indicator is included in the repository. It renders:
- Regime ribbons (color-coded background by current regime)
- Transition matrix as an on-chart table
- Directional signal as an oscillator

See [[TradingViewPineScript]] for usage.

---

## Related Files

- [[HMM-Theory]] — mathematical foundation
- [[MarketRegimes]] — regime classification details
- [[HMM-Implementation-Python]] — full hmmlearn-based implementation
- [[Backtesting]] — walk-forward validation

---

## Sources

- [YouTube: I Re-Created A Quant Trading Strategy With Claude Code](https://www.youtube.com/watch?v=ZVMTeDBmSrI&t=1134s)
- [YouTube: I Re-Built A Quant Trading Strategy With Fable 5](https://www.youtube.com/watch?v=Z-hU97WO30I)
- [GitHub: markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method)
- [YouTube: I Built the Viral Claude Code Trading Strategy Properly](https://www.youtube.com/watch?v=NQpAqaJrm7U)
