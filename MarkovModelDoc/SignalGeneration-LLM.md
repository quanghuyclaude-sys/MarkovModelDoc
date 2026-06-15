# Signal Generation — How Claude Makes Trading Decisions

> Back to: [[SelfImprovingTradingAgent]]
> Sources: [MindStudio: Build a 24/7 AI Trading Agent](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca) · [Joseph Fluckiger: Building an AI Trading Agent with Claude](https://josephfluckiger.blogspot.com/2026/01/building-ai-trading-agent-with-claude.html)

---

## How It Works

Claude receives a structured JSON market snapshot from [[MarketResearchModule]] and returns a structured JSON decision. The system prompt (in `CLAUDE.md`) defines the rules, risk limits, and output format. Claude reasons over the data and produces one of three decisions: `BUY`, `SELL`, or `NO_TRADE`.

The default is always `NO_TRADE`. Cash is a position.

---

## System Prompt Design (CLAUDE.md)

This is the most important file in the project. Every routine fires with Claude reading this first.

```markdown
# Trading Agent System Prompt

## Your Role
You are a disciplined quantitative trading agent. Your job is to analyze
market data and make conservative, evidence-based trading decisions.

## Decision Rules
- Default to NO_TRADE when uncertain — do not force trades
- RSI above 75: do not initiate new long positions
- RSI below 25: do not initiate new short positions
- Only trade in the direction of the MA cross (bullish cross = longs only)
- Never average down into a losing position
- If already holding a position in a symbol, output HOLD or SELL only

## Risk Constraints
- Never risk more than 2% of portfolio on a single trade
- Never invest more than 5% of portfolio in a single position
- Always use limit orders — never market orders
- If a position drops 8% from entry, output SELL immediately

## Output Format
You MUST return a valid JSON object with exactly these fields:
{
  "decision":  "BUY" | "SELL" | "NO_TRADE",
  "symbol":    "TICKER" or null,
  "qty":       integer or null,
  "limit_price": float or null,
  "reasoning": "2-3 sentences explaining your decision",
  "confidence": "LOW" | "MEDIUM" | "HIGH"
}

Return ONLY the JSON object. No markdown, no explanation outside the JSON.
```

---

## The Decision Function

```python
import json
import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = open("CLAUDE.md").read()

def claude_decide(snapshot: dict) -> dict:
    user_message = f"""
Analyze this market snapshot and return your trading decision as JSON:

{json.dumps(snapshot, indent=2)}

Remember: default to NO_TRADE on uncertainty. Return ONLY valid JSON.
"""
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=512,
        temperature=0.3,          # low temperature = more consistent decisions
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = response.content[0].text.strip()

    try:
        decision = json.loads(raw)
        assert decision["decision"] in ("BUY", "SELL", "NO_TRADE")
        return decision
    except (json.JSONDecodeError, AssertionError, KeyError):
        # Any parsing failure → safe fallback
        return {
            "decision":    "NO_TRADE",
            "symbol":       snapshot["symbol"],
            "qty":          None,
            "limit_price":  None,
            "reasoning":    f"JSON parse error on raw response: {raw[:100]}",
            "confidence":   "LOW"
        }
```

---

## Confidence Level Semantics

| Level | Meaning | Action |
|---|---|---|
| `HIGH` | Strong signal alignment across price, RSI, news, trend | Execute if guardrails pass |
| `MEDIUM` | Partial signal — some indicators agree, some neutral | Execute with reduced size |
| `LOW` | Weak or conflicting signals | Reject — do not execute |

The [[Guardrails-RiskManagement]] layer enforces this: LOW confidence orders are blocked in code, not just in the prompt.

---

## Prompt Engineering Lessons

From Joseph Fluckiger's production deployment (500+ signals, several weeks):

| Problem observed | Fix applied |
|---|---|
| Too many HOLD outputs | Added "Be decisive — NO_TRADE is fine, HOLD is not a valid output" |
| Confidence scores clustered at 0.5 | Added explicit calibration guidance: "HIGH = 3+ indicators agree" |
| Tech stock bias | Discovered via logs → added "Distribute attention across all watchlist symbols" |
| Verbose reasoning eating tokens | Changed to "2-3 sentences max" in system prompt |

---

## Temperature Setting

Use **low temperature (0.2–0.3)** for trading decisions. Higher temperature = more creative but less consistent. A trading agent needs repeatability — given the same snapshot, it should reach the same decision.

```python
# Good for trading decisions
temperature=0.3

# Never for trading (hallucination risk)
temperature=1.0
```

---

## Multi-Symbol Batching

Process each symbol independently to avoid context bleeding:

```python
def run_signal_generation(watchlist: list[dict]) -> list[dict]:
    decisions = []
    for symbol_config in watchlist:
        snapshot = build_market_snapshot(symbol_config["ticker"])
        decision = claude_decide(snapshot)
        decision["max_allocation_pct"] = symbol_config["max_allocation_pct"]
        decisions.append(decision)
    return decisions
```

Do **not** pass all symbols in one prompt — Claude may trade-off between symbols in ways that violate individual position limits.

---

## Output Validation Schema

```python
REQUIRED_FIELDS = {"decision", "symbol", "qty", "limit_price", "reasoning", "confidence"}
VALID_DECISIONS = {"BUY", "SELL", "NO_TRADE"}
VALID_CONFIDENCE = {"LOW", "MEDIUM", "HIGH"}

def validate_decision(d: dict) -> bool:
    if not REQUIRED_FIELDS.issubset(d.keys()):
        return False
    if d["decision"] not in VALID_DECISIONS:
        return False
    if d["confidence"] not in VALID_CONFIDENCE:
        return False
    if d["decision"] in ("BUY", "SELL") and not d["qty"]:
        return False
    return True
```

---

## Integration with HMM Regime Filter

If you are combining this agent with the [[HiddenMarkovTrading]] strategy, add the current regime to the market snapshot before passing to Claude:

```python
snapshot["hmm_regime"]        = "Bull"     # from HMM model
snapshot["hmm_signal_score"]  = 0.74       # bull_prob - bear_prob
snapshot["hmm_bull_prob"]     = 0.82
snapshot["hmm_bear_prob"]     = 0.08
```

Then add to `CLAUDE.md`:
```
- Only initiate BUY decisions when hmm_regime is "Bull" and hmm_signal_score > 0.5
- In Bear regime: only SELL or NO_TRADE
```

---

## Sources

- [MindStudio: Build a 24/7 AI Trading Agent with Claude Code and Alpaca](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca)
- [Joseph Fluckiger: Building an AI Trading Agent with Claude](https://josephfluckiger.blogspot.com/2026/01/building-ai-trading-agent-with-claude.html)
- [YouTube: How To Build A Self-Improving AI Trading Agent](https://www.youtube.com/watch?v=6njREUQAFdg)
