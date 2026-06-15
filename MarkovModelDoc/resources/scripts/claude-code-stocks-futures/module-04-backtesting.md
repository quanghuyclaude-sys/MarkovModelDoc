# Module 04 — Backtesting & ML Training Loop

> Source: github.com/jackson-video-resources/claude-code-stocks-futures/prompts/module-04-backtesting.md
> Part of: [[Stocks-Futures-Agent]]

---

## Section 4.3 — Baseline Testing

Start with a single strategy implementation using yfinance data. Record as reference:
- Sharpe ratio
- Max drawdown
- Win rate

---

## Section 4.4 — Iterative Refinement

Rule: **make one change at a time**. Adjust individual parameters (EMA periods, filters, stop losses) and monitor impact. Revert if:
- Sharpe deteriorates
- Trade count drops below 50
- Drawdown increases

---

## Section 4.5 — Parameter Optimization

```
"Run automated parameter sweeps across multiple combinations, storing results in SQLite.
Optimize on the first 16 months of data.
Validate the top 10 combinations on the remaining 8 months.
Flag any combination that shows significant in-sample vs out-of-sample divergence as overfit."
```

---

## Section 4.6 — Self-Improving Loop

Build a system with four components:

```
"Build a self-improving trading system with:
1. Trade logging mechanism
2. Parameter storage and versioning
3. Automated retraining scheduler — triggers on 100 new trades or weekly
4. Result comparison logic — only updates parameters if new Sharpe exceeds current by 5%+"
```

This creates a feedback loop: live trades → retrain → better parameters → better live trades.

---

## Related Files

- [[Backtesting]] — walk-forward methodology
- [[SelfImprovementLoop]] — the broader self-improvement pattern
- [[Skills-StrategyAudit]] — audit before deploying
