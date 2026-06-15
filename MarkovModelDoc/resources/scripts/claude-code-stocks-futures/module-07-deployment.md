# Module 07 — Automation & Resilience

> Source: github.com/jackson-video-resources/claude-code-stocks-futures/prompts/module-07-deployment.md
> Part of: [[Stocks-Futures-Agent]]

---

## Section 7.2 — PM2 Setup

```bash
npm install -g pm2

# Start
pm2 start trading-system.py --name trading-system --interpreter python3

# Persist across reboots
pm2 save
pm2 startup

# Monitor
pm2 status
pm2 logs trading-system
pm2 stop trading-system
pm2 restart trading-system
```

---

## Section 7.3 — Telegram Alerts

**Setup:**
1. Message `@BotFather` on Telegram → `/newbot`
2. Get chat ID: message your bot, then visit `https://api.telegram.org/bot<token>/getUpdates`
3. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

**Prompt:**
```
"Add Telegram alerts using the Bot API directly (no external libraries) that notify on:
- Trade openings (instrument, direction, size, entry price)
- Trade closings (P&L)
- Stop loss triggers
- Unhandled errors
Optional: daily 4pm ET market-close summary via cron — trade count, total P&L, status."
```

---

## Section 7.4 — Error Handling & Reconnection

```
"Add resilience:
1. WebSocket reconnection — retry every 30 seconds, log each attempt
2. Order failures — single retry after 5 seconds, alert and skip on second failure
3. Main loop protection — catch all exceptions, log stack trace, send alert, resume after 60s
4. Comprehensive logging — signals, orders, errors, reconnections → trading-system.log with UTC timestamps"
```
