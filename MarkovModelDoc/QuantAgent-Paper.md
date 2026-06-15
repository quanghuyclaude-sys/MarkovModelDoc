# QuantAgent — The Academic Framework

> Back to: [[SelfImprovingTradingAgent]]
> Source: [QuantAgent: Seeking Holy Grail in Trading by Self-Improving LLM (arXiv 2402.03755)](https://arxiv.org/abs/2402.03755)

---

## What Is QuantAgent?

QuantAgent is a research paper from 2024 that formalizes the self-improving trading agent pattern into a rigorous two-layer framework. It is the academic foundation for what the video builds in practice.

The core insight: building a domain-specific knowledge base is the bottleneck for LLM agents in specialized fields like quantitative finance. QuantAgent solves this by having the agent automatically build and refine its own knowledge base through iterative backtesting.

---

## The Two-Layer Loop

```
┌──────────────────────────────────────────────┐
│                 OUTER LOOP                   │
│  (runs after every backtest — improves KB)   │
│                                              │
│   Backtest Signal → Compute Metrics          │
│       → Expert Review → Update KB            │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │             INNER LOOP                 │  │
│  │  (runs to generate each signal)        │  │
│  │                                        │  │
│  │  Task → Query KB → Draft Signal        │  │
│  │      → Refine with KB Context          │  │
│  │      → Output Final Signal Code        │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### Inner Loop — Signal Generation with KB Context

The inner agent does not generate signals from scratch. Before drafting, it queries the knowledge base for similar past signals and their outcomes. The draft is refined using that context.

```
Task: "Generate a momentum signal for equity returns"
    │
    ▼
Query KB: "What momentum signals exist? What were their results?"
    │
    ▼
KB returns: 3 prior momentum signals with Sharpe ratios and notes
    │
    ▼
Draft signal incorporating lessons from KB
    │
    ▼
Refine: check for known pitfalls documented in KB
    │
    ▼
Output: signal code + documentation
```

### Outer Loop — Knowledge Base Update

After each signal is backtested, the outer loop updates the KB with the result:

```python
def update_knowledge_base(signal_name: str, signal_code: str,
                          trading_idea: str, backtest_metrics: dict,
                          expert_review: str):
    kb_entry = {
        "name":           signal_name,
        "code":           signal_code,
        "idea":           trading_idea,
        "sharpe":         backtest_metrics["sharpe"],
        "max_drawdown":   backtest_metrics["max_drawdown"],
        "annual_return":  backtest_metrics["annual_return"],
        "expert_review":  expert_review,
        "created_at":     datetime.utcnow().isoformat(),
    }
    knowledge_base.append(kb_entry)
    # Save to persistent storage — this is what makes the agent self-improving
    save_kb(knowledge_base)
```

---

## Knowledge Base Structure

Each entry in the KB documents a financial signal completely:

```json
{
  "name": "momentum_12m_1m",
  "idea": "Buy stocks with strong 12-month return, skip last month (reversal correction)",
  "code": "def signal(returns):\n    mom = returns.rolling(252).sum() - returns.rolling(21).sum()\n    return mom.rank(pct=True) - 0.5",
  "sharpe": 0.84,
  "max_drawdown": -0.18,
  "annual_return": 0.112,
  "expert_review": "Classic Jegadeesh-Titman momentum. Works well in trending markets. Underperforms in reversals. Combine with regime filter.",
  "tags": ["momentum", "equity", "long-short"],
  "created_at": "2024-03-15T10:22:00Z"
}
```

The KB becomes a curated library of what works, what does not, and why.

---

## Why Evaluation Must Be Automatic

The key requirement for the outer loop to work: **backtesting must run programmatically** without human intervention. If a human has to manually run each backtest, the loop breaks.

```python
def auto_backtest(signal_func, price_data: pd.DataFrame) -> dict:
    signals  = price_data.apply(signal_func, axis=1)
    returns  = price_data["close"].pct_change()
    strategy = (signals.shift(1) * returns).dropna()

    annual_return = (1 + strategy).prod() ** (252 / len(strategy)) - 1
    sharpe        = (strategy.mean() / strategy.std()) * (252 ** 0.5)
    max_dd        = ((1 + strategy).cumprod() / (1 + strategy).cumprod().cummax() - 1).min()

    return {"annual_return": annual_return, "sharpe": sharpe, "max_drawdown": max_dd}
```

---

## Empirical Results

From the paper:

- Agent successfully generated a comprehensive signal library over multiple iterations
- Signal quality measurably improved across rounds (later signals had higher Sharpe ratios)
- The KB acted as a filter — the agent stopped regenerating signals that were already documented as failures
- Financial forecasting accuracy increased as the KB grew

---

## Mapping to the Video Implementation

| QuantAgent Component | Video Equivalent |
|---|---|
| Knowledge base (KB) | `journals/` directory + `CLAUDE.md` |
| Inner loop | Single trading cycle (research → decide) |
| Outer loop | Weekly reflection routine |
| Backtest evaluation | P&L tracking in journal JSONL |
| KB update | Human reviews report → updates CLAUDE.md |
| Expert review | Human judgment on proposed rule changes |

The key difference: QuantAgent is fully automated. The video approach keeps a human in the loop for KB updates (CLAUDE.md changes). This is safer for live trading.

---

## Further Reading

- [QuantAgent on arXiv](https://arxiv.org/abs/2402.03755)
- [QuantAgent Abstract Overview](https://arxiv.org/abs/2402.03755v1)
- [TradingGroup: Multi-Agent Trading with Self-Reflection](https://arxiv.org/pdf/2508.17565)
- Related concept: [[SelfImprovementLoop]] (practical implementation)

---

## Sources

- [QuantAgent: Seeking Holy Grail in Trading by Self-Improving LLM](https://arxiv.org/abs/2402.03755)
- [YouTube: How To Build A Self-Improving AI Trading Agent](https://www.youtube.com/watch?v=6njREUQAFdg)
