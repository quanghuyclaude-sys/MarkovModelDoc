# Module 01 — Setup & Foundation

> Source: github.com/jackson-video-resources/claude-code-stocks-futures/prompts/module-01-setup.md
> Part of: [[Stocks-Futures-Agent]]

---

## Section 1.3 — Project Structure Orientation

After creating `~/trading-system/` and `CLAUDE.md`, run:

```
"What is this project and what are the file structure conventions?"
```

## Section 1.4 — Alpaca API Integration

Once `.env` contains Alpaca credentials:

```
"Write a Python script called alpaca-test.py that reads ALPACA_API_KEY,
ALPACA_SECRET_KEY, and ALPACA_BASE_URL from the .env file using python-dotenv,
connects to the Alpaca paper trading API, and prints the account balance."
```

**Expected outcome:** `python3 alpaca-test.py` prints your paper account balance.

**Troubleshooting:**
- Spacing errors in the `.env` file
- Incorrect `BASE_URL` format (must include `paper-` prefix for paper trading)
- Missing `alpaca-py` package

**Module 1 complete** when account balance prints successfully.
