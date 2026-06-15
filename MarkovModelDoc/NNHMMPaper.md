# NN + HMM Research Paper — AI-Powered Algorithmic Trading

> Source: Shared by Roan (@RohOnChain) on X: [https://x.com/RohOnChain/status/2052798873371037833](https://x.com/RohOnChain/status/2052798873371037833)
> Paper title: *AI-Powered Energy Algorithmic Trading: Integrating Hidden Markov Models with Neural Networks*
> Platform: QuantConnect
> Back to: [[HiddenMarkovTrading]] · [[HMM-Theory]]

---

## Abstract (verbatim from paper)

> "In quantitative finance, machine-learning methods are essential for alpha generation. This study introduces a novel approach that combines Hidden Markov Models (HMM) and neural networks integrated with Black-Litterman portfolio optimization. The approach was tested during the COVID period (2019–2022), where it achieved an 83% return with a Sharpe ratio of 0.77. Two risk models were incorporated to enhance risk management, particularly during the volatile periods. The methodology was implemented on the QuantConnect platform, which was chosen for its robust framework and experimental reproducibility. The system is designed to predict future price movements and includes a three-year warm-up period to ensure the proper functioning of the algorithm. It focuses on highly liquid, large-cap stocks to ensure stable and predictable performance, while also accounting for broker payments. The dual-model alpha system utilizes log returns to select the optimal state based on historical performance. It combines state predictions with neural network outputs derived from historical data to generate trading signals. This study provides an in-depth examination of the trading system's architecture, data pre-processing, training, and performance. The full code and backtesting data are available under QuantConnect's terms."

---

## Key Results

| Metric | Value |
|---|---|
| Return | **83%** |
| Sharpe ratio | **0.77** |
| Start equity | $100,000 |
| End equity | **$182,761.12** |
| Total orders | 40 |
| Average win | 7.70% |
| Average loss | -3.29% |
| Test period | 2019–2022 (COVID period) |

---

## Architecture — Four-Stage Pipeline

```
Start
  │
  ▼
Universe Selection
  │  Highly liquid, large-cap stocks only
  │  Filters for stable and predictable price behavior
  │
  ▼
Alpha Generation  ← HMM + Neural Network (dual-model)
  │  HMM identifies current market regime via log returns
  │  Neural network (PyTorch) generates state predictions
  │  Dual-model combines both outputs as trading signal
  │
  ▼
Portfolio Construction  ← Black-Litterman optimization
  │  Combines model views with market equilibrium
  │  Accounts for broker payments in sizing
  │
  ▼
Risk Management & Execution Models
  │  Two risk models for drawdown control
  │  Particularly active during high-volatility periods
  │
  ▼
End
```

---

## The Dual-Model Alpha System

Two models work in parallel to generate the alpha signal:

### Model 1 — Hidden Markov Model
- Uses **log returns** to classify the current hidden market state
- Selects the optimal state based on historical performance
- Identifies regime (Bull / Bear / Sideways equivalent)

### Model 2 — PyTorch Neural Network
- Multi-layer neural network (architecture visible in paper Figure 4.2.1.2)
- Input layer → multiple hidden layers → output layer
- Learns non-linear state emission functions that the Gaussian HMM cannot capture
- Derives signals from historical data patterns

### Combination
- State predictions from HMM **+** neural network outputs → final trading signal
- This hybrid is what produces the 83% return — neither model alone achieves it
- The NN replaces the Gaussian emission assumption of standard HMM with learned non-linear emissions

---

## Implementation Details

| Detail | Value |
|---|---|
| Platform | QuantConnect |
| Neural network framework | PyTorch |
| Portfolio optimization | Black-Litterman |
| Warm-up period | 3 years (required before live signals) |
| Universe | Highly liquid, large-cap stocks |
| Risk models | 2 (both active during volatile periods) |
| Signal input | Log returns |

---

## Why This Matters for HMM Strategy

This paper provides the academic proof case for the NN+HMM hybrid referenced throughout this library. Key takeaways:

1. **Standard HMM alone is not the ceiling** — adding a neural network for emission modeling materially improves returns (53.55% CAGR with HMM+RF vs 83% with NN+HMM per [[HiddenMarkovTrading]] benchmarks)

2. **The warm-up period is critical** — 3 years of data required before the model produces reliable signals. Skipping this is a common failure point.

3. **COVID stress test passed** — the volatile 2019–2022 period is one of the hardest test environments. The two-risk-model layer kept the system functional when pure trend strategies blew up.

4. **Sharpe of 0.77** — lower than HMM+RF (1.76) but the absolute return is higher (83% vs 53.55% CAGR). The NN+HMM trades a lower Sharpe for higher raw return — different risk/reward profile.

5. **Only 40 orders** — extremely low trade frequency. The regime filter acts as a strong gating mechanism; the system waits for high-conviction setups.

---

## Connection to This Library

| Paper Component | Library Equivalent |
|---|---|
| HMM regime detection | [[MarkovHedgeFundMethod]], [[HMM-Implementation-Python]] |
| Neural network emissions | Extension beyond standard [[HMM-Theory]] Gaussian assumption |
| Black-Litterman sizing | Related to [[RegimeFilter-RiskManagement]] position scaling |
| Two risk models | [[Guardrails-RiskManagement]] multi-layer safety |
| QuantConnect platform | [[Backtesting]] walk-forward methodology |
| Log return inputs | Same as `label_regimes()` in [[resources/scripts/markov-hedge-fund-method/markov_regime.py]] |

---

## Sources

- [Roan (@RohOnChain) on X — NN+HMM 83% return breakdown](https://x.com/RohOnChain/status/2052798873371037833)
- Full paper: *AI-Powered Energy Algorithmic Trading: Integrating Hidden Markov Models with Neural Networks* (available under QuantConnect's terms)
- [[HiddenMarkovTrading]] — performance benchmarks table referencing this result
- [[HMM-Theory]] — theoretical foundation for the HMM component
