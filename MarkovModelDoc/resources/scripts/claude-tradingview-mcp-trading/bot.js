// Source: github.com/jackson-video-resources/claude-tradingview-mcp-trading
// Claude + TradingView MCP → BitGet automated crypto trading bot
//
// Fetches 500 candles from Binance public API (no key required).
// Calculates EMA(8), VWAP (resets midnight UTC), RSI(3).
// Evaluates VWAP + RSI(3) + EMA(8) entry conditions from rules.json.
// Executes via BitGet API (HMAC-SHA256 auth).
//
// Modes:
//   Paper Trading  — PAPER_TRADING=true (default, no real orders)
//   Live Trading   — PAPER_TRADING=false
//   Cloud Mode     — Railway deployment, candle data from Binance
//   Local Mode     — node bot.js
//
// Risk controls:
//   MAX_TRADE_SIZE_USD  — max position size per trade (env var)
//   MAX_TRADES_PER_DAY  — daily trade cap (env var)
//   1% portfolio risk per trade
//
// Logs:
//   trades.csv            — tax-ready transaction log
//   safety-check-log.json — decision audit trail
//
// Usage:
//   node bot.js              — run one cycle
//   node bot.js --tax-summary — print full activity report

"use strict";

const fs      = require("fs");
const path    = require("path");
const https   = require("https");
const crypto  = require("crypto");
require("dotenv").config();

// ─── Config ──────────────────────────────────────────────────────────────────
const PAPER_TRADING      = process.env.PAPER_TRADING !== "false";
const PORTFOLIO_VALUE    = parseFloat(process.env.PORTFOLIO_VALUE_USD  || "1000");
const MAX_TRADE_SIZE     = parseFloat(process.env.MAX_TRADE_SIZE_USD   || "100");
const MAX_TRADES_PER_DAY = parseInt(process.env.MAX_TRADES_PER_DAY     || "3", 10);
const RISK_PCT           = 0.01;   // 1% portfolio risk per trade
const SYMBOL             = "BTCUSDT";
const CANDLE_LIMIT       = 500;

const RULES_FILE         = path.join(__dirname, "rules.json");
const TRADES_FILE        = path.join(__dirname, "trades.csv");
const SAFETY_LOG_FILE    = path.join(__dirname, "safety-check-log.json");

// ─── Utilities ────────────────────────────────────────────────────────────────
function httpsGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(new Error(`JSON parse error: ${e.message}`)); }
      });
    }).on("error", reject);
  });
}

function sign(secret, message) {
  return crypto.createHmac("sha256", secret).update(message).digest("hex");
}

function nowMs() { return Date.now(); }

function countTodayTrades() {
  if (!fs.existsSync(TRADES_FILE)) return 0;
  const today = new Date().toISOString().slice(0, 10);
  const lines = fs.readFileSync(TRADES_FILE, "utf8").split("\n");
  return lines.filter((l) => l.startsWith(today) && l.includes("Live")).length;
}

// ─── Indicators ───────────────────────────────────────────────────────────────
function ema(values, period) {
  const k = 2 / (period + 1);
  let e = values[0];
  for (let i = 1; i < values.length; i++) {
    e = values[i] * k + e * (1 - k);
  }
  return e;
}

function vwap(candles) {
  // Session VWAP — resets at midnight UTC
  const midnightUTC = new Date();
  midnightUTC.setUTCHours(0, 0, 0, 0);
  const session = candles.filter((c) => c.openTime >= midnightUTC.getTime());
  if (!session.length) return null;
  let sumPV = 0, sumV = 0;
  for (const c of session) {
    const typical = (c.high + c.low + c.close) / 3;
    sumPV += typical * c.volume;
    sumV  += c.volume;
  }
  return sumV > 0 ? sumPV / sumV : null;
}

function rsi(closes, period) {
  if (closes.length < period + 1) return null;
  const slice = closes.slice(-(period + 1));
  let gains = 0, losses = 0;
  for (let i = 1; i < slice.length; i++) {
    const diff = slice[i] - slice[i - 1];
    if (diff > 0) gains  += diff;
    else          losses -= diff;
  }
  const avgGain = gains  / period;
  const avgLoss = losses / period;
  if (avgLoss === 0) return 100;
  const rs = avgGain / avgLoss;
  return 100 - 100 / (1 + rs);
}

// ─── Market Data ──────────────────────────────────────────────────────────────
async function fetchCandles(symbol, interval = "1m", limit = CANDLE_LIMIT) {
  const url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`;
  const raw = await httpsGet(url);
  return raw.map((k) => ({
    openTime: k[0],
    open:     parseFloat(k[1]),
    high:     parseFloat(k[2]),
    low:      parseFloat(k[3]),
    close:    parseFloat(k[4]),
    volume:   parseFloat(k[5]),
  }));
}

// ─── Strategy Evaluation ──────────────────────────────────────────────────────
function evaluateStrategy(candles, rules) {
  const closes  = candles.map((c) => c.close);
  const current = closes[closes.length - 1];

  const ema8    = ema(closes, 8);
  const vwapVal = vwap(candles);
  const rsi3    = rsi(closes, 3);

  const indicators = { price: current, ema8, vwap: vwapVal, rsi3 };

  if (!vwapVal || rsi3 === null) {
    return { signal: "NO_TRADE", reason: "Insufficient data", indicators };
  }

  // Distance filter — no trade if price > 1.5% from VWAP
  const vwapDist = Math.abs(current - vwapVal) / vwapVal;
  if (vwapDist > 0.015) {
    return { signal: "NO_TRADE", reason: `Price ${(vwapDist * 100).toFixed(2)}% from VWAP — exceeds 1.5% filter`, indicators };
  }

  // Long entry — all 3 required
  const longConditions = {
    price_above_vwap: current > vwapVal,
    price_above_ema:  current > ema8,
    rsi_below_30:     rsi3 < (rules.long_conditions?.rsi_below ?? 30),
  };

  if (Object.values(longConditions).every(Boolean)) {
    return { signal: "BUY", reason: "All long conditions met", indicators, conditions: longConditions };
  }

  // Short entry — all 3 required
  const shortConditions = {
    price_below_vwap: current < vwapVal,
    price_below_ema:  current < ema8,
    rsi_above_70:     rsi3 > (rules.short_conditions?.rsi_above ?? 70),
  };

  if (Object.values(shortConditions).every(Boolean)) {
    return { signal: "SELL", reason: "All short conditions met", indicators, conditions: shortConditions };
  }

  return { signal: "NO_TRADE", reason: "Conditions not aligned", indicators };
}

// ─── Position Sizing ──────────────────────────────────────────────────────────
function computePositionSize(price, stopPct) {
  const riskAmount = PORTFOLIO_VALUE * RISK_PCT;
  const riskPerUnit = price * stopPct;
  const riskBased   = riskAmount / riskPerUnit;
  const allocBased  = MAX_TRADE_SIZE / price;
  return Math.min(riskBased, allocBased);
}

// ─── BitGet Execution ─────────────────────────────────────────────────────────
async function placeBitGetOrder(side, qty, price) {
  if (PAPER_TRADING) {
    console.log(`[PAPER] ${side} ${qty.toFixed(6)} ${SYMBOL} @ ${price}`);
    return { orderId: `paper-${nowMs()}`, status: "paper" };
  }

  const apiKey    = process.env.BITGET_API_KEY;
  const secretKey = process.env.BITGET_SECRET_KEY;
  const passphrase = process.env.BITGET_PASSPHRASE;

  if (!apiKey || !secretKey || !passphrase) {
    throw new Error("BitGet credentials missing from .env");
  }

  const ts      = String(nowMs());
  const body    = JSON.stringify({ symbol: SYMBOL, side: side.toLowerCase(), orderType: "limit", price: String(price), size: String(qty), force: "gtc" });
  const message = ts + "POST" + "/api/v2/spot/trade/place-order" + body;
  const sig     = sign(secretKey, message);

  return new Promise((resolve, reject) => {
    const data = Buffer.from(body);
    const req  = https.request({
      hostname: "api.bitget.com",
      path:     "/api/v2/spot/trade/place-order",
      method:   "POST",
      headers:  {
        "Content-Type":      "application/json",
        "ACCESS-KEY":        apiKey,
        "ACCESS-SIGN":       sig,
        "ACCESS-TIMESTAMP":  ts,
        "ACCESS-PASSPHRASE": passphrase,
        "Content-Length":    data.length,
      },
    }, (res) => {
      let resp = "";
      res.on("data", (c) => (resp += c));
      res.on("end", () => {
        try { resolve(JSON.parse(resp)); }
        catch (e) { reject(e); }
      });
    });
    req.on("error", reject);
    req.write(data);
    req.end();
  });
}

// ─── Logging ──────────────────────────────────────────────────────────────────
function logTrade(evaluation, qty, price, orderId) {
  const now   = new Date().toISOString();
  const mode  = PAPER_TRADING ? "Paper" : "Live";
  const total = qty * price;
  const fee   = total * 0.001;
  const line  = `${now.slice(0,10)},${now.slice(11,19)},BitGet,${SYMBOL},${evaluation.signal},${qty.toFixed(6)},${price},${total.toFixed(2)},${fee.toFixed(4)},${(total - fee).toFixed(2)},${orderId},${mode}\n`;

  if (!fs.existsSync(TRADES_FILE)) {
    fs.writeFileSync(TRADES_FILE, "Date,Time,Exchange,Symbol,Side,Quantity,Price,Total_USD,Estimated_Fee,Net_Amount,Order_ID,Mode\n");
  }
  fs.appendFileSync(TRADES_FILE, line);
}

function logSafetyCheck(evaluation, allowed, reason) {
  const entry = {
    timestamp:  new Date().toISOString(),
    signal:     evaluation.signal,
    indicators: evaluation.indicators,
    allowed,
    reason,
    conditions: evaluation.conditions || {},
  };
  let log = [];
  if (fs.existsSync(SAFETY_LOG_FILE)) {
    try { log = JSON.parse(fs.readFileSync(SAFETY_LOG_FILE, "utf8")); } catch (_) {}
  }
  log.push(entry);
  fs.writeFileSync(SAFETY_LOG_FILE, JSON.stringify(log.slice(-500), null, 2));
}

// ─── Main Cycle ───────────────────────────────────────────────────────────────
async function runCycle() {
  console.log(`\n[${new Date().toISOString()}] Cycle starting — ${PAPER_TRADING ? "PAPER" : "LIVE"} mode`);

  // Load strategy rules
  if (!fs.existsSync(RULES_FILE)) {
    console.error("rules.json not found. Run onboarding prompt first.");
    return;
  }
  const rules = JSON.parse(fs.readFileSync(RULES_FILE, "utf8"));

  // Fetch candles
  const candles = await fetchCandles(SYMBOL);
  const price   = candles[candles.length - 1].close;
  console.log(`  Price: ${price.toFixed(2)}  |  Candles: ${candles.length}`);

  // Evaluate strategy
  const evaluation = evaluateStrategy(candles, rules);
  console.log(`  Signal: ${evaluation.signal} — ${evaluation.reason}`);

  // Safety checks
  if (evaluation.signal === "NO_TRADE") {
    logSafetyCheck(evaluation, false, evaluation.reason);
    return;
  }

  const todayTrades = countTodayTrades();
  if (!PAPER_TRADING && todayTrades >= MAX_TRADES_PER_DAY) {
    logSafetyCheck(evaluation, false, `Daily trade cap reached (${todayTrades}/${MAX_TRADES_PER_DAY})`);
    console.log(`  Blocked: daily cap reached.`);
    return;
  }

  // Size and execute
  const stopPct = rules.risk?.stop_pct ?? 0.003;
  const qty     = computePositionSize(price, stopPct);

  console.log(`  Placing ${evaluation.signal}: ${qty.toFixed(6)} ${SYMBOL} @ ${price}`);
  const result = await placeBitGetOrder(evaluation.signal, qty, price);

  logTrade(evaluation, qty, price, result.orderId || result.data?.orderId || "unknown");
  logSafetyCheck(evaluation, true, "All checks passed");
  console.log(`  Order submitted: ${JSON.stringify(result)}`);
}

// ─── Tax Summary ──────────────────────────────────────────────────────────────
function printTaxSummary() {
  if (!fs.existsSync(TRADES_FILE)) { console.log("No trades logged yet."); return; }
  const lines = fs.readFileSync(TRADES_FILE, "utf8").split("\n").filter((l) => l && !l.startsWith("Date"));
  console.log(`\nTrade Summary — ${lines.length} records\n`);
  let total = 0;
  for (const l of lines) {
    const cols = l.split(",");
    console.log(`  ${cols[0]} ${cols[1]}  ${cols[4]} ${cols[2]} ${cols[5]} @ ${cols[6]}  Net: $${cols[9]}  [${cols[11]}]`);
    total += parseFloat(cols[9] || "0");
  }
  console.log(`\nTotal net: $${total.toFixed(2)}\n`);
}

// ─── Entry Point ──────────────────────────────────────────────────────────────
if (require.main === module) {
  if (process.argv.includes("--tax-summary")) {
    printTaxSummary();
  } else {
    runCycle().catch((err) => { console.error("Cycle error:", err.message); process.exit(1); });
  }
}

module.exports = { runCycle, evaluateStrategy, fetchCandles };
