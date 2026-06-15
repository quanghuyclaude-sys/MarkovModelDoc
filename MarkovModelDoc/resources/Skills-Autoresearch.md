# Skill: autoresearch

> Repo: [jackson-video-resources/skills](https://github.com/jackson-video-resources/skills)
> Back to: [[ClaudeCodeSkills-Trading]]

---

## Install

```bash
npx skills add jackson-video-resources/skills -s autoresearch -g -y
```

## Invoke

```
"use autoresearch to find the latest papers on momentum factor decay"
"use autoresearch to find 3 momentum strategies"
"load autoresearch and scan for BTC scalping strategies published in 2025"
```

---

## What It Does

Runs automated research across multiple sources for any goal or domain. Designed to produce tight, fast loops that run unsupervised — keeping winning results and discarding losers.

### What It Delivers (for any stated goal)

1. **Goal Definition** — precise, measurable success metrics
2. **Experiment Loop Design** — the full plan → action → measure → repeat cycle
3. **Technical Stack** — exact tools, compute, orchestration layer
4. **Quick-Start Commands** — runnable in under 10 minutes
5. **Business Model** — which monetisation pattern fits (SaaS, agency, retainer, etc.)
6. **First Experiment Tonight** — one minimal proof-of-concept you can run immediately
7. **Risks & Human Checkpoints** — where human review is required before execution

### Example Domains

- Finding profitable trading strategies via backtesting
- Generating and scoring research hypotheses
- Optimising content through A/B testing
- Automating lead qualification workflows

---

## Role in the Trading Stack

Powers the **Research Agent** nightly scan in [[ZeroHumanTradingFirm]]:
- Scans YouTube, arXiv, TradingView ideas, Reddit overnight
- Delivers weekly strategy briefs
- Feeds intelligence into Backtest and Risk agents

Can be chained with other skills:

```
"Use autoresearch to find 3 momentum strategies,
 then use backtest on each,
 then use strategy-audit on the best performer,
 then use capital-allocator for a $5k portfolio"
```

---

## Related Files

- [[ZeroHumanTradingFirm]] — the Research Agent uses this skill
- [[YT-StrategyAgent]] — dedicated YouTube transcript → strategy pipeline
- [[ClaudeCodeSkills-Trading]] — full skill list
