# Quant Career Roadmap — Blueprint to $650,000/Year

> Source: Roan (@RohOnChain) on X — [https://x.com/RohOnChain/status/2052043443766194272](https://x.com/RohOnChain/status/2052043443766194272)
> Published: April 28, 2026
> Back to: [[NNTradingSignals]] · [[PredictionMarketsQuant]] · [[AI-Quant-Workbench]]

---

## Industry Compensation (2025–2026)

| Role / Firm | Compensation |
|---|---|
| Entry-level Quant Researcher (Citadel) | $336,000–$642,000 total comp |
| Jane Street average employee | $1.4M (first half of 2025) |
| IMC Trading interns (annualized) | $240,000+ |
| 5-year benchmark at top prop shops | $800,000–$1,200,000/year |

---

## The Four Quant Roles

| Role | What They Do | Entry Comp | Skills |
|---|---|---|---|
| **Quant Researcher** | Find patterns, build predictive models, design strategies | $350k–$650k | PhD-level math or exceptional undergrad quant |
| **Quant Trader** | Execute models in real time | $200k–$400k + unlimited upside | Fast probabilistic thinking, mental math |
| **Quant Developer** | Build trading infrastructure, low-latency systems | $200k–$350k | C++, Rust, Python at high performance |
| **Risk Quant** | Model validation, VaR, stress testing, regulatory | Stable, lower ceiling | Statistics, compliance |

**Fastest-growing role (2025–2026):** AI/ML-focused quant — signal generation via deep learning, alternative data processing, ML models deployed directly to live trading.

**Key insight:** Jane Street explicitly states prior finance/economics knowledge is not expected or required. Over 2/3 of recent interns studied CS or mathematics.

---

## The Mathematical Foundation — 5 Layers in Correct Order

You cannot skip levels. Every concept is prerequisite for the next.

### Layer 1: Probability

Everything in quantitative finance reduces to: **What are the odds, and are they in my favor?**

Core concepts:
- **Conditional probability:** `P(A|B) = P(A and B) / P(B)` — quants always think in conditionals, never absolutes
- **Bayes' Theorem:** `Posterior = (Likelihood × Prior) / Evidence` — update conviction as new information arrives; fastest updaters consistently outperform
- **Expected value:** Average outcome across all scenarios
- **Variance:** Deviation from expected value — survive variance long enough and positive EV accumulates

Resource: *Blitzstein & Hwang, Introduction to Probability* (free PDF from Harvard). Work every problem in Chapters 1–6. Budget 3–4 weeks.

### Layer 2: Statistics

The most important thing statistics teaches: **most of what looks like signal is actually noise.**

Core concepts:
- **Hypothesis testing:** The multiple comparisons problem — 1,000 random strategies will produce 50 with apparently strong results by chance at 5% significance. This is the single most common reason backtests look great and live results are terrible.
- **Linear regression:** Regress returns against known risk factors. Only **alpha** (the intercept after accounting for all factors) is real edge.

Resource: *Wasserman, All of Statistics*, Chapters 1–13. Budget 4–5 weeks.

### Layer 3: Linear Algebra

The machinery running everything in quant finance and ML.

Core concepts:
- **Covariance matrix:** `Variance = wᵀ Σ w` — the mathematical core of portfolio optimization and risk management
- **Eigenvalues:** In a 500-stock universe, the first 5 eigenvectors explain ~70% of all variance. Everything else is noise. Foundation of factor investing and dimensionality reduction.

Resource: *Gilbert Strang, MIT 18.06 lectures* (free at MIT OpenCourseWare) + *Introduction to Linear Algebra* textbook. Budget 4–6 weeks.

### Layer 4: Calculus and Optimization

Nearly every quant problem reduces to maximizing something subject to constraints.

Core concepts:
- **Convex optimization:** A convex optimization problem has a unique global solution that can be found efficiently. Most portfolio construction and risk management problems can be structured as convex programs.

Resource: *Boyd & Vandenberghe, Convex Optimization* (free PDF from Stanford). Work Chapters 1–5. Budget 4–5 weeks.

### Layer 5: Stochastic Calculus

After this layer you can derive how financial instruments are priced from first principles.

Core insight: In randomness, the square of a small random increment is **not negligible** (unlike ordinary calculus). This produces **Ito's Lemma** — the chain rule of stochastic calculus.

**Black-Scholes equation:**
```
dV/dt + (1/2)σ²S²(d²V/dS²) + rS(dV/dS) - rV = 0
```

The remarkable result: the expected return of the stock disappears completely. Option price depends only on **how much** the stock moves, not where it goes.

Resource: *Shreve, Stochastic Calculus for Finance*, Volumes 1 and 2. Budget 6–8 weeks.

---

## Tech Stack

### Research Programming (Quant Researcher / Analyst)

| Tool | Purpose |
|---|---|
| pandas / polars | Data manipulation (polars 10–50x faster on large datasets) |
| numpy / scipy | Numerical computation |
| xgboost, lightgbm, catboost | ML on tabular data |
| PyTorch | Deep learning |
| cvxpy | Optimization problems |
| statsmodels | Statistical testing |

### Production Systems (Quant Developer / HFT)

**C++** — dominant in HFT for decades. Memory control, deterministic performance, no GC pauses. Libraries: QuantLib, Eigen, Boost.

**Rust** — serious emerging competitor. Same performance as C++ with compile-time memory safety. NautilusTrader uses Rust core + Python API — this architecture is becoming the standard pattern for new systematic trading infrastructure.

### Data Sources

| Source | Cost | Use |
|---|---|---|
| yfinance | Free | Learning |
| Polygon.io | ~$200/month | Serious retail (sub-20ms latency) |
| Bloomberg Terminal | ~$32,000/year | Institutional standard |
| Finnhub | Free tier | Early projects |

### Backtesting

- **NautilusTrader** — production-grade, Rust core
- **Backtrader / vectorbt** — simpler, good for learning concepts

---

## Interview Process

### What Firms Actually Test

**Citadel structure:** Multiple simultaneous tracks (software engineering, trading, quant research). Serious candidate may go through 15–20 interviews in a single season. Final rounds = "super days": 6 consecutive 45-minute interviews covering C++, system design, probability proofs, ML design, and behavioral.

**Jane Street approach:** Problems intentionally harder than one person can solve alone. They test how you use hints, reason under uncertainty, and collaborate under pressure. Narrating thinking > producing silent correct answers.

**Mental math:** Firms use Zetamac for early screening. Target 50+ correct answers per minute before applying.

### Interview Resources

| Resource | What It Covers |
|---|---|
| *Zhou, A Practical Guide to Quantitative Finance Interviews* (Green Book) | 200+ real problems — probability, statistics, brain teasers, mental math. Most referenced resource across successful candidates. |
| QuantGuide.io | Quant-specific practice problems |
| Brainstellar | Probability puzzles at interview difficulty |
| LeetCode Blind 75 | Coding rounds — focus on pattern understanding. Dynamic programming is the most common failure point at Citadel and Jane Street. |

**Research experience** separates strongest candidates from everyone else. Not grades — actual research where you formulated a hypothesis, built something, and can describe what failed and why.

### Fast-Track Competitions

| Competition | Prize / Benefit |
|---|---|
| Jane Street Kaggle | $100,000 prize |
| WorldQuant BRAIN | Cash for alpha signals you submit |
| Citadel Datathon | Explicitly fast-tracks winners into employment interviews |

---

## The Staircase From Zero to $650,000

1. **Build math foundation** in correct layer order — run academic track and coding track in parallel
2. **Build one real project** before applying anywhere — backtest a strategy on real data, submit to WorldQuant BRAIN or Kaggle, implement via a broker API (Alpaca)
3. **Get first institutional credential** — cold email PhD students, TA a quant course, join a research assistant position
4. **Use each credential to reach the next** — research lab → startup → mid-tier firm → elite fund. No reliable shortcut exists.
5. **Apply before you feel ready** — track every rejection. Every question you couldn't answer = study that before next interview.
6. **Compete publicly** — competitions are recruitment pipelines

**The moat is mathematical depth.** The ability to derive why Ito's Lemma has an extra term. To know when convex optimization applies in a live market. Borrowed approaches expire. Mathematical fluency generates new approaches indefinitely.

---

## Complete Reading List

**Mathematics:**
- Blitzstein & Hwang, *Introduction to Probability* (free, Harvard)
- Strang, *Introduction to Linear Algebra* + MIT 18.06 (free, OpenCourseWare)
- Wasserman, *All of Statistics*
- Boyd & Vandenberghe, *Convex Optimization* (free, Stanford)
- Shreve, *Stochastic Calculus for Finance*, Vol. 1 and 2

**Quantitative Finance:**
- Hull, *Options Futures and Other Derivatives*
- Natenberg, *Option Volatility and Pricing*
- Lopez de Prado, *Advances in Financial Machine Learning*
- Ernest Chan, *Quantitative Trading*
- Zuckerman, *The Man Who Solved the Market*

**Interview Prep:**
- Zhou, *A Practical Guide to Quantitative Finance Interviews*
- Crack, *Heard on the Street*
- Joshi, *Quant Job Interview Questions and Answers*

---

## Connection to This Library

| Roadmap Concept | Library Equivalent |
|---|---|
| Layer 1: Probability / Bayes | [[HMM-Theory]] Baum-Welch, forward-backward algorithm |
| Layer 3: Covariance / eigenvalues | [[NNHMMPaper]] Black-Litterman portfolio optimization |
| Layer 4: Convex optimization | Position sizing in [[TradeExecution]], [[RegimeFilter-RiskManagement]] |
| Kelly Criterion | [[NNTradingSignals]] position sizing section |
| NautilusTrader / backtesting | [[Backtesting]] walk-forward methodology |
| Alpha after factor regression | Edge concept underlying [[MarkovHedgeFundMethod]] |

---

## Sources

- [Roan (@RohOnChain) — Quant Roadmap](https://x.com/RohOnChain/status/2052043443766194272)
- [[NNTradingSignals]] — practical implementation of the ML skills described here
- [[PredictionMarketsQuant]] — applying these skills to prediction markets specifically
- [[AI-Quant-Workbench]] — 5-module research workbench implementing statistical tools
