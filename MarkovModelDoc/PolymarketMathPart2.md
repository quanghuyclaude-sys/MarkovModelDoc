# Polymarket Math — Part 2: Frank-Wolfe Implementation

> Source: Roan (@RohOnChain) on X — (Feb 4, 2026)
> Series: Part 2 of Polymarket arbitrage math series
> Back to: [[PredictionMarketsQuant]] · [[QuantRoadmap]] · [[NNTradingSignals]]

---

## Context

Part 1 covered the theory: integer programming, marginal polytopes, Bregman projection, Frank-Wolfe iterations. Part 2 covers the implementation that turned those equations into $40M in extracted arbitrage and a top arbitrageur who made **$2,009,631.76 across 4,049 trades**.

**The four implementation problems:**
1. Initialization — how to build valid starting points for Frank-Wolfe
2. Stability — why standard methods crash on LMSR, and how to prevent it
3. Execution — when to stop iterating and trade with guaranteed profit
4. Market structure — why the mispricing exists in the first place

---

## Part I: Initialization — Algorithm 3 (InitFW)

### The Problem

Frank-Wolfe requires a valid starting active set Z₀. You can't start with random numbers. You need:
- At least one valid payoff vector
- An interior point `u` where **every unsettled security has a price strictly between 0 and 1**
- An extended partial outcome σ̂ (securities that can be logically settled)

If any coordinate of `u` is exactly 0 or 1, the adaptive contraction (Part II) fails and the algorithm breaks.

### Algorithm 3: InitFW

**Goal:** Given partial outcome σ (already-settled securities), produce Z₀, interior point u, and extended σ̂.

**Process:** For each unsettled security i, ask the integer programming solver two questions:
- Q1: "Give me a valid payoff vector z where zᵢ = 1"
- Q2: "Give me a valid payoff vector z where zᵢ = 0"

| Solver Result | Meaning | Action |
|---|---|---|
| Both 0 and 1 exist | Security i is genuinely uncertain | Add both vectors to Z₀; i stays unsettled |
| Only zᵢ = 1 found | All valid outcomes have i = 1 | Add (i, 1) to extended σ̂ |
| Only zᵢ = 0 found | All valid outcomes have i = 0 | Add (i, 0) to extended σ̂ |

**Interior point construction:**
```
u = (1/|Z₀|) × Σ_{z ∈ Z₀} z
```

Because each unsettled security appears as both 0 and 1 across vertices in Z₀, the average guarantees `uᵢ` is strictly between 0 and 1 for all unsettled i.

### Real Example: NCAA Tournament

- 7 securities per team × 2 teams = 14 securities (0–6 wins each)
- Constraint: Duke and Cornell cannot both reach finals (5+ wins each) — they meet in semifinals
- When InitFW asks for a vector where Duke: 5 wins = 1 AND Cornell: 5 wins = 1 → IP solver returns **infeasible**
- Z₀ is populated with vectors respecting the dependency
- u ≈ 0.14 for each team's 0–6 win probabilities

**Performance:** InitFW completes in under 1 second for full NCAA tournament (63 games, 2⁶³ outcomes). IP solver does feasibility checks only, not optimization.

### Three Failure Modes Without Proper Initialization

1. **Empty Z₀** — no valid vertices, algorithm can't start
2. **Boundary interior point** — any coordinate at 0 or 1 makes contraction undefined, gradients explode
3. **Missed settlements** — wasting computation optimizing prices that should be fixed; missing arbitrage removal

---

## Part II: Barrier Frank-Wolfe with Adaptive Contraction

### The Gradient Explosion Problem

Standard Frank-Wolfe assumes the gradient is Lipschitz continuous with a bounded constant L. **LMSR violates this catastrophically.**

For LMSR, the Bregman divergence is KL divergence:
```
D(μ||θ) = Σᵢ μᵢ ln(μᵢ / pᵢ(θ))
```

The gradient:
```
∇R(μ) = ln(μ) + 1
```

As any coordinate `μᵢ → 0`, the gradient component `(∇R)ᵢ = ln(μᵢ) + 1 → −∞`. The marginal polytope M has vertices where coordinates are exactly 0 (securities that resolve False). **As Frank-Wolfe iterates approach these boundary vertices, the gradient explodes.** The algorithm diverges.

### The Solution: Contracted Polytope

Define the **contracted polytope:**
```
M' = (1 − ε)M + εu
```

Where ε ∈ (0,1) is the contraction parameter and u is the interior point from InitFW.

Every vertex v of M gets pulled toward u:
```
v' = (1 − ε)v + εu
```

Because u has all coordinates strictly between 0 and 1, every coordinate of v' is also strictly between 0 and 1. The contracted polytope M' stays away from the boundary.

**The Hessian bound on M':**
```
H_ii = ∂²R/∂μᵢ² = 1/μᵢ ≤ 1/ε
```

This gives Lipschitz constant `L_ε = O(1/ε)` — finite for any fixed ε > 0.

### Adaptive Epsilon Rule (Algorithm 2)

| ε value | Trade-off |
|---|---|
| Large ε | Fast convergence (small Lε), but optimizing wrong polytope (far from M) |
| Small ε | Slow convergence (large Lε), but close to the true M |

**The adaptive rule:** Start large, decrease over time based on progress.

```
If g(μₜ) / (−4g_u) < ε_{t-1}:
    ε_t = min{g(μₜ) / (−4g_u), ε_{t-1} / 2}
Else:
    ε_t = ε_{t-1}
```

Where g(μₜ) is the Frank-Wolfe gap and g_u is the gap at the interior point u.

**ε shrinks adaptively based on convergence, not a fixed schedule.**

### Convergence Rate

```
O(L_ε × diam(M') / t) = O(1/(ε × t))
```

**Practical timeline from Kroer experiments:**
| Phase | ε | Progress |
|---|---|---|
| First 10 iterations | 0.1 | Rapid progress toward rough solution |
| Iterations 10–50 | 0.01 | Refining the solution |
| Iterations 50–150 | 0.001 | Converging to high precision |

Total: 50–150 iterations for NCAA tournament with thousands of securities. Total time: 30 minutes once outcome space shrinks enough for IP solves to complete quickly.

**Without adaptive contraction:** The algorithm either crashes from numerical overflow or diverges due to unstable gradients. This is not optional — it is a necessity.

---

## Part III: Profit Guarantee — When to Stop and Trade

### Proposition 4.1

The guaranteed profit from moving market state θ to θ̂ (where p(θ̂) = μ̂) is:
```
Profit ≥ D(μ̂||θ) − g(μ̂)
```

Where:
- `D(μ̂||θ)` = Bregman divergence (maximum arbitrage if μ̂ were perfect)
- `g(μ̂)` = Frank-Wolfe gap (profit lost to approximation error)

**D(μ̂||θ) − g(μ̂) ≥ 0 always** (proven via convex duality). You never return a trade with negative guaranteed profit.

### Decision Framework

| Scenario | Guaranteed Profit | Action |
|---|---|---|
| D = 0.15, g = 0.20 | −0.05 | Don't trade — approximation too poor |
| D = 0.15, g = 0.02 | +0.13 (87% of max) | Trade immediately |
| D = 0.0001, g = 0.00001 | +0.00009 | Skip — execution costs exceed profit |

### Three Stopping Conditions

**Condition 1: α-Extraction**
```
g(μₜ) ≤ (1 − α) × D(μₜ||θ)
```

Rearranges to: guaranteed profit ≥ α × D(μₜ||θ).

Research implementation: **α = 0.9** — stop when guaranteed to capture ≥ 90% of available arbitrage. Getting the last 10% may require 50 more iterations while the market moves.

**Condition 2: Near-Arbitrage-Free**
```
D(μₜ||θ) ≤ εD
```

Research value: **εD = 0.05** — if maximum arbitrage available is below 5 cents per dollar, skip. Execution risk and gas fees would consume it.

**Condition 3: Forced Interruption**

When a new trade arrives or time limit is hit, return the best iterate found so far:
```
t* = argmax_{τ≤t} [D(μτ||θ) − g(μτ)]
```

Even interrupted at iteration 5, the returned iterate has maximum guaranteed profit among those 5.

### Real Numbers from NCAA Experiments

**Early tournament (16 games settled):**
```
Iteration 10: D = 0.0045, g = 0.0042 → guaranteed profit = 0.0003 (don't trade)
Iteration 50: D = 0.0045, g = 0.0004 → guaranteed profit = 0.0041
α-extraction check: g(μ₅₀) = 0.0004 ≤ 0.9 × 0.0045 = 0.00405 ✓ → Stop
Guaranteed profit: 91% of maximum
```

**Late tournament (56 games settled):**
```
Iteration 20: D = 0.0002, g = 0.00001 → guaranteed profit = 0.00019
α-extraction check: g(μ₂₀) = 0.00001 ≤ 0.9 × 0.0002 = 0.00018 ✓ → Stop
Guaranteed profit: 95% of maximum
```

Late tournament converges faster — outcome space is smaller (128 possibilities vs billions).

### $0.05 Minimum Threshold

The minimum threshold accounts for:
- Non-atomic execution (one leg might fill, others might not)
- Gas fees (~$0.02 per multi-leg trade on Polygon)
- Slippage and order book movement

---

## Part IV: Why Mispricing Exists — The Market Maker's Perspective

### The Fundamental Impossibility

**Theorem (implicit in Kroer et al.):** For any cost function on combinatorial markets with dependencies:
- Fast price updates → arbitrage exists
- Arbitrage-free prices → slow updates

**You cannot have both.**

### How Polymarket Prices (Fast Path)

When a trade arrives:
1. Update state: `θ_new = θ_old + δ`
2. Compute new prices: `p(θ_new) = ∇C(θ_new)`
3. Execute immediately

**Time: <100ms.** But prices might violate logical constraints. If Duke loses in Round 1, "Duke wins championship" should go to $0 instantly — instead it decays gradually.

### How FWMM Prices (Accurate Path)

When a trade arrives:
1. Run InitFW to extend partial outcome
2. Run Barrier FW to project onto M
3. Update state to projected prices

**Time: 30 seconds to 30 minutes.** By the time projection completes, 10 more trades have arrived.

**Polymarket chose speed over accuracy.** This creates three systematic types of mispricing:

| Type | Description | Scale |
|---|---|---|
| Within-market inconsistency | Sum of probabilities ≠ 1 for multi-condition markets | 662 NegRisk markets (42% of all) had sum ≠ 1; median deviation: $0.08 per dollar |
| Cross-market inconsistency | Dependent markets price as if independent | Trump PA + GOP national margin should be correlated; they update independently |
| Settlement lag | Prices don't instantly lock when outcomes resolve; drift toward 0 or 1 as traders bet against them | Assad example: YES=$0.30, NO=$0.30 (sum=$0.60) when outcome already determined; window lasted hours |

### Market Maker's Loss Bound

From Abernethy et al. 2011:
```
Max loss = b × log(|Ω|)
```

Where b = liquidity parameter and |Ω| = number of outcomes.

**NCAA tournament example:**
```
|Ω| = 2⁶³, b = 150
Max loss = 150 × log(2⁶³) = 150 × 43.7 = $6,555
```

No matter how much arbitrage exists, the market maker loses at most $6,555. This is why LMSR is used. Bounded loss even in adversarial scenarios.

### Why Polymarket Tolerates Arbitrage

The market maker is **choosing** to be exploitable:
- Speed > accuracy for their business model
- Arbitrageurs provide consistent, predictable volume
- Loss is bounded anyway
- Removing all arbitrage would drive sophisticated traders elsewhere

The $40M in extracted arbitrage is not a bug. It is an accepted cost for maintaining liquidity.

---

## The Complete Framework (Summary)

| Part | Problem Solved | Key Mechanism |
|---|---|---|
| I — Initialization | Can't start Frank-Wolfe without valid Z₀ | InitFW: IP feasibility checks → vertices + interior point + extended settlements |
| II — Stability | LMSR gradients explode at boundaries | Barrier FW: contracted polytope M' = (1−ε)M + εu + adaptive epsilon rule |
| III — Execution | When to stop iterating vs market moving | Profit guarantee D(μ̂||θ) − g(μ̂) ≥ 0; α=0.9 extraction condition |
| IV — Market Structure | Why opportunities exist | Impossible tradeoff: fast updates = systematic mispricing |

---

## What Part 3 Would Cover (Not Yet Available)

- System architecture: data pipeline, execution engine, monitoring
- Code examples: Python + Gurobi implementation
- Risk management: position sizing, Kelly criterion, drawdown limits
- Infrastructure: AWS setup, database schema, WebSocket handling
- Production system that scales to seven figures

---

## Research References

- Kroer et al. 2016: *Arbitrage-Free Combinatorial Market Making via Integer Programming* (arXiv:1606.02825v2)
- Saguillo et al. 2025: *Unravelling the Probabilistic Forest: Arbitrage in Prediction Markets* (arXiv:2508.03474v1)
- Abernethy et al. 2011: Bounded loss proof for LMSR
- Avellaneda & Stoikov 2008: Market making framework (see [[PredictionMarketsQuant]])

---

## Connection to This Library

| Article Concept | Library Equivalent |
|---|---|
| Frank-Wolfe convergence | Same iterative update logic as Baum-Welch in [[HMM-Theory]] |
| α = 0.9 extraction threshold | Analogous to conviction thresholds in [[RegimeFilter-RiskManagement]] |
| Integer programming solver | Tools referenced in [[AI-Quant-Workbench]] |
| Kill switch on VPIN spike | [[PredictionMarketsQuant]] VPIN detection, [[ClaudeTradingView-Bot]] safety checks |
| Bounded market maker loss | Risk bounding in [[Guardrails-RiskManagement]] |

---

## Sources

- [Roan (@RohOnChain) — Polymarket Math Part 2](https://x.com/RohOnChain/status/2052043443766194272)
- [[PredictionMarketsQuant]] — Phase 3 models (Avellaneda-Stoikov, Kelly, VPIN) that this builds on
- [[QuantRoadmap]] — mathematical foundation (linear algebra, optimization, stochastic calculus) underlying these methods
