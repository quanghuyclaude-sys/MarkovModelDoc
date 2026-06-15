# YouTube Strategy Agent — Mine Any Trader Into a Rules File

> Back to: [[ZeroOne-ResourceHub]]
> Repo: [jackson-video-resources/yt-strategy-agent](https://github.com/jackson-video-resources/yt-strategy-agent)

---

## What It Does

A 24/7 automated agent that watches YouTube trading channels and converts their
content into living strategy documents — updated every 10 minutes as new videos drop.

For each tracked channel it generates and continuously updates:

| File | Content |
|---|---|
| `strategy.md` | Deduced trading approach in plain English |
| `rules.json` | Structured buy/sell rules with risk and timing |
| `changelog.md` | Append-only record of strategy shifts over time |
| `trades.md` | Highlighted trade calls from the host |
| `videos/*.md` | Per-video notes + full transcripts |

The `rules.json` output can be dropped directly into [[ClaudeTradingView-Bot]] or
[[TradingView-MCP]] for automated execution.

---

## How the 10-Minute Cycle Works

```
Every 10 minutes:

1. Fetch latest 5 video IDs from each tracked channel (YouTube Data API)
2. Check which videos are new (not yet in SQLite)
3. Pull transcripts for new videos via Apify
4. Extract strategy elements using Claude (structured JSON output)
5. Apply recency weighting to all rules
6. Cluster similar rules using embedding similarity
7. Detect strategy shifts vs. existing strategy.md
8. Update all output files
9. Send email alerts if: new video dropped / strategy shifted / trade call found
```

---

## Recency Weighting System

Rules are weighted by how recently they appeared across videos:

| Video Position | Weight |
|---|---|
| Most recent | 1.00 |
| 2nd most recent | 0.70 |
| 3rd most recent | 0.50 |
| 4th most recent | 0.35 |
| 5th most recent | 0.25 |

Rules scoring below **0.30 confidence** are automatically removed from strategy.md.
This ensures the strategy reflects the trader's current thinking, not old views.

---

## Strategy Shift Detection

The agent flags a strategy shift when any of these trigger:

- New rules directly contradict existing high-confidence rules
- Overall strategy summary moves >0.35 in semantic distance (embedding comparison)
- Claude marks `strategy_shift.changed = true` in its extraction JSON

When a shift is detected, an email alert fires and `changelog.md` is updated.

---

## Manual Extraction Workflow (Single Channel)

To extract a strategy from one channel without the full agent:

1. Run [Apify YouTube Transcript Scraper](https://apify.com) on target channel
2. Feed transcript output to `prompts/01-extract-strategy.md` in Claude Code:
   ```
   Here is a transcript from [Trader Name]:
   [paste transcript]

   Extract their trading strategy and output as:
   1. strategy.md — plain English description
   2. rules.json — structured entry/exit conditions
   ```
3. Drop the resulting rules.json into [[ClaudeTradingView-Bot]] or [[TradingView-MCP]]

Cost: approximately £6–7/month total (VPS + Anthropic API + Apify + free YouTube API).

---

## Setup

Installation is AI-guided — paste `PROMPT.md` into Claude Code agent mode.
The agent sets up the full stack in ~20 minutes.

Currently supports macOS only for the full agent.
Manual extraction workflow works on any OS.

---

## Technical Stack

| Component | Technology |
|---|---|
| Language | Python |
| Storage | SQLite |
| Scheduling | systemd service |
| Transcripts | Apify |
| Embeddings | Claude / OpenAI |
| Alerts | Gmail SMTP |
| Deployment | VPS (Hostinger) |

---

## Strategy Sources Beyond YouTube

The same extraction pattern works on other text sources:

| Source | Method |
|---|---|
| YouTube channels | Apify Transcript Scraper + this agent |
| TradingView published ideas | Scrape via TradingView MCP or Apify |
| arXiv quant papers | WebFetch + Claude extraction |
| Reddit (r/algotrading) | Apify Reddit Scraper |
| SEC EDGAR hedge fund filings | Reverse-engineer pitch decks |
| GitHub algo repos | Read code + Claude extraction |

The [[ZeroHumanTradingFirm]] Research Agent does this nightly across all sources.

---

## Output Integration

```
YT-StrategyAgent output files
        │
        ├── rules.json ──► [[ClaudeTradingView-Bot]] (crypto auto-execution)
        │
        ├── rules.json ──► [[TradingView-MCP]] (morning brief)
        │
        ├── strategy.md ──► [[SignalGeneration-LLM]] system prompt context
        │
        └── changelog.md ──► [[SelfImprovementLoop]] (track strategy drift)
```

---

## Sources

- [GitHub: yt-strategy-agent](https://github.com/jackson-video-resources/yt-strategy-agent)
- [ZeroOne Systems](https://www.skool.com/zero-one)
- [Lewis Jackson YouTube Channel](https://www.youtube.com/@LewisWJackson)
