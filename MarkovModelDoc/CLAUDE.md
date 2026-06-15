# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Purpose

This repository is a **personal knowledge library** documenting the ZeroOne Systems / Lewis Jackson AI trading stack — centred on Hidden Markov Model (HMM) regime detection. It is an Obsidian vault: every file is Markdown, cross-linked with `[[WikiLink]]` syntax, and there is no build system, test suite, or deployable code here.

**When answering questions, use only documents in this library.** Do not generate signals, thresholds, parameters, or architectural claims from general training data — cite the specific `.md` file instead.

---

## Library Map

The documents form a layered system. Read them in this order to orient:

| Layer | Entry point | What it covers |
|---|---|---|
| Index | `ZeroOne-ResourceHub.md` | All repos, videos, and how the tools connect |
| Theory | `HMM-Theory.md` | HMM math: states, transition matrix, Viterbi, Baum-Welch, Chapman-Kolmogorov |
| Core strategy | `MarkovHedgeFundMethod.md` | The specific pipeline Lewis built: regime classification → transition matrix → directional signal |
| HMM in code | `HMM-Implementation-Python.md` | Full `hmmlearn`-based implementation |
| Regime logic | `MarketRegimes.md` | Bull / Bear / Sideways classification rules |
| Signal layer | `SignalGeneration.md` | SMA crossover (primary) + HMM score (regime gate) + combined logic |
| LLM signal | `SignalGeneration-LLM.md` | Claude as the signal generator: system prompt, JSON output schema, confidence levels |
| Risk / guardrails | `Guardrails-RiskManagement.md` | Multi-layer safety: CLAUDE.md rules → code validation → daily loss halt |
| Regime risk | `RegimeFilter-RiskManagement.md` | HMM-gated order filter, position sizing by regime confidence |
| Execution | `TradeExecution.md` | Position sizing formula, limit-order submission, Alpaca API |
| Research module | `MarketResearchModule.md` | Data fetching, indicator computation, market snapshot builder |
| Strategies | `VWAP-RSI-EMA-Strategy.md` | VWAP + RSI(3) + EMA(8) scalper (BTCUSDT, 1m) — live example |
| Agent pipeline | `AgentArchitecture.md` | 4-stage cycle: research → signal → execute → journal |
| Multi-agent firm | `ZeroHumanTradingFirm.md` | 6-agent autonomous firm (CEO, Research, Backtest, Risk, Execution, Cost) |
| Self-improvement | `SelfImprovementLoop.md` | Journal-based feedback loop |
| Backtesting | `Backtesting.md` | Walk-forward validation approach |
| Statistical toolkit | `AI-Quant-Workbench.md` | 5-module research workbench (probability, stats, portfolio math, AI loop, demo) |
| Scheduling | `ClaudeCodeRoutines.md` | Cron-based routine definitions |
| TradingView | `TradingView-MCP.md` · `TradingViewPineScript.md` | Chart data MCP + Pine Script indicator |
| Crypto bot | `ClaudeTradingView-Bot.md` | Claude + TradingView → BitGet pipeline |
| Stocks/futures | `Stocks-Futures-Agent.md` | Alpaca-based equity/futures agent |
| Skills index | `ClaudeCodeSkills-Trading.md` | Reusable Claude Code skill installs — install commands and invocations |
| Skills (detailed) | `resources/` folder | Full skill docs downloaded from GitHub — one file per skill |
| YouTube miner | `YT-StrategyAgent.md` | Extracts strategy rules from YouTube videos |
| Macro features | `MacroFeatures.md` | Macro data inputs |
| Quant paper | `QuantAgent-Paper.md` | Academic references |
| NN+HMM paper | `NNHMMPaper.md` | Full breakdown of the 83% return paper (HMM + PyTorch + Black-Litterman, COVID 2019–2022) |
| Neural network signals | `NNTradingSignals.md` | LSTM implementation, stationary features, walk-forward training, Kelly sizing (Roan @RohOnChain) |
| Quant career roadmap | `QuantRoadmap.md` | 4 quant roles, 5-layer math foundation, interview process, staircase to $650k/yr (Roan) |
| Prediction markets quant | `PredictionMarketsQuant.md` | Polymarket microstructure, Avellaneda-Stoikov, VPIN, empirical Kelly, 5-phase roadmap (Roan) |
| Polymarket math Part 2 | `PolymarketMathPart2.md` | Frank-Wolfe implementation: InitFW, Barrier FW, profit guarantee, why mispricing exists (Roan) |
| Delta-neutral strategies | `DeltaNeutral.md` | Basis arbitrage, hedged LP + gamma hedging, yield tokenization (Pendle PT/YT), Sortino sizing |
| Deployment | `Deployment.md` | Cloud hosting, monitoring, cost notes |
| Trade journal | `TradeJournal.md` | JSONL logging schema |

---

## Key Parameters (from the documents)

These are the canonical values used across the library — do not invent alternatives:

| Parameter | Value | Source |
|---|---|---|
| Regime classification window | 20 days | `MarkovHedgeFundMethod.md` |
| Bull/Bear threshold | ±5% rolling return | `MarkovHedgeFundMethod.md` |
| SMA crossover | 10-day vs 30-day | `SignalGeneration.md` |
| Conviction threshold (Bull regime) | > 0.53 | `SignalGeneration.md` |
| Conviction threshold (Sideways) | > 0.60 | `RegimeFilter-RiskManagement.md` |
| Conviction threshold (Bear) | > 0.70 | `RegimeFilter-RiskManagement.md` |
| Max position size | 5% of portfolio | `Guardrails-RiskManagement.md` |
| Min cash reserve | 20% of portfolio | `Guardrails-RiskManagement.md` |
| Max concurrent positions | 5 | `Guardrails-RiskManagement.md` |
| Daily loss halt | 3% of starting equity | `Guardrails-RiskManagement.md` |
| Hard stop per trade | 8% from entry | `Guardrails-RiskManagement.md` |
| Risk per trade | 2% of portfolio | `TradeExecution.md` |
| VWAP distance filter | ≤ 1.5% from VWAP | `VWAP-RSI-EMA-Strategy.md` |
| Hard stop (BTCUSDT scalper) | 0.3% from entry | `VWAP-RSI-EMA-Strategy.md` |

---

## Cross-Link Convention

Documents use `[[FileName]]` (Obsidian wiki-link, no `.md` extension). When referencing documents in answers, use the actual filename with `.md`.

---

## resources/ Folder

Downloaded directly from GitHub on 2026-06-15. Contains the actual `SKILL.md` content for each skill:

| File | Skill | Source |
|---|---|---|
| `Skills-Backtest.md` | `backtest` | jackson-video-resources/skills |
| `Skills-RiskManager.md` | `risk-manager` | jackson-video-resources/skills |
| `Skills-TradeJournal.md` | `trade-journal` | jackson-video-resources/skills |
| `Skills-StrategyAudit.md` | `strategy-audit` | jackson-video-resources/skills |
| `Skills-CapitalAllocator.md` | `capital-allocator` | jackson-video-resources/skills |
| `Skills-PineScript.md` | `pine-script` | jackson-video-resources/skills |
| `Skills-Autoresearch.md` | `autoresearch` | jackson-video-resources/skills |
| `Skills-Engineering.md` | `code-simplifier`, `commit-push-pr`, `security-audit`, `seo-optimizer` | jackson-video-resources/skills |
| `Skills-MarkovRegime.md` | `markov-hedge-fund-method` (regime plugin) | jackson-video-resources/markov-hedge-fund-method |

Note: The ZeroOne Skool community classroom contains additional per-skill documentation not available publicly.

---

## What This Library Does NOT Contain

- Live broker credentials or API keys
- Runnable code (all code blocks are illustrative, sourced from GitHub repos)
- A build system, package manager, or test suite
- Any file outside this Obsidian vault (`.obsidian/` folder is editor config only)
