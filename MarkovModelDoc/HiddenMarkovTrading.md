# Hidden Markov Trading — Central Hub

> Strategy reconstructed from: [I Re-Created A Quant Trading Strategy With Claude Code (Insanely Cool)](https://www.youtube.com/watch?v=ZVMTeDBmSrI&t=1134s) · [Rebuilt with Fable 5](https://www.youtube.com/watch?v=Z-hU97WO30I)  
> Original framework by Roan (@RohOnChain) · tooling by Lewis Jackson  
> GitHub: [markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method)

---

## What This Is

A **self-adaptive, regime-aware trading system** built on Hidden Markov Models (HMMs). Instead of applying a single fixed strategy to all market conditions, it first identifies *what kind of market* is happening right now — then trades accordingly.

The core insight: markets cycle through distinct behavioral states (Bull, Bear, Sideways). A strategy that knows which state it is in can size positions correctly, filter bad trades, and avoid catastrophic drawdowns.

---

## System Architecture

```
Market Data
    │
    ▼
┌─────────────────────────┐
│  Regime Detection (HMM) │  ← Hidden Markov Model
│  Bull / Bear / Sideways │
└─────────┬───────────────┘
          │
    ┌─────┴──────┐
    ▼            ▼
Signal        Risk
Generation    Filter
    │            │
    └─────┬──────┘
          ▼
      Trade Execution
          │
          ▼
    Walk-Forward Backtest
```

---

## Knowledge Map

| Topic | File | Purpose |
|---|---|---|
| What HMMs are mathematically | [[HMM-Theory]] | Foundation — read first |
| Bull/Bear/Sideways regimes | [[MarketRegimes]] | What the model is detecting |
| The original video strategy | [[MarkovHedgeFundMethod]] | Core implementation |
| Python code with hmmlearn | [[HMM-Implementation-Python]] | Build it |
| Filtering trades by regime | [[RegimeFilter-RiskManagement]] | Risk management layer |
| Generating buy/sell signals | [[SignalGeneration]] | Entry/exit logic |
| Walk-forward backtesting | [[Backtesting]] | Validating the strategy |
| Macro features (VIX, yield) | [[MacroFeatures]] | Advanced inputs |
| TradingView Pine Script | [[TradingViewPineScript]] | Visualization |

---

## Quick-Start Build Order

1. Read [[HMM-Theory]] to understand the model
2. Read [[MarketRegimes]] to understand what you're detecting
3. Follow [[HMM-Implementation-Python]] to fit your first model
4. Wire in [[SignalGeneration]] to produce trade signals
5. Add [[RegimeFilter-RiskManagement]] to block bad-regime entries
6. Validate with [[Backtesting]] using walk-forward methodology
7. Add [[MacroFeatures]] for richer regime detection
8. Visualize in TradingView with [[TradingViewPineScript]]

---

## Key Performance Benchmarks

| Setup                           | Sharpe | Max Drawdown | CAGR                                              |
| ------------------------------- | ------ | ------------ | ------------------------------------------------- |
| SMA crossover only (no HMM)     | 0.37   | ~56%         | 6.41%                                             |
| SMA crossover + HMM filter      | 0.48   | ~24%         | 6.88%                                             |
| HMM + Random Forest (BTC)       | 1.76   | -20.03%      | 53.55%                                            |
| Buy & Hold BTC comparison       | 1.16   | -28.14%      | 50.21%                                            |
| **Neural Network + HMM hybrid** | —      | —            | **83% return** ($100k → $182,761 on live markets) |

The HMM regime filter cut max drawdown by more than half while improving Sharpe. The NN+HMM hybrid referenced by Roh uses neural networks to enhance state emission modeling, producing stronger returns on live markets — see [Roh's breakdown](https://x.com/RohOnChain/status/2052798873371037833) and [[HMM-Implementation-Python]] for the base layer.

---

## Core Dependencies

```bash
pip install yfinance hmmlearn pandas numpy scikit-learn ta plotly
```

Or use the zero-dependency install via `uv` (see [[MarkovHedgeFundMethod]]).

---

## Sources

- [YouTube: I Re-Created A Quant Trading Strategy With Claude Code](https://www.youtube.com/watch?v=ZVMTeDBmSrI&t=1134s)
- [YouTube: I Re-Built A Quant Trading Strategy With Fable 5](https://www.youtube.com/watch?v=Z-hU97WO30I)
- [GitHub: markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method)
- [QuantStart: Market Regime Detection using HMMs](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)
- [QuantInsti: Market Regime using Hidden Markov Model](https://blog.quantinsti.com/regime-adaptive-trading-python/)
- [PyQuantLab: Regime-Aware Trading with HMMs and Macro Features](https://pyquantlab.medium.com/regime-aware-trading-with-hidden-markov-models-hmms-and-macro-features-c75f6d357880)
- [MarketCalls: Introduction to HMM for Traders](https://www.marketcalls.in/python/introduction-to-hidden-markov-models-hmm-for-traders-python-tutorial.html)
