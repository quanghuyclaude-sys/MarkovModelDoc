# ZeroOne Systems — Resource Hub

> Community: [skool.com/zero-one](https://www.skool.com/zero-one) (login required for classroom)
> Creator: Lewis Jackson — [YouTube](https://www.youtube.com/@LewisWJackson) · [GitHub](https://github.com/jackson-video-resources)
> Mission: "Turn AI Agents into Income" — live challenge: £50k → £500k ([live dashboard](https://www.youtube.com/watch?v=Eozt4PHbKt8))

---

## Access Note

The Skool classroom interior requires membership login. Everything documented here
is sourced from Lewis Jackson's **public** GitHub repositories, YouTube videos, and
published articles — all free, no paywall.

---

## What ZeroOne Systems Covers

A complete end-to-end stack for building autonomous AI trading systems:

| Layer | Tool | File |
|---|---|---|
| Chart reading + automation | TradingView MCP | [[TradingView-MCP]] |
| Crypto auto-trader (BitGet) | claude-tradingview-mcp-trading | [[ClaudeTradingView-Bot]] |
| 6-agent trading firm | paperclip-zero-human-trading-firm | [[ZeroHumanTradingFirm]] |
| Stocks, futures, Forex (Alpaca) | claude-code-stocks-futures | [[Stocks-Futures-Agent]] |
| Mine YouTube traders for strategy | yt-strategy-agent | [[YT-StrategyAgent]] |
| Claude Code skills library | skills (backtest, risk-manager, etc.) | [[ClaudeCodeSkills-Trading]] |
| Quant research workbench | ai-quant-workbench | [[AI-Quant-Workbench]] |
| Example live strategy | VWAP + RSI(3) + EMA(8) scalper | [[VWAP-RSI-EMA-Strategy]] |

---

## GitHub Organisation — All Repos

| Repo | Stars | Language | Purpose |
|---|---|---|---|
| [claude-tradingview-mcp-trading](https://github.com/jackson-video-resources/claude-tradingview-mcp-trading) | 470 | JS | Claude + TradingView → BitGet |
| [markov-hedge-fund-method](https://github.com/jackson-video-resources/markov-hedge-fund-method) | 276 | Python | HMM regime detection |
| [paperclip-zero-human-trading-firm](https://github.com/jackson-video-resources/paperclip-zero-human-trading-firm) | 103 | — | 6-agent trading firm |
| [claude-code-stocks-futures](https://github.com/jackson-video-resources/claude-code-stocks-futures) | 14 | — | Alpaca stocks/futures/Forex |
| [yt-strategy-agent](https://github.com/jackson-video-resources/yt-strategy-agent) | 18 | Python | YouTube → strategy doc |
| [skills](https://github.com/jackson-video-resources/skills) | 8 | MIT | Claude Code skill library |
| [ai-quant-workbench](https://github.com/jackson-video-resources/ai-quant-workbench) | 5 | Python | Quant research toolkit |
| [tradingview-mcp-jackson](https://github.com/LewisWJackson/tradingview-mcp-jackson) | — | JS | TradingView MCP fork |
| [bittensor-investing-agent](https://github.com/jackson-video-resources/bittensor-investing-agent) | 8 | Python | Bittensor subnet investing |
| [defi-yield-optimizer-agent](https://github.com/jackson-video-resources/defi-yield-optimizer-agent) | 2 | TS | Uniswap V3 LP optimizer |

---

## Key YouTube Videos

Ordered most recent first.

| Video | Date | What It Covers |
|---|---|---|
| [I Re-Built A Quant Trading Strategy With Fable 5](https://www.youtube.com/watch?v=Z-hU97WO30I) | Jun 2026 | Same Markov strategy rebuilt with Fable 5 — see [[MarkovHedgeFundMethod]] |
| [How To Make Money With Claude's New Fable 5](https://www.youtube.com/watch?v=KrMk4aeM54k) | Jun 2026 | 5 businesses Fable 5 unlocks: data room analyst, legacy code rebuilds, recurring research reports, tender/grant writing; Lewis runs $30k–$100k/month with 2 humans + 52 AI agents; free Skool prompt included |
| [Turning $50k - $500k In 1 Year with AI Trading (My Progress So Far)](https://www.youtube.com/watch?v=Eozt4PHbKt8) | Jun 2026 | Live challenge progress update; live trade dashboard publicly available |
| [I Built an AI Trading System With Claude + TradingView](https://www.youtube.com/watch?v=IqvnryFzZD4) | Jun 2026 | Full AI trading system using Claude + TradingView + IBKR API; prompts shared on blog |
| [So My AI Agent Does Insider Trading Now...](https://www.youtube.com/watch?v=flZA58F0BOQ) | May 2026 | 7-agent SEC filing monitor: **Eddie** (Form 4 CEO trades, daily), **Maggie** (13F institutional holdings — Berkshire/Bridgewater/Renaissance, weekly), **Frank** (Fed speech signals); data is public, zero illegal activity — edge comes from reading it before the market does |
| [I Re-Created A Quant Trading Strategy With Claude Code](https://www.youtube.com/watch?v=ZVMTeDBmSrI) | 2025 | Markov HMM regime strategy — original Claude Code build |
| [How To Build A Self-Improving AI Trading Agent](https://www.youtube.com/watch?v=6njREUQAFdg) | 2025 | Journal-based self-improvement loop |
| [How To Connect Claude to TradingView](https://www.youtube.com/watch?v=vIX6ztULs4U) | 2025 | TradingView MCP setup |
| [I Built a Zero-Human Trading Team with Claude](https://www.youtube.com/watch?v=cXhEw2jF4go) | 2025 | 6-agent trading firm |
| [How To Create A Personal Zero Human Trading Firm](https://www.youtube.com/watch?v=T6jdfZ317Vw) | 2025 | Firm setup walkthrough |

---

## ZeroOne Classroom Structure (From Public Search)

The classroom reportedly contains:
- Every prompt from Lewis's YouTube videos
- Updated versions with community bug fixes
- Each page: prompt + what it does + prerequisites + 3 common failure points
- Skills Library: daily-use skills for trading, research, content, deployment
- 60-Day "Your First Agent" Challenge (Premium/VIP)
- Community leaderboards and referral program

---

## How These Tools Connect to Your Strategy

```
YouTube Traders
    │
    ▼ [[YT-StrategyAgent]]
Strategy Rules (rules.json)
    │
    ├──► [[TradingView-MCP]] — reads charts, indicators, OHLCV
    │
    ├──► [[ClaudeTradingView-Bot]] — crypto execution via BitGet
    │
    ├──► [[Stocks-Futures-Agent]] — equity/futures execution via Alpaca
    │
    └──► [[ZeroHumanTradingFirm]] — full 6-agent autonomous firm
              │
              ├── Research Agent (nightly scans)
              ├── Backtest Agent (validates strategies)
              ├── Risk Agent (gatekeeper)
              └── Execution Agent (places trades)

[[AI-Quant-Workbench]] — validates signal quality statistically
[[ClaudeCodeSkills-Trading]] — installs reusable skills into Claude Code
[[HiddenMarkovTrading]] — regime filter sits on top of all of these
```

---

## Sources

- [ZeroOne Systems Skool Community](https://www.skool.com/zero-one)
- [Lewis Jackson YouTube Channel](https://www.youtube.com/@LewisWJackson)
- [Lewis Jackson GitHub Organisation](https://github.com/jackson-video-resources)
- [Roan (@RohOnChain) on X](https://x.com/RohOnChain) — original Markov framework author; publishes institutional quant research breakdowns on prediction markets, HMM hybrids, and arbitrage math