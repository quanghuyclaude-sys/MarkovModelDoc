# TradingView Pine Script — Regime Visualization

> Back to strategy hub: [[HiddenMarkovTrading]]
> Source: [GitHub: markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method)

---

## Overview

The markov-hedge-fund-method repository includes a **Pine Script indicator** for TradingView that visualizes:
- Regime ribbons (colored chart background by regime)
- Transition probability table (on-chart 3x3 matrix)
- Directional signal oscillator

Note: Pine Script runs client-side in TradingView and cannot run a full HMM natively. The indicator approximates regimes using rolling return windows — the same rule-based method from the Python implementation.

---

## Core Regime Detection Logic (Pine Script)

```pine
//@version=5
indicator("Markov Regime Detector", overlay=true)

// --- Inputs ---
window       = input.int(20,   "Regime Window (days)")
bull_thresh  = input.float(0.05, "Bull Threshold")
bear_thresh  = input.float(-0.05, "Bear Threshold")

// --- Rolling return ---
rolling_ret  = (close - close[window]) / close[window]

// --- Regime classification ---
is_bull      = rolling_ret > bull_thresh
is_bear      = rolling_ret < bear_thresh
is_sideways  = not is_bull and not is_bear

// --- Background ribbon ---
bgcolor(is_bull     ? color.new(color.green, 85) : na)
bgcolor(is_bear     ? color.new(color.red,   85) : na)
bgcolor(is_sideways ? color.new(color.gray,  90) : na)

// --- Label current regime ---
regime_label = is_bull ? "BULL" : is_bear ? "BEAR" : "SIDEWAYS"
label.new(bar_index, high, regime_label, style=label.style_none,
          color=color.new(color.white, 100), textcolor=color.white, size=size.tiny)
```

---

## Directional Signal Oscillator

```pine
// --- Signal: bull probability estimate (simplified) ---
// Uses momentum as a proxy for regime probability

fast_ma  = ta.ema(close, 10)
slow_ma  = ta.ema(close, 30)
trend    = (fast_ma - slow_ma) / slow_ma

// Normalize to [-1, +1] approximating bull_prob - bear_prob
signal   = math.max(-1.0, math.min(1.0, trend * 20))

// Plot signal on separate pane
plot(signal,  "Directional Signal", color=color.yellow, display=display.pane)
hline(0.53,  "Bull Threshold",  color=color.green, linestyle=hline.style_dashed)
hline(-0.53, "Bear Threshold",  color=color.red,   linestyle=hline.style_dashed)
hline(0,     "Neutral",         color=color.gray,  linestyle=hline.style_solid)
```

---

## Transition Matrix Table

```pine
// --- On-chart transition probability table ---
var table t = table.new(position.top_right, 4, 4, border_width=1)

// Headers
if barstate.islast
    table.cell(t, 0, 0, "",          bgcolor=color.gray)
    table.cell(t, 1, 0, "→Bull",     bgcolor=color.gray, text_color=color.white)
    table.cell(t, 2, 0, "→Bear",     bgcolor=color.gray, text_color=color.white)
    table.cell(t, 3, 0, "→Sideways", bgcolor=color.gray, text_color=color.white)
    table.cell(t, 0, 1, "Bull",      bgcolor=color.new(color.green, 60), text_color=color.white)
    table.cell(t, 0, 2, "Bear",      bgcolor=color.new(color.red,   60), text_color=color.white)
    table.cell(t, 0, 3, "Sideways",  bgcolor=color.new(color.gray,  60), text_color=color.white)
    // Values populated from Python-computed probabilities pasted as inputs
```

> For live transition probabilities, compute the 3×3 matrix in Python (see [[MarkovHedgeFundMethod]]) and paste the values as Pine Script inputs.

---

## Entry/Exit Signals on Chart

```pine
// --- Trade signals ---
long_signal  = ta.crossover(fast_ma, slow_ma) and is_bull
exit_signal  = ta.crossunder(fast_ma, slow_ma)

plotshape(long_signal, "Buy",  shape.triangleup,   location.belowbar,
          color=color.green, size=size.small)
plotshape(exit_signal, "Sell", shape.triangledown,  location.abovebar,
          color=color.red,   size=size.small)
```

---

## Regime Ribbon (Alternative — Using Fills)

```pine
bull_fill = plot(is_bull     ? high * 1.001 : na, color=color.new(color.green, 90))
bear_fill = plot(is_bear     ? high * 1.001 : na, color=color.new(color.red,   90))
side_fill = plot(is_sideways ? high * 1.001 : na, color=color.new(color.gray,  95))
base      = plot(close, display=display.none)

fill(bull_fill, base, color=color.new(color.green, 90))
fill(bear_fill, base, color=color.new(color.red,   90))
```

---

## Limitations of Pine Script vs Python HMM

| Capability | Pine Script | Python hmmlearn |
|---|---|---|
| True HMM fitting | No | Yes |
| Transition matrix calculation | Manual/hardcoded | Automatic |
| Chapman-Kolmogorov forecast | Manual | Automatic |
| Viterbi state sequence | Approximated via SMA | Exact |
| Custom feature inputs | Limited | Unlimited |

Use Pine Script for **visual confirmation** and trade alerts. Use the Python model for **signal generation** — then replicate entry/exit rules in Pine for execution.

---

## Workflow: Python → TradingView

1. Run the Python HMM on your ticker (see [[HMM-Implementation-Python]])
2. Export regime labels and signal values to CSV
3. Import as custom data into TradingView, or
4. Hardcode computed transition probabilities as Pine Script inputs
5. Use Pine signals for alerts and order management

---

## Related Files

- [[MarkovHedgeFundMethod]] — source of the Pine Script indicator
- [[SignalGeneration]] — the signal logic being visualized
- [[MarketRegimes]] — what the colored ribbons represent

---

## Sources

- [GitHub: markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method)
- [YouTube: I Re-Created A Quant Trading Strategy With Claude Code](https://www.youtube.com/watch?v=ZVMTeDBmSrI&t=1134s)
