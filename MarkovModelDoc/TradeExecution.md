# Trade Execution — Alpaca API & Order Management

> Back to: [[SelfImprovingTradingAgent]]
> Sources: [MindStudio: Build a 24/7 AI Trading Agent](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca) · [Tradewink: Build an AI Trading Agent with Alpaca API](https://www.tradewink.com/learn/build-ai-agent-alpaca-tutorial)

---

## Execution Principle

**Never let an LLM submit orders without hard-coded risk checks.**

Claude's decision output is a *recommendation*, not a command. A separate code layer validates every field before any API call is made. This is the last line of defense before real money moves.

---

## Alpaca API Setup

```python
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import os

# Start with paper=True — always
trade_client = TradingClient(
    api_key=os.environ["APCA_API_KEY_ID"],
    secret_key=os.environ["APCA_API_SECRET_KEY"],
    paper=True   # switch to False only after 90+ days of paper testing
)
```

### Key REST Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /v2/account` | Cash, equity, buying power |
| `GET /v2/positions` | All open positions |
| `GET /v2/positions/{symbol}` | Single position |
| `POST /v2/orders` | Submit an order |
| `DELETE /v2/orders/{id}` | Cancel an order |
| `GET /v2/orders` | List orders |
| `GET /v2/clock` | Market open/closed status |
| `GET /v2/calendar` | Trading calendar |

---

## Position Sizing

Never let Claude choose raw share counts — always compute sizing from risk rules in code:

```python
def compute_position_size(
    account_equity: float,
    current_price: float,
    stop_price: float,
    risk_pct: float = 0.02,        # risk 2% of portfolio per trade
    max_allocation_pct: float = 0.05,  # max 5% of portfolio in one position
) -> int:
    # Risk-based sizing: risk_amount / risk_per_share
    risk_amount   = account_equity * risk_pct
    risk_per_share = abs(current_price - stop_price)
    risk_based_qty = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0

    # Allocation-based ceiling
    max_value     = account_equity * max_allocation_pct
    alloc_based_qty = int(max_value / current_price)

    # Take the more conservative of the two
    return min(risk_based_qty, alloc_based_qty)
```

---

## Order Submission

Always use **limit orders**, never market orders. Set the limit within 0.2% of the current ask to ensure fills while preventing slippage:

```python
def submit_limit_order(
    symbol: str,
    qty: int,
    side: str,           # "BUY" or "SELL"
    current_price: float,
    slippage_pct: float = 0.002,
) -> dict:

    if side == "BUY":
        limit_price = round(current_price * (1 + slippage_pct), 2)
        order_side  = OrderSide.BUY
    else:
        limit_price = round(current_price * (1 - slippage_pct), 2)
        order_side  = OrderSide.SELL

    order_req = LimitOrderRequest(
        symbol=symbol,
        qty=qty,
        side=order_side,
        time_in_force=TimeInForce.DAY,   # expires end of session if unfilled
        limit_price=limit_price
    )

    try:
        order = trade_client.submit_order(order_req)
        return {"status": "submitted", "order_id": str(order.id), "limit_price": limit_price}
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

---

## Pre-Execution Validation Layer

```python
def validate_and_execute(decision: dict, account: dict, current_price: float) -> dict:
    symbol = decision["symbol"]
    equity = account["equity"]
    cash   = account["cash"]
    n_open = len(account["open_positions"])

    # 1. Confidence gate
    if decision["confidence"] == "LOW":
        return {"executed": False, "reason": "Low confidence — blocked"}

    # 2. Max concurrent positions
    if decision["decision"] == "BUY" and n_open >= 5:
        return {"executed": False, "reason": "Max 5 positions reached"}

    # 3. Cash reserve check (must keep 20% cash)
    order_value = (decision.get("qty") or 0) * current_price
    if cash - order_value < equity * 0.20:
        return {"executed": False, "reason": "Would breach 20% cash reserve"}

    # 4. Max allocation per position
    if order_value / equity > 0.05:
        return {"executed": False, "reason": "Exceeds 5% position limit"}

    # 5. Market hours
    from alpaca.trading.client import TradingClient
    clock = trade_client.get_clock()
    if not clock.is_open:
        return {"executed": False, "reason": "Market is closed"}

    # All checks passed — submit
    result = submit_limit_order(symbol, decision["qty"], decision["decision"], current_price)
    result["executed"] = result["status"] == "submitted"
    return result
```

---

## Stop-Loss Automation

Do not rely on Claude to notice a stop being hit. Set bracket orders or monitor in code:

```python
def place_bracket_order(symbol: str, qty: int, entry_price: float,
                         stop_pct: float = 0.08, target_pct: float = 0.15) -> dict:
    from alpaca.trading.requests import OrderRequest

    stop_price   = round(entry_price * (1 - stop_pct), 2)
    target_price = round(entry_price * (1 + target_pct), 2)

    # Alpaca bracket order: entry + stop + take-profit in one request
    order = trade_client.submit_order(OrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY,
        type="limit",
        time_in_force=TimeInForce.GTC,
        limit_price=round(entry_price * 1.002, 2),
        order_class="bracket",
        stop_loss={"stop_price": stop_price},
        take_profit={"limit_price": target_price},
    ))
    return {"order_id": str(order.id), "stop": stop_price, "target": target_price}
```

---

## Pattern Day Trader (PDT) Rule

If account equity is below $25,000:
- Maximum **3 round-trip day trades** per rolling 5-business-day period
- Violating this gets the account flagged and restricted for 90 days

Add this check:

```python
def check_pdt_safe(account) -> bool:
    equity = float(account.equity)
    daytrade_count = int(account.daytrade_count)
    if equity < 25000 and daytrade_count >= 3:
        return False   # block day trades
    return True
```

---

## Paper Trading Checklist Before Going Live

- [ ] 90+ days of paper trading with 100+ completed trades
- [ ] Positive Sharpe ratio on paper results
- [ ] Max drawdown within acceptable limits
- [ ] Stop-loss triggers tested intentionally
- [ ] All error paths (API down, bad JSON, market closed) confirmed
- [ ] Daily loss limit halt confirmed working
- [ ] Bracket orders confirmed filling correctly

---

## Sources

- [MindStudio: Build a 24/7 AI Trading Agent with Claude Code and Alpaca](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca)
- [Tradewink: Build an AI Trading Agent with Alpaca API](https://www.tradewink.com/learn/build-ai-agent-alpaca-tutorial)
- [YouTube: How To Build A Self-Improving AI Trading Agent](https://www.youtube.com/watch?v=6njREUQAFdg)
