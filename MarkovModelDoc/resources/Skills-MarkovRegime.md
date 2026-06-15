# Skill: markov-hedge-fund-method (regime)

> Repo: [jackson-video-resources/markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method)
> Back to: [[MarkovHedgeFundMethod]] · [[ClaudeCodeSkills-Trading]]

---

## Install

```bash
# Via Claude Code plugin marketplace (recommended)
/plugin marketplace add jackson-video-resources/markov-hedge-fund-method
/plugin install markov-hedge-fund-method@markov-hedge-fund-method
```

Or build locally from the `markov-hedge-fund-method.md` prompt in Claude Code — every line is visible as it's constructed.

**Zero external dependency install** — uses `uv` with inline PEP 723 metadata. No manual `pip install` required.

---

## Plugin Metadata

```json
{
  "name": "markov-hedge-fund-method",
  "description": "Markov regime detection for any asset. Labels each day Bull/Bear/Sideways from a rolling-return rule, builds the maximum-likelihood transition matrix, forecasts n-step ahead via Chapman-Kolmogorov, solves the stationary distribution, and runs a no-lookahead walk-forward backtest reporting Sharpe and max drawdown. Composes into any trading agent on any asset as a confirmation, signal, or tail-risk layer. Optional Hidden Markov Model upgrade. Framework by Roan (@RohOnChain).",
  "version": "1.0.0",
  "author": { "name": "Lewis Jackson" }
}
```

---

## What It Does

Identifies which market regime — Bull, Bear, or Sideways — an asset is currently trading in, and generates a directional signal from -1 to +1.

### Five Core Functions (`markov_regime.py`)

| Function | Description |
|---|---|
| `label_regimes()` | Classifies daily states from rolling returns vs ±5% threshold |
| `build_transition_matrix()` | Estimates 3×3 transition matrix via maximum likelihood |
| `nstep_forecast()` | Chapman-Kolmogorov n-step probability projection |
| `stationary_distribution()` | Long-run regime mix via eigenvector analysis |
| `walk_forward_backtest()` | No-lookahead backtest; retrains matrix incrementally |

Optional: `fit_hmm()` adds Gaussian Hidden Markov Model via Baum-Welch when `hmmlearn` is available.

---

## Data Input

| Method | How |
|---|---|
| Ticker symbol | `--ticker BTC-USD` — fetches daily closes via yfinance, no API key |
| CSV file | `--csv path/file.csv` — must have `date` and `close` columns |

Works with any asset yfinance supports: stocks, ETFs, crypto, FX, futures.

---

## Output

### Terminal mode (default)
Pretty-printed summary with matrices and performance metrics.

### JSON mode (for agent consumption)

```json
{
  "current_regime": "Bull",
  "transition_matrix": { ... },
  "directional_signal": 0.74,
  "stationary_distribution": { "Bull": 0.45, "Bear": 0.25, "Sideways": 0.30 },
  "sharpe": 0.48,
  "max_drawdown": -0.24
}
```

---

## Three Composition Patterns

How to integrate the regime signal into an existing strategy:

| Pattern | Description |
|---|---|
| **Confirmation Layer** | Gate entry signals — only trade when regime aligns with strategy direction |
| **Risk Filter** | Scale position size based on long-run structural time in Bear regime |
| **Standalone Signal** | Use directional signal directly as a bias: -1 (bearish) to +1 (bullish) |

---

## The Pine Script Indicator

Located at `pine-script/markov-hedge-fund-method.pine` in the repo.

Renders on TradingView:
- Colored ribbon behind price bars (Bull = green, Bear = red, Sideways = grey)
- Current regime banner
- 3×3 transition matrix table (diagonal cells highlighted in green)
- Stationary distribution
- Regime flip labels with debouncing

**Configuration:**
- Lookback window (default: 20 bars)
- Bull threshold (default: +5%)
- Bear threshold (default: -5%)
- Table position and text size

**Technical:** Uses `var` arrays for persistent transition counts, unrolled 3×3 matrix multiplication for Pine v5 compatibility, computation gated on `barstate.islast`.

---

## Attribution

Framework designed by **Roan (@RohOnChain)**. Plugin and installer built by **Lewis Jackson**. MIT License.

---

## Related Files

- [[MarkovHedgeFundMethod]] — full pipeline walkthrough
- [[HMM-Theory]] — mathematical foundation
- [[HMM-Implementation-Python]] — hmmlearn-based full HMM implementation
- [[TradingViewPineScript]] — Pine Script usage context
- [[RegimeFilter-RiskManagement]] — how to wire the regime output into a risk filter
