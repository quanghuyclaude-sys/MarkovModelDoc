# Market Regimes — What the HMM Detects

> Back to strategy hub: [[HiddenMarkovTrading]]  
> Source: [QuantInsti: Market Regime using Hidden Markov Model](https://blog.quantinsti.com/regime-adaptive-trading-python/)

---

## What Is a Market Regime?

A market regime is a period during which prices behave in a consistent, identifiable way. Regimes are not labeled in the data — they must be inferred. The HMM's job is to find these hidden behavioral states.

The fundamental assumption: **a single strategy cannot work well across all regimes**. A trend-following system that thrives in a Bull regime will bleed out in a choppy Sideways market.

---

## The Three Primary Regimes

### Bull (Regime 0 — Low Volatility, Uptrend)
- Positive mean daily returns
- Low day-to-day volatility
- Strong momentum — SMA(short) > SMA(long)
- **Action**: Go long, hold positions, increase position size

### Bear (Regime 1 — High Volatility, Downtrend)
- Negative or flat mean daily returns
- High volatility — frequent large swings
- Momentum is bearish or erratic
- **Action**: Close longs, go flat or short, shrink position size

### Sideways / Neutral (Regime 2 — Ranging)
- Near-zero mean return
- Moderate volatility
- No persistent trend direction
- **Action**: Mean-reversion strategies work here; trend strategies sit out

---

## How the Markov Hedge Fund Method Classifies Regimes

From the [markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method) repository:

**Simple classification using rolling 20-day windows:**
```
Bull     → rolling 20-day return > +5%
Bear     → rolling 20-day return < -5%
Sideways → between -5% and +5%
```

This rule-based approach builds the **state transition matrix** from historical labeled data — then forecasts future state probabilities using Chapman-Kolmogorov.

---

## The 3×3 State Transition Matrix

For 3 regimes, the transition matrix looks like:

```
             Next: Bull   Next: Bear   Next: Sideways
Curr: Bull      0.82        0.08          0.10
Curr: Bear      0.12        0.76          0.12
Curr: Sideways  0.18        0.13          0.69
```

High diagonal entries confirm that regimes are **sticky** — markets tend to stay in the same state for extended periods. This is the core reason HMMs work for trading.

---

## Stationary Distribution

The long-run fraction of time spent in each regime:

```python
# Solve π × A = π, sum(π) = 1
# Example result:
π_bull     = 0.45   # 45% of time in Bull
π_bear     = 0.25   # 25% of time in Bear
π_sideways = 0.30   # 30% of time in Sideways
```

This tells you the historical base rate — useful for calibrating position sizing.

---

## Regime Signals (Directional Score)

The markov-hedge-fund-method generates a **signed directional signal**:

```
Signal = P(Bull tomorrow) - P(Bear tomorrow)
```

- Signal near +1.0 → strong bull conviction → full long
- Signal near -1.0 → strong bear conviction → flat or short
- Signal near 0 → uncertain → reduce or skip

---

## Regime Persistence and Mean Reversion

| Metric | Regime Persistence |
|---|---|
| Average Bull streak | 45–90 trading days |
| Average Bear streak | 15–40 trading days |
| Average Sideways streak | 20–60 trading days |

Bear regimes are shorter but more intense. This asymmetry is why a regime filter reduces drawdown without proportionally reducing returns.

---

## Sources

- [QuantInsti: Market Regime using Hidden Markov Model](https://blog.quantinsti.com/regime-adaptive-trading-python/)
- [GitHub: markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method)
- [PyQuantLab: Regime-Aware Trading with HMMs and Macro Features](https://pyquantlab.medium.com/regime-aware-trading-with-hidden-markov-models-hmms-and-macro-features-c75f6d357880)
- [QuantConnect: Intraday Application of Hidden Markov Models](https://www.quantconnect.com/research/17900/intraday-application-of-hidden-markov-models/)
