# Prediction Markets Quant — Complete Roadmap

> Source: Roan (@RohOnChain) on X — [https://x.com/RohOnChain/status/2052043443766194272](https://x.com/RohOnChain/status/2052043443766194272) (Feb 24, 2026)
> Back to: [[QuantRoadmap]] · [[PolymarketMathPart2]] · [[NNTradingSignals]]

---

## Why Prediction Markets Need Quants

Institutional demand is accelerating. Susquehanna International Group (SIG) hired a Senior Trader for prediction markets, building real-time models for uncertain, event-driven outcomes. A large institution stated: *"We have more capital available than crypto markets have profitable opportunities to deploy into."*

- **TradFi:** Compressed most inefficiencies decades ago through quantitative arbitrage
- **Prediction markets:** Young. Mathematical infrastructure doesn't exist yet. → Systematic opportunity

---

## Phase 0: Mental Model Reset

Stop thinking: *betting platform. Place a bet. Hope you're right.*

**What prediction markets actually are:**

| Framework | Reality |
|---|---|
| Continuous Bayesian updating machines | Every trade is information. Every price change = market revising collective belief based on new evidence |
| Orderbook microstructure systems | Bid/ask, liquidity providers/takers, informed/noise flow — identical mechanics to equities and futures |
| Probability calibration datasets | Every resolution gives a ground truth data point. At $0.30, did it happen 30% of the time? Testable. |
| Sentiment compression layers | Political events, sports, macro — compressed to a single number between 0 and 1 |

**Polymarket specifically:**
```
Price = crowd posterior probability
Orderbook = liquidity supply curve
Resolution = Bernoulli outcome (0 or 1, nothing in between)
```

---

## Phase 1: Mathematical Foundation

### Conditional Probability

The most important concept for prediction market quants.

```
P(A|B) = P(A and B) / P(B)
```

In practice: unconditional probability of a sharp move after an announcement = 40%. On days with elevated implied volatility before the announcement, conditional probability = 68%. That 68% is real signal. The 40% mixes signal and noise.

### Bayes' Theorem

```
Posterior = (Likelihood × Prior) / Evidence
```

When a new poll drops, an injury is announced, or a political figure makes a statement — the model doesn't react emotionally. It updates the probability estimate precisely based on how much new information should shift the prior belief.

### Expected Value

Every trade decision reduces to:
```
EV = (Probability of WIN × Profit) − (Probability of LOSS × Loss)
```

Example: YES contract pays $1 on 40% probability event, costs $0.30:
```
EV = (0.40 × $0.70) − (0.60 × $0.30) = $0.28 − $0.18 = +$0.10
```

Positive EV → trade. Negative → don't. The entire game is estimating probability more accurately than the market.

### Kelly Criterion

```
f* = (p × b − q) / b
```

Where p = win probability, b = net odds received, q = 1 − p.

- Never bet full Kelly in practice — use **fractional Kelly** because probability estimates carry uncertainty
- A 10% edge → bet 10% of capital for maximum long-run growth
- Bet more = eventual ruin even with genuine edge
- See [[NNTradingSignals]] for empirical Kelly with Monte Carlo (institutional application)

### Game Theory

Prediction markets are you versus other participants who are also actively extracting edge: informed traders, noise traders, market makers, arbitrageurs.

**Nash Equilibrium:** State where no participant can improve by changing strategy unilaterally. Exploitable edges are always found **away from equilibrium**.

**Prisoner's Dilemma framework** explains why market makers sometimes widen spreads simultaneously, why arbitrageurs delay trading, why informed traders disguise order flow.

### Naive Bayes Classifier

```
P(outcome | features) ∝ P(outcome) × ∏ P(featureᵢ | outcome)
```

Given observable signals (poll data, historical patterns, market momentum, news sentiment): what is the probability the event resolves YES? The fast, transparent baseline probability estimate before refining with more sophisticated models.

### Shannon Entropy

```
H = −∑ pᵢ × log(pᵢ)
```

In prediction markets, entropy = direct measure of **how much edge is available**:
- Contract near $0.50 → maximum entropy → maximum room for your model to add value
- Contract near $0.95 → near-zero entropy → adverse selection risk from informed traders is extreme

Entropy tells you **which markets are worth making markets in**.

---

## Phase 2: Market Microstructure

### The Order Book and Adverse Selection

The bid-ask spread exists for one reason: **some traders know more than you do.** A market maker quoting $0.60/$0.64 means: "4 cents compensates me for times an informed trader knows the true probability is 80%."

A spread that **suddenly widens** means someone just received information you don't have. That signal alone is actionable.

### Minting and Merging

When no one sells YES tokens, the system mints a new YES+NO pair by locking $1 USDC as collateral. The reverse destroys equal YES+NO tokens and returns $1 USDC.

This enforces the invariant at the smart contract level:
```
P(YES) + P(NO) = $1.00
```

When this breaks across correlated markets, guaranteed profit exists. A recent research paper found **41% of all conditions on Polymarket showed exploitable mispricing** at some point.

### Hybrid Architecture

| Component | Detail |
|---|---|
| Order matching | Signed off-chain, matched by Polymarket's centralized operator |
| Settlement | On-chain via Polygon, ~2-second block times |
| Gas costs | ~$0.007 per transaction |
| Critical bottleneck | **Canceling orders**, not placing them |

Your ability to cancel stale quotes before an informed trader fills them is the single most important latency metric.

### Fee Structure and Rewards

- Most markets: 0% fees
- Fee-enabled markets: `fee = baseRate × min(price, 1−price) × size`
- Polymarket distributes ~**$12 million annually** in liquidity rewards
- Two-sided quoting earns ~3× the rewards of single-sided quoting

---

## Phase 3: Quantitative Models

### Avellaneda-Stoikov Framework (Market Making)

Published 2008, foundation of modern quantitative market making.

**Reservation price:**
```
r = s − q × γ × σ² × (T − t)
```

Where s = mid-price, q = inventory position, γ = risk aversion, σ² = market variance, (T−t) = time to resolution.

- Long inventory → reservation price falls below mid (want to sell)
- Short inventory → reservation price rises above mid (want to buy)

**Optimal spread:**
```
δ = γσ²(T−t) + (2/γ) × ln(1 + γ/κ)
```

Two sources of edge: (1) inventory risk compensation (scales with volatility), (2) pure liquidity provision profit (persists even with zero risk aversion).

**For prediction markets — critical modification:** Prices must stay between 0 and 1. Use the log-odds transformation:
```
logit(p) = ln(p / (1−p))
```

This maps bounded price space to unbounded real line where standard diffusion models apply. Prices stay in (0,1) by construction. This is the same sigmoid function at the heart of every neural network — not a coincidence.

### Empirical Kelly with Monte Carlo

The textbook Kelly formula assumes you know your edge with certainty. That assumption is wrong.

When your model estimates 6% edge, that's a point estimate with uncertainty around it. Standard Kelly leads to systematic overbetting and eventual ruin.

**Institutional solution:**
1. Build empirical return distribution from historical data
2. Run Monte Carlo resampling → 10,000 alternative path scenarios (randomly reorder historical return sequence)
3. Target position size at **95th percentile drawdown** across all scenarios (not median)

```
f_empirical = f_kelly × (1 − CV_edge)
```

Where CV_edge = coefficient of variation of edge estimates across simulations. High uncertainty → aggressive haircut to position size.

### VPIN — Toxicity Detection

```
VPIN = |V_buy − V_sell| / (V_buy + V_sell)
```

Measures imbalance between buy and sell volume over rolling windows.

| VPIN signal | Action |
|---|---|
| Balanced buy/sell | Flow is noise — normal operation |
| Diverging sharply one direction | Someone with private information is trading aggressively |
| VPIN rises sharply | Widen spreads immediately |
| VPIN continues rising | Withdraw quotes entirely |

Adverse selection cost near resolution dominates all other considerations. No spread is wide enough to justify quoting into fully informed flow.

---

## Phase 4: Technical Infrastructure

### Language Strategy

| Stage | Language | Why |
|---|---|---|
| Research and proof | Python | Fast iteration, rich ML ecosystem |
| Production (once edge proven) | Go or Rust | Microsecond latency, no GC pauses |

Start with Python. The person who learns Rust first but doesn't understand microstructure builds a very fast system that loses money quickly.

### Real-Time Data Architecture

Production market making requires **WebSocket connections**, not REST polling.

- Arbitrage windows compressed from 12 seconds (2024) → 30ms (Q1 2026)
- 500ms REST polling interval = elimination from the game, not just a disadvantage
- **Track sequence numbers** on every message — a single missed update means your local order book diverges from reality

### Kill Switch Architecture

- **Passive:** GTD orders auto-expiring before known high-impact events
- **Active:** `cancelAll()` on VPIN spikes, position limit breaches, or any error condition

### Infrastructure

- Test different server regions for latency to Polygon's RPC endpoints
- Use **AWS KMS** for private key management — never store locally in a live system
- Cost of a compromised key >> any latency gain from insecure handling

---

## Phase 5: Deploy, Measure, Compete

1. **Deploy with minimal capital first** — prove the system works before scaling
2. **Track:** execution success rate, fill quality vs theoretical fair value, P&L broken down into spread capture vs adverse selection losses **separately**
3. If adverse selection losses are growing relative to spread capture → VPIN detection is failing → fix before adding capital
4. **The loop:** Get new strategy → backtest → find where it breaks → improve → repeat

This loop never ends. The market evolves, competitors improve, edges compress. Long-term winners are those who build the **system that keeps finding new edges**, not those who find one edge.

---

## Resources

**Phase 1 — Mathematics:**
- E.T. Jaynes, *Probability Theory: The Logic of Science*
- J.L. Kelly Jr., original Kelly Criterion paper (1956)
- Annie Duke, *Thinking in Bets*

**Phase 2 — Microstructure:**
- Polymarket CLOB documentation
- Glosten & Milgrom, *Bid Ask and Transaction Prices* (1985)
- Gnosis Conditional Token Framework documentation

**Phase 3 — Quantitative Models:**
- Avellaneda & Stoikov, *High-Frequency Trading in a Limit Order Book* (2008)
- Easley, López de Prado & O'Hara, *Flow Toxicity and Liquidity* (2012)
- Jon Becker's 400 million trade Polymarket dataset

**Phase 4 — Infrastructure:**
- Polymarket CLOB client on GitHub
- AWS KMS documentation
- Polygon network RPC documentation

---

## Connection to This Library

| Article Concept | Library Equivalent |
|---|---|
| Kelly Criterion | [[NNTradingSignals]] Step 5, [[TradeExecution]] position sizing |
| VPIN toxicity detection | Analogous to HMM conviction threshold gating in [[RegimeFilter-RiskManagement]] |
| Avellaneda-Stoikov reservation price | Regime-adjusted positioning in [[MarkovHedgeFundMethod]] |
| Empirical Kelly with Monte Carlo | Extends [[Guardrails-RiskManagement]] risk framework |
| Frank-Wolfe / Bregman projection | [[PolymarketMathPart2]] full implementation |
| Shannon entropy as market selection | Regime confidence score in [[RegimeFilter-RiskManagement]] |
| WebSocket + kill switch | [[ClaudeTradingView-Bot]] bot.js architecture |

---

## Sources

- [Roan (@RohOnChain) — Prediction Markets Quant Roadmap](https://x.com/RohOnChain/status/2052043443766194272)
- [[PolymarketMathPart2]] — Frank-Wolfe arbitrage implementation (Part 2 of this series)
- [[QuantRoadmap]] — broader quant career foundation
- [[NNTradingSignals]] — neural network implementation referenced in Phase 4
