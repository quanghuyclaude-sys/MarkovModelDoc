# Self-Improving AI Trading Agent — Central Hub

> Source video: [How To Build A Self-Improving AI Trading Agent (Insanely Cool)](https://www.youtube.com/watch?v=6njREUQAFdg)
> Related build: [How to Build a 24/7 AI Trading Agent with Claude Code Routines](https://www.mindstudio.ai/blog/how-to-build-ai-trading-agent-claude-code-routines)
> Academic foundation: [QuantAgent — Seeking Holy Grail in Trading by Self-Improving LLM](https://arxiv.org/abs/2402.03755)

---

## What This Is

A **fully autonomous, self-improving trading system** powered by Claude Code. It runs on a schedule, researches markets, makes decisions, executes trades, and writes a journal of its own reasoning — then uses that journal to improve itself over time.

The key property: the agent's **outputs become its next inputs**. Every journal entry is potential training signal for the next cycle. This is what makes it self-improving rather than just automated.

---

## How It Works (One Sentence)

Every 15–30 minutes during market hours, Claude fetches market data → analyzes it → decides to buy, sell, or do nothing → executes the order via Alpaca → writes a journal entry explaining its reasoning → periodically re-reads past journals to find patterns and update its own instructions.

---

## System Architecture

```
┌─────────────────────────────────────────────────┐
│              Claude Code Routine                 │
│         (runs every 15–30 min, market hours)     │
└───────────────────┬─────────────────────────────┘
                    │
          ┌─────────▼──────────┐
          │  Market Research   │  ← Price, news, RSI, VWAP
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │  Signal Generation │  ← Claude reasons → JSON decision
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │  Risk Guardrails   │  ← Hard-coded code-level checks
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │  Order Execution   │  ← Alpaca API (paper or live)
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐
          │   Trade Journal    │  ← Append-only JSONL / Markdown
          └─────────┬──────────┘
                    │
          ┌─────────▼──────────┐      weekly
          │  Self-Improvement  │ ◄──────────── Journal history
          │  (Reflection Loop) │
          └────────────────────┘
```

---

## Knowledge Map

| Topic | File | Purpose |
|---|---|---|
| Full 4-stage pipeline | [[AgentArchitecture]] | Read first |
| How Claude Code Routines work | [[ClaudeCodeRoutines]] | Scheduling |
| Fetching price, news, indicators | [[MarketResearchModule]] | Data layer |
| How Claude makes trading decisions | [[SignalGeneration-LLM]] | Brain of the agent |
| Alpaca API, order types, sizing | [[TradeExecution]] | Execution layer |
| Journal format and logging | [[TradeJournal]] | Memory layer |
| How the agent learns from itself | [[SelfImprovementLoop]] | The key differentiator |
| Multi-layer safety system | [[Guardrails-RiskManagement]] | Safety |
| Academic theory behind the pattern | [[QuantAgent-Paper]] | Deep theory |
| Cloud deploy, monitoring, costs | [[Deployment]] | Production |

---

## Quick-Start Build Order

1. Set up Alpaca paper trading account and get API keys
2. Read [[ClaudeCodeRoutines]] — understand how to schedule Claude
3. Build [[MarketResearchModule]] — get data flowing first
4. Design [[SignalGeneration-LLM]] — the system prompt is everything
5. Add [[Guardrails-RiskManagement]] before any real money
6. Wire [[TradeExecution]] — test with paper trading for 90+ days
7. Set up [[TradeJournal]] — this enables everything else
8. Implement [[SelfImprovementLoop]] — the journal feeds back in
9. Follow [[Deployment]] for production infrastructure

---

## Cost Profile

| Component | Estimated Cost |
|---|---|
| Claude API (15-min cycles, ~26/day) | $0.26–$1.30/day |
| Alpaca (paper trading) | Free |
| Alpaca (live trading) | Free (commission-free) |
| News API (Polygon.io) | ~$29/month starter |
| Cloud hosting (VPS/Lambda) | $5–$20/month |

---

## Key Performance Results (From Real Builds)

| Builder | Result | Source |
|---|---|---|
| Saulius (commodity futures, 2026) | Sharpe 1.72, 38.7% annualized, 80% positive RankIC | MindStudio |
| Chudi Nnorukam (autonomous bot) | API cost $340→$136/mo, uptime 99.2%, error rate 1/6→1/40 | MindStudio |
| Joseph Fluckiger (news signal bot) | 500+ signals, ~$0.04/day API cost, tech bias discovered via logs | Blog |

---

## Related Strategy Files

This agent can be used to trade the signals from [[HiddenMarkovTrading]] — the HMM generates regime-aware signals, and this agent executes and improves them autonomously.

---

## Sources

- [YouTube: How To Build A Self-Improving AI Trading Agent](https://www.youtube.com/watch?v=6njREUQAFdg)
- [MindStudio: Build a 24/7 AI Trading Agent with Claude Code and Alpaca](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca)
- [MindStudio: Claude Code Routines](https://www.mindstudio.ai/blog/how-to-build-ai-trading-agent-claude-code-routines)
- [QuantAgent Paper (arXiv)](https://arxiv.org/abs/2402.03755)
- [Tradewink: Build an AI Trading Agent with Alpaca API](https://www.tradewink.com/learn/build-ai-agent-alpaca-tutorial)
- [Joseph Fluckiger: Building an AI Trading Agent with Claude](https://josephfluckiger.blogspot.com/2026/01/building-ai-trading-agent-with-claude.html)
