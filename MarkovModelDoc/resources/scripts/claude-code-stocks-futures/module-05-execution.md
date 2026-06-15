# Module 05 — Paper Trading Execution

> Source: github.com/jackson-video-resources/claude-code-stocks-futures/prompts/module-05-execution.md
> Part of: [[Stocks-Futures-Agent]]

---

## Section 5.2 — Execution Layer Prompt

```
"Build an execution layer that:
- Monitors for buy and sell signals from the strategy
- Submits market orders to Alpaca when buy signals trigger for NQ1!
- Computes position sizing to risk exactly 1% of account capital
- Uses stop loss distance for sizing:
    $10,000 account × 1% risk = $100 risk
    47-point stop × $20/point = $940 risk per contract
    Position size = $100 / $940 = 0.1 contracts → use MNQ (micro, $2/point)
- Sets take profit at 2:1 reward-to-risk ratio automatically
- Returns order confirmation or error message"
```

**Customize:** Swap `NQ1!`, point value, and stop distance for your instrument.

---

## Position Sizing Formula

```
position_size = (account_balance × risk_pct) / (stop_distance × point_value)
```

Example for $10k account, 1% risk, 47pt stop, $20/pt:
```
$10,000 × 0.01 / (47 × $20) = 0.106 contracts → round down to 0.1
```

For retail trading with fractional contracts unavailable, use MNQ ($2/point) instead of NQ ($20/point).

---

## How the Execution Layer Works

1. Strategy module generates signal
2. Execution layer reads current account balance via Alpaca API
3. Calculates position size from formula above
4. Places bracket order: entry + stop loss + take profit
5. Returns order ID and status

---

## Related Files

- [[TradeExecution]] — the full execution pattern with risk guardrails
- [[Guardrails-RiskManagement]] — safety checks before every order
