# AI Quant Workbench — Statistical Research Toolkit

> Back to: [[ZeroOne-ResourceHub]]
> Repo: [jackson-video-resources/ai-quant-workbench](https://github.com/jackson-video-resources/ai-quant-workbench)
> Built by: Lewis Jackson, based on Roan (@RohOnChain) framework

---

## What It Is

A free Claude Code skill that installs a quantitative research workbench — five
Python modules covering probability, statistics, portfolio mathematics, and
AI-augmented research. It validates the statistical quality of trading signals
before they go live.

The workbench is research-only: it never places, simulates, or recommends trades.
It tells you whether your signal has statistical validity.

---

## Installation

Paste the one-shot install prompt into Claude Code agent mode.
The installer automatically:
1. Detects your OS (Mac/Linux/Windows)
2. Installs `uv` (Astral Python toolchain) if needed
3. Creates a Python 3.12 virtual environment
4. Deploys all 5 modules to `~/.claude/skills/ai-quant-workbench/`
5. Fetches 2 years of SPY daily OHLCV data (or uses cached fallback)
6. Runs coin-flip demo as validation check

Installation is idempotent — safe to re-run from any phase.

---

## The Five Modules

### 1. Probability Primitives (`probability.py`)

Implements foundational probability concepts used in trading:

```python
# Conditional probability: P(A|B)
conditional_probability(p_a_and_b, p_b)

# Bayesian updating — update prior belief with new evidence
bayesian_update(prior, likelihood, evidence)

# Expected value — core of any position sizing decision
expected_value(outcomes, probabilities)
```

Usage: `"use the ai-quant skill to compute expected value:
         win 2% probability 0.6, lose 1% probability 0.4"`

### 2. Statistics Utilities (`statistics.py`)

| Function | Purpose |
|---|---|
| One-sample t-test | Is this signal's mean return statistically different from zero? |
| OLS regression | Signal-vs-noise — how much of return is explained by the factor? |
| Augmented Dickey-Fuller | Is the signal stationary? (required for HMM inputs) |
| Residual analysis | Normality check, fit quality assessment |

Usage: `"use the ai-quant skill to run an ADF stationarity test on my RSI series"`

The stationarity test is directly relevant to [[HMM-Theory]] — the HMM requires
stationary inputs for reliable regime detection.

### 3. Portfolio Mathematics (`portfolio.py`)

```python
# Covariance matrix of returns
cov_matrix = compute_covariance(returns_df)

# Eigendecomposition — PCA-style risk decomposition
eigenvalues, eigenvectors = eigendecompose(cov_matrix)

# Half-Kelly position sizing with hard 2% cap
kelly_size = half_kelly(
    win_rate=0.60,
    avg_win=0.02,
    avg_loss=0.01,
    portfolio_value=10000,
    hard_cap_pct=0.02   # never risk more than 2% regardless of Kelly output
)

# Portfolio variance: w^T * Sigma * w
variance = portfolio_variance(weights, cov_matrix)
```

The half-Kelly with 2% hard cap is the same position sizing rule used in
[[Guardrails-RiskManagement]] and [[ClaudeCodeSkills-Trading]].

### 4. AI-Augmented Research Loop (`research.py`)

```
User states a hypothesis:
"I believe RSI(3) has predictive power for next-day returns on BTCUSDT"
    │
    ▼
Workbench selects appropriate statistical tests
    │
    ▼
Runs tests on provided data
    │
    ▼
Asks Claude to interpret results in trading context
    │
    ▼
Returns: "Evidence supports / does not support hypothesis at X% confidence"
```

This is the validation step before promoting any signal to [[ClaudeTradingView-Bot]]
or [[Stocks-Futures-Agent]].

### 5. Coin-Flip Demo (`coinflip.py`)

Solves the expected flips until two consecutive heads using:
- Symbolic math via SymPy
- Monte Carlo simulation (100,000 trials)

Both converge to ~6. This validates the workbench installation and demonstrates
the probability primitives. It is Roan's interview problem from the original framework.

---

## Workflow: Research → Validate → Deploy

```
Hypothesis: "RSI(3) below 30 with price above VWAP predicts positive next-bar return"
    │
    ▼
[[AI-Quant-Workbench]] — statistics.py
    ├── ADF test: is RSI(3) stationary?         ✓ pass
    ├── T-test: is mean return significantly > 0? ✓ pass (p=0.03)
    ├── OLS: how much variance does it explain?   R²=0.12 (moderate)
    └── Residuals: normally distributed?          ✓ pass
    │
    ▼
Signal validated — add to [[VWAP-RSI-EMA-Strategy]] rules.json
    │
    ▼
[[ClaudeTradingView-Bot]] or [[Stocks-Futures-Agent]] executes it live
```

---

## Cost Per Research Session

```
Typical session: ~5,000–15,000 output tokens + ~30,000–80,000 input tokens
At Claude Sonnet 4.6 list pricing: ≈ $0.50 per research session
```

---

## Connecting to HMM Research

The workbench is directly useful for validating HMM inputs and outputs:

| HMM Research Task | Workbench Tool |
|---|---|
| Check returns are stationary | `statistics.py` ADF test |
| Validate regime signal has alpha | `statistics.py` OLS + t-test |
| Size positions by regime confidence | `portfolio.py` half-Kelly |
| Test if regime detection improves Sharpe | `research.py` hypothesis loop |
| Decompose portfolio risk by regime | `portfolio.py` eigendecomposition |

See [[HMM-Theory]] for the theoretical side and [[Backtesting]] for the empirical side.

---

## Invocation Examples

```
"use the ai-quant skill to fit an OLS regression of AAPL returns on SPY returns"

"use the ai-quant skill to test whether my MACD signal has a statistically
 significant positive mean return on 2 years of BTCUSDT daily data"

"use the ai-quant skill to compute half-Kelly position size:
 win rate 62%, avg win 2.1%, avg loss 1.4%, portfolio $8000"

"load the ai-quant skill and run the full research loop on this hypothesis:
 HMM Bull regime predicts above-average next-week SPY returns"
```

---

## Sources

- [GitHub: ai-quant-workbench](https://github.com/jackson-video-resources/ai-quant-workbench)
- [ZeroOne Systems](https://www.skool.com/zero-one)
- [GitHub: markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method)
