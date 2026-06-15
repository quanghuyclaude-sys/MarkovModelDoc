# TradingView MCP — Connect Claude to TradingView

> Back to: [[ZeroOne-ResourceHub]]
> Repo: [LewisWJackson/tradingview-mcp-jackson](https://github.com/LewisWJackson/tradingview-mcp-jackson)
> Video: [How To Connect Claude to TradingView (Insanely Cool)](https://www.youtube.com/watch?v=vIX6ztULs4U)

---

## What It Is

A local MCP (Model Context Protocol) server that connects Claude Code to your running
TradingView Desktop app via Chrome DevTools Protocol (CDP). Claude can read your charts
and control TradingView — all processing stays on your machine. Nothing leaves locally.

Architecture:
```
Claude Code
    │ MCP stdio
    ▼
MCP Server (Node.js, localhost)
    │ Chrome DevTools Protocol
    ▼
TradingView Desktop (localhost:9222)
```

---

## What Claude Can Read

| Data | Details |
|---|---|
| Symbol + timeframe | Current chart settings |
| OHLCV bars | Price history for any visible period |
| Current quote | Real-time bid/ask/last |
| Indicator values | RSI, MACD, Bollinger Bands, EMAs — any loaded indicator |
| Custom Pine Script output | Lines, labels, tables, boxes, support/resistance levels |
| Watchlist | All symbols in your current watchlist |
| Replay P&L | Position and profit/loss in replay mode |

---

## What Claude Can Control

| Action | Details |
|---|---|
| Change symbol / timeframe | Switch charts programmatically |
| Add / remove indicators | Load or unload any TradingView indicator |
| Adjust indicator parameters | Change RSI period, EMA length, etc. |
| Inject Pine Script | Write, compile, and deploy custom scripts |
| Draw on chart | Trend lines, horizontal levels, rectangles, labels |
| Create / delete price alerts | Set alerts at any price level |
| Configure layout | Multi-pane setups, chart grids |
| Navigate replay | Step through bars historically |
| Take screenshots | Capture chart state |

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/LewisWJackson/tradingview-mcp-jackson.git ~/tradingview-mcp-jackson
cd ~/tradingview-mcp-jackson
npm install

# 2. Copy and configure rules
cp rules.example.json rules.json
# Edit rules.json with your trading strategy conditions
```

Launch TradingView with debug port enabled (use the provided launch scripts in the repo),
then register the MCP server in Claude Code:

```json
// ~/.claude/.mcp.json
{
  "mcpServers": {
    "tradingview": {
      "command": "node",
      "args": ["/Users/YOUR_USERNAME/tradingview-mcp-jackson/src/server.js"]
    }
  }
}
```

Verify connection with the `tv_health_check` tool inside Claude Code.

---

## Morning Brief Workflow

The standout feature of this fork. Each morning, Claude:

1. Scans every symbol in your watchlist
2. Reads all loaded indicator values per symbol
3. Applies conditions from `rules.json` (your strategy rules)
4. Outputs a structured session bias: bullish / bearish / neutral per symbol
5. Highlights key levels to watch
6. Saves the brief to file for pattern comparison across days

This replaces manual chart review. Your strategy rules run automatically against live data.

---

## rules.json — Strategy Definition

The rules file tells Claude what conditions define a trade setup. It is the same
file used by [[ClaudeTradingView-Bot]] for automated execution.

See [[VWAP-RSI-EMA-Strategy]] for the full example strategy that ships with the repo.

Custom strategy workflow:
1. Use Apify YouTube Transcript Scraper on any trading YouTuber
2. Feed transcript to `prompts/01-extract-strategy.md`
3. Claude generates a custom `rules.json`
4. Drop it in — morning brief now uses your strategy

See [[YT-StrategyAgent]] for the automated version of this process.

---

## Requirements

- TradingView Desktop with **paid subscription** (for real-time data)
- Node.js 18+
- Claude Code
- macOS, Windows, or Linux

The tool reads from your locally running TradingView — it does not bypass
paywalls and does not scrape TradingView's servers.

---

## Integration With Your Strategy Stack

```
TradingView MCP
    │
    ├──► Morning brief → feeds [[SignalGeneration-LLM]]
    │
    ├──► Live indicator values → feeds [[ClaudeTradingView-Bot]]
    │
    ├──► Pine Script injection → deploys [[TradingViewPineScript]] (HMM ribbons)
    │
    └──► Historical OHLCV → feeds [[AI-Quant-Workbench]] for research
```

---

## Sources

- [GitHub: tradingview-mcp-jackson](https://github.com/LewisWJackson/tradingview-mcp-jackson)
- [YouTube: How To Connect Claude to TradingView](https://www.youtube.com/watch?v=vIX6ztULs4U)
- [ZeroOne Systems](https://www.skool.com/zero-one)
