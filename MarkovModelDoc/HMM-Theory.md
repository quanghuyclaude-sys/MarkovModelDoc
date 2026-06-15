# HMM Theory — Hidden Markov Models Explained

> Back to strategy hub: [[HiddenMarkovTrading]]  
> Source: [QuantStart: Hidden Markov Models — An Introduction](https://www.quantstart.com/articles/hidden-markov-models-an-introduction/)

---

## The Core Idea

In financial markets, the forces driving price behavior — investor sentiment, liquidity conditions, macro regime — are **not directly observable**. We only see their effect: prices, volumes, returns.

A Hidden Markov Model assumes:
- There is a sequence of **hidden states** (e.g., Bull, Bear, Sideways)
- Each hidden state generates **observable outputs** (e.g., returns, volatility)
- We can infer the most likely hidden state from the observations

The "Markov" part means each state depends only on the **immediately preceding state** — not on full history.

---

## The Three Components

### 1. States (S)
The hidden variables the model tries to infer.

In trading:
- **State 0** — Low volatility / trending up (Bull)
- **State 1** — High volatility / trending down (Bear)
- **State 2** — Sideways / ranging

You choose how many states (`n_components` in hmmlearn). Start with 2–3.

### 2. Transition Matrix (A)
The probability of moving from one state to another.

```
         Bull   Bear   Sideways
Bull   [ 0.85   0.10   0.05  ]
Bear   [ 0.15   0.75   0.10  ]
Sideways [ 0.20  0.15   0.65  ]
```

High diagonal values mean the market tends to stay in the same regime (persistence).

### 3. Emission Distribution (B)
Given a hidden state, what distribution of returns/volatility do we observe?

For a **Gaussian HMM**:
- Each state has its own mean (μ) and variance (σ²)
- Bull state: positive mean, low variance
- Bear state: negative mean, high variance

---

## Key Algorithms

### Viterbi Algorithm
Finds the **most likely sequence** of hidden states given observed data.  
Used for: labeling historical bars with their regime.

### Baum-Welch Algorithm
An Expectation-Maximization (EM) algorithm that **learns** the transition matrix and emission parameters from data — without needing labeled training data.  
Used for: fitting the model (`model.fit()`).

### Forward Algorithm
Computes the **probability of the observed sequence** given the model.  
Used for: scoring model quality and predicting tomorrow's regime.

---

## Chapman-Kolmogorov Equations

For multi-step regime forecasting, the n-step transition probability is:

```
A^n = A × A × A × ... (n times)
```

So if today is Bull, the probability of being in Bear in 5 days is the (Bull, Bear) entry of A⁵.

The **stationary distribution** (long-run average time in each regime) is found by solving:

```
π × A = π
```

This tells you, in the long run, what fraction of time the market spends in each state.

---

## Why Gaussian HMM for Trading

- Returns across a single regime roughly follow a normal distribution
- Different regimes have different mean/variance — captured by separate Gaussians
- No need for labeled data — unsupervised learning
- Naturally handles regime persistence (markets trend, not random-walk)

---

## Limitations to Know

| Limitation                              | Implication                               |
| --------------------------------------- | ----------------------------------------- |
| Assumes Markov property (memoryless)    | Long-term dependencies not captured       |
| Gaussian emission may not fit fat tails | Consider Student-t HMM for heavy tails    |
| Number of states is a hyperparameter    | Requires tuning / BIC/AIC model selection |
| Non-stationarity                        | Retrain periodically (walk-forward)       |
| Local optima in EM                      | Run multiple random restarts              |

---

## Extensions Beyond Standard HMM

### Neural Network + HMM Hybrid
Replace the Gaussian emission distribution with a neural network that learns non-linear emission functions. A researcher applied this to live markets and achieved **83% return ($100k → $182,761)**. Roh (@RohOnChain) published a breakdown: [X post](https://x.com/RohOnChain/status/2052798873371037833).

### Game Theory Layer (Smart Money Detection)
USC mathematicians published a **43-page game theory framework** for detecting insider/smart-money moves before public announcements. Referenced by Roh as one of the most dangerous quant papers of the year — combines with HMM regime context to flag structurally anomalous price action. See [Roh's X post](https://x.com/RohOnChain/status/2066220156804837408).

---

## Sources

- [QuantStart: Hidden Markov Models — An Introduction](https://www.quantstart.com/articles/hidden-markov-models-an-introduction/)
- [QuantStart: Market Regime Detection using HMMs in QSTrader](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)
- [YouTube: I Re-Created A Quant Trading Strategy With Claude Code](https://www.youtube.com/watch?v=ZVMTeDBmSrI&t=1134s)
- [RohOnChain on X — NN+HMM 83% return research](https://x.com/RohOnChain/status/2052798873371037833)
- [RohOnChain on X — USC game theory paper](https://x.com/RohOnChain/status/2066220156804837408)
