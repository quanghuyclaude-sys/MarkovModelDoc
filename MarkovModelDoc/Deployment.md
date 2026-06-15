# Deployment — Infrastructure, Monitoring & Costs

> Back to: [[SelfImprovingTradingAgent]]
> Sources: [MindStudio: Build a 24/7 AI Trading Agent](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca) · [Tradewink: Build an AI Trading Agent with Alpaca API](https://www.tradewink.com/learn/build-ai-agent-alpaca-tutorial)

---

## Infrastructure Options

| Option | Cost | Best For |
|---|---|---|
| Claude Code Routines (built-in) | Free (just API cost) | Simplest — no external infra |
| Linux VPS (systemd / pm2) | $5–20/month | Full control, persistent process |
| AWS Lambda + EventBridge | $1–5/month | Serverless, auto-scaling |
| Docker on any cloud | $10–30/month | Portable, reproducible env |

The video uses **Claude Code Routines** — no external scheduler needed. The routine config file handles everything.

---

## Project Directory Structure

```
trading-agent/
├── CLAUDE.md                    ← Agent standing instructions
├── watchlist.json               ← Symbol universe + allocation limits
├── .claude/
│   └── routines.json            ← Schedule definitions
├── .env                         ← API keys (never commit this)
├── agent/
│   ├── research.py              ← Market data fetching
│   ├── decide.py                ← Claude signal generation
│   ├── execute.py               ← Order submission
│   ├── journal.py               ← Logging
│   └── guardrails.py            ← Risk validation
├── journals/
│   ├── 2026-06-12.jsonl         ← Machine-readable daily log
│   ├── 2026-06-12.md            ← Human-readable daily summary
│   └── weekly-2026-06-12.md     ← Weekly reflection reports
├── heartbeat.json               ← Written each cycle — used for monitoring
└── trading.db                   ← SQLite (alternative to JSONL)
```

---

## Environment Variables

Store in `.env` — never commit to version control:

```bash
# Alpaca
APCA_API_KEY_ID=your_key_here
APCA_API_SECRET_KEY=your_secret_here
APCA_BASE_URL=https://paper-api.alpaca.markets   # change for live

# News
POLYGON_API_KEY=your_polygon_key
NEWSAPI_KEY=your_newsapi_key

# Notifications
SENDGRID_API_KEY=your_sendgrid_key
ALERT_EMAIL=you@example.com

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key
```

Load in Python:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Heartbeat Monitoring

Every routine writes a heartbeat file on completion. An external monitor alerts if the heartbeat goes stale:

```python
import json
from datetime import datetime
from pathlib import Path

def write_heartbeat(status: str, trades_placed: int):
    Path("heartbeat.json").write_text(json.dumps({
        "timestamp":     datetime.utcnow().isoformat() + "Z",
        "status":        status,
        "trades_placed": trades_placed,
    }))

# Monitoring check (run separately or via cron):
def check_heartbeat(max_age_minutes: int = 35):
    hb = json.loads(Path("heartbeat.json").read_text())
    last = datetime.fromisoformat(hb["timestamp"].replace("Z", ""))
    age  = (datetime.utcnow() - last).seconds / 60
    if age > max_age_minutes:
        send_alert(f"Agent heartbeat stale — last seen {age:.0f} min ago")
```

---

## Daily Email Digest

Send a summary of each day's activity via SendGrid:

```python
import sendgrid
from sendgrid.helpers.mail import Mail

def send_daily_digest(journal_summary: str):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ["SENDGRID_API_KEY"])
    message = Mail(
        from_email="agent@yourdomain.com",
        to_emails=os.environ["ALERT_EMAIL"],
        subject=f"Trading Agent Daily Report — {date.today()}",
        plain_text_content=journal_summary
    )
    sg.send(message)
```

---

## Cost Breakdown

### Claude API Cost Per Day

| Model | Tokens per cycle | Cost per cycle | 26 cycles/day | Daily cost |
|---|---|---|---|---|
| claude-opus-4-8 | ~2,000 in / ~200 out | ~$0.04 | 26 | ~$1.04 |
| claude-sonnet-4-6 | ~2,000 in / ~200 out | ~$0.01 | 26 | ~$0.26 |
| claude-haiku-4-5 | ~2,000 in / ~200 out | ~$0.003 | 26 | ~$0.08 |

Recommendation: use Haiku for routine signal generation, Opus only for weekly reflection.

### Total Monthly Estimate

| Item | Monthly Cost |
|---|---|
| Claude API (Haiku cycles + Opus weekly) | ~$5–15 |
| Alpaca (commission-free broker) | $0 |
| Polygon.io news (starter tier) | $29 |
| VPS / cloud hosting | $5–20 |
| SendGrid (100 emails/day free tier) | $0 |
| **Total** | **~$39–64/month** |

---

## Token Cost Control Techniques

| Technique | Saving |
|---|---|
| Cap OHLCV bars at 60 (not 500) | ~70% context reduction |
| Truncate news summaries to 200 chars | ~60% news token reduction |
| Summarize journal before passing to reflection routine | Keeps history manageable |
| Use Haiku for signal generation, Opus for reflection only | ~70% cost reduction |
| Set explicit tool call budget per session | Prevents runaway loops |

From Chudi Nnorukam's production deployment: API costs dropped from $340 to $136/month after implementing tiered context loading.

---

## Going from Paper to Live Trading

Follow this progression — do not skip steps:

```
Step 1: Paper trading (paper=True in TradingClient)
    ↓   minimum 90 days, 100+ completed trades
Step 2: Live trading — tiny size (1 share per position)
    ↓   minimum 30 days, confirm all systems work identically
Step 3: Live trading — normal sizing per risk rules
    ↓   ongoing monitoring, weekly reflection
Step 4: Expand watchlist or adjust sizing based on performance
```

Switch from paper to live by changing one line:
```python
trade_client = TradingClient(api_key, secret_key, paper=False)  # live
```
And update `APCA_BASE_URL` to `https://api.alpaca.markets`.

---

## Production Stability (Chudi Nnorukam Results)

After optimizing the deployment architecture over 3 months (Dec 2025 – Mar 2026):

| Metric | Before | After |
|---|---|---|
| API cost | $340/month | $136/month |
| Uptime | ~90% | 99.2% |
| Error rate | 1 in 6 cycles | 1 in 40 cycles |

Key fixes: tiered context loading, two-gate verification before order submission, persistent state tracking via database instead of in-memory.

---

## Deployment Checklist

- [ ] `.env` created with all API keys, not committed to git
- [ ] `.gitignore` includes `.env`, `journals/`, `trading.db`
- [ ] Paper trading running for 90+ days before live
- [ ] Heartbeat monitoring configured with alert on stale
- [ ] Daily email digest working
- [ ] Daily loss limit tested intentionally (simulate a loss)
- [ ] Stop-loss auto-close tested intentionally
- [ ] Routine timezone confirmed as `America/New_York`
- [ ] Market holiday calendar awareness confirmed
- [ ] Claude API spend cap configured

---

## Sources

- [MindStudio: Build a 24/7 AI Trading Agent with Claude Code and Alpaca](https://www.mindstudio.ai/blog/build-ai-trading-agent-claude-code-alpaca)
- [MindStudio: Claude Code Routines](https://www.mindstudio.ai/blog/how-to-build-ai-trading-agent-claude-code-routines)
- [Tradewink: Build an AI Trading Agent with Alpaca API](https://www.tradewink.com/learn/build-ai-agent-alpaca-tutorial)
- [YouTube: How To Build A Self-Improving AI Trading Agent](https://www.youtube.com/watch?v=6njREUQAFdg)
