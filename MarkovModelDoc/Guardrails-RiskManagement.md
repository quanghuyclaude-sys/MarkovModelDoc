# Guardrails & Risk Management — Multi-Layer Safety System

> Back to: [[SelfImprovingTradingAgent]]
> Sources: [MindStudio: Build a 24/7 AI Trading Agent](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca) · [Medium: Before You Use Claude Code for Trading](https://medium.com/@aiintrading/before-you-use-claude-code-for-trading-15-things-you-should-know-6dbfd42b381e)

---

## Three-Layer Safety Architecture

No single guardrail is sufficient. The system uses three independent layers, each catching failures the others might miss.

```
Layer 1: CLAUDE.md rules (natural language — Claude reads and reasons about them)
    │
    ▼
Layer 2: Code validation (hard checks before any API call — Claude cannot bypass these)
    │
    ▼
Layer 3: Alpaca platform protections (broker-level — day trade limits, margin controls)
```

A trade must pass all three layers to execute.

---

## Layer 1 — CLAUDE.md Rules (Agent-Level)

Plain-language rules Claude reads at every routine start. They shape Claude's reasoning before it produces a decision.

```markdown
## Hard Limits (Never violate)
- Never invest more than 5% of total portfolio in a single position
- Never place a market order — always limit orders within 0.2% of ask
- Close any position that drops 8% from entry without waiting for a signal
- Keep at least 20% of portfolio in cash at all times
- Stop all trading if daily P&L loss exceeds 3% of starting equity

## Signal Quality Rules
- DEFAULT to NO_TRADE when uncertain — do not force trades
- Do not buy when RSI > 75 unless you have a specific contrarian thesis
- Require at least 2 confirming indicators before entering (price + RSI + news or trend)

## Position Management
- Never average down into a losing position
- Journal every decision including NO_TRADE — explain why

## Market Hours
- Only trade between 10:00 AM and 3:30 PM ET
- Always verify market is open via Alpaca clock API before any order
- Do not trade the first 30 minutes after open (9:30–10:00) — too volatile
```

---

## Layer 2 — Code Validation (Hard-Coded Checks)

These run in Python before any API call. Claude cannot override them.

```python
class RiskGuardrails:
    def __init__(self, max_position_pct=0.05, cash_reserve_pct=0.20,
                 max_positions=5, daily_loss_limit_pct=0.03):
        self.max_position_pct  = max_position_pct
        self.cash_reserve_pct  = cash_reserve_pct
        self.max_positions     = max_positions
        self.daily_loss_limit  = daily_loss_limit_pct
        self.starting_equity   = None
        self.blocked           = False

    def check_daily_loss(self, current_equity: float) -> bool:
        if self.starting_equity is None:
            self.starting_equity = current_equity
            return True
        loss_pct = (self.starting_equity - current_equity) / self.starting_equity
        if loss_pct >= self.daily_loss_limit:
            self.blocked = True
            return False
        return True

    def validate(self, decision: dict, account: dict, current_price: float) -> tuple:
        if self.blocked:
            return False, "Daily loss limit hit — trading halted for the day"
        if decision["confidence"] == "LOW":
            return False, "LOW confidence — rejected"
        if decision["decision"] == "NO_TRADE":
            return True, "NO_TRADE approved"

        qty          = decision.get("qty") or 0
        equity       = account["equity"]
        cash         = account["cash"]
        order_value  = qty * current_price
        allocation   = order_value / equity

        if decision["decision"] == "BUY":
            if allocation > self.max_position_pct:
                return False, f"Allocation {allocation:.1%} exceeds limit"
            if cash - order_value < equity * self.cash_reserve_pct:
                return False, "Would breach cash reserve"
            if len(account["open_positions"]) >= self.max_positions:
                return False, "Max positions reached"
        return True, "Approved"
```

---

## Layer 3 — Alpaca Platform Protections

Handled automatically by the broker — no code required:

| Protection | Description |
|---|---|
| Buying power check | Rejects orders exceeding available buying power |
| PDT rule enforcement | Flags accounts under $25K exceeding 3 day trades per 5 days |
| Margin limits | Prevents over-leveraging |
| Price collars | Rejects limit orders far outside the current market |

---

## Daily Loss Limit Circuit Breaker

```python
def run_trading_cycle(guardrails: RiskGuardrails, watchlist: list):
    account = get_account_state()
    if not guardrails.check_daily_loss(account["equity"]):
        append_journal_entry(
            symbol="SYSTEM", decision="HALTED",
            reasoning="Daily loss limit reached. Trading suspended.",
            confidence="HIGH"
        )
        return

    for symbol_config in watchlist:
        snapshot = build_market_snapshot(symbol_config["ticker"])
        decision = claude_decide(snapshot)
        approved, reason = guardrails.validate(decision, account, snapshot["price"])
        result = submit_limit_order(...) if approved else {"executed": False, "reason": reason}
        append_journal_entry(snapshot, decision, result)
```

---

## Stop-Loss Monitoring (Intra-Day)

Do not rely on Claude to monitor positions each cycle. Use a dedicated monitor:

```python
def monitor_open_positions(stop_pct: float = 0.08):
    for pos in trade_client.get_all_positions():
        pnl_pct = float(pos.unrealized_plpc)
        if pnl_pct <= -stop_pct:
            trade_client.close_position(pos.symbol)
            append_journal_entry(
                symbol=pos.symbol, decision="SELL",
                reasoning=f"Stop-loss triggered at {pnl_pct:.1%}. Auto-closed.",
                confidence="HIGH"
            )
```

---

## Risk Summary Table

| Risk | Layer | Mechanism |
|---|---|---|
| Oversized position | 1 + 2 | CLAUDE.md + code allocation check |
| Low confidence trade | 1 + 2 | CLAUDE.md + confidence gate |
| Market orders | 1 | CLAUDE.md rule |
| Market closed trading | 1 + 2 | CLAUDE.md + Alpaca clock check |
| Daily drawdown | 2 | Circuit breaker |
| Stop-loss breach | 2 | Auto-close position monitor |
| PDT violation | 3 | Alpaca enforcement |

---

## Sources

- [MindStudio: Build a 24/7 AI Trading Agent with Claude Code and Alpaca](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca)
- [Medium: Before You Use Claude Code for Trading](https://medium.com/@aiintrading/before-you-use-claude-code-for-trading-15-things-you-should-know-6dbfd42b381e)
- [YouTube: How To Build A Self-Improving AI Trading Agent](https://www.youtube.com/watch?v=6njREUQAFdg)
