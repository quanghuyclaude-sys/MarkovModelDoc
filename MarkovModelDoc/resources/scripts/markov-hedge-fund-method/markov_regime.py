# Source: github.com/jackson-video-resources/markov-hedge-fund-method
# Framework by Roan (@RohOnChain), refactored by Lewis Jackson
# MIT License
#
# Markov Regime Detection — importable module + CLI
#
# Five core operations:
#   1. label_regimes()           — Bull/Bear/Sideways from rolling returns
#   2. build_transition_matrix() — 3x3 MLE transition matrix
#   3. nstep_forecast()          — Chapman-Kolmogorov n-step probabilities
#   4. stationary_distribution() — long-run regime mix via eigenvector
#   5. walk_forward_backtest()   — no-lookahead backtest, retrains incrementally
#
# Optional: fit_hmm() — Gaussian HMM via Baum-Welch (requires hmmlearn)
#
# CLI usage:
#   python markov_regime.py --ticker SPY
#   python markov_regime.py --ticker BTC-USD --window 20 --threshold 0.05
#   python markov_regime.py --csv my_prices.csv --json
#
# Output modes:
#   terminal (default) — pretty-printed summary with matrices and metrics
#   --json             — structured dict for downstream agent consumption
#
# Disclaimer: backtests are historical only, not forward-looking.

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "yfinance>=0.2",
#   "pandas>=2.0",
#   "numpy>=1.26",
#   "scipy>=1.12",
#   "hmmlearn>=0.3; extra == 'hmm'",
# ]
# ///

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


# ─── Data Loading ──────────────────────────────────────────────────────────

def load_ticker(ticker: str, start: str = "2015-01-01") -> pd.Series:
    """Fetch daily closes from yfinance. No API key required."""
    try:
        import yfinance as yf
    except ImportError:
        sys.exit("yfinance not installed. Run: pip install yfinance")
    df = yf.download(ticker, start=start, auto_adjust=True, progress=False)
    if df.empty:
        sys.exit(f"No data returned for ticker '{ticker}'.")
    close = df["Close"].squeeze()
    close.name = ticker
    return close


def load_csv(path: str) -> pd.Series:
    """
    Load a CSV with date + close columns.
    Flexible column naming: accepts 'date'/'Date'/'DATE', 'close'/'Close'/'price'/'adj_close'.
    """
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower().str.strip()
    date_col  = next((c for c in df.columns if "date" in c), None)
    close_col = next((c for c in df.columns if c in {"close", "price", "adj_close", "adjusted"}), None)
    if not date_col or not close_col:
        sys.exit(f"Could not find date/close columns in {path}. Found: {list(df.columns)}")
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    return df[close_col].astype(float)


# ─── Regime Labeling ───────────────────────────────────────────────────────

STATES = ["Bull", "Bear", "Sideways"]


def label_regimes(
    prices: pd.Series,
    window: int = 20,
    threshold: float = 0.05,
) -> pd.Series:
    """
    Classify each bar as Bull / Bear / Sideways using a rolling return window.

    Bull     → rolling_return > +threshold
    Bear     → rolling_return < -threshold
    Sideways → between -threshold and +threshold

    Args:
        prices:    Daily closing prices.
        window:    Rolling window in bars (default 20).
        threshold: Return boundary, e.g. 0.05 = ±5% (default 0.05).

    Returns:
        pd.Series of strings: "Bull", "Bear", or "Sideways".
    """
    rolling_ret = prices.pct_change(window)
    regimes = pd.Series(index=prices.index, dtype=str)
    regimes[rolling_ret > threshold]  = "Bull"
    regimes[rolling_ret < -threshold] = "Bear"
    mask = (rolling_ret >= -threshold) & (rolling_ret <= threshold)
    regimes[mask] = "Sideways"
    return regimes.dropna()


# ─── Transition Matrix ─────────────────────────────────────────────────────

def build_transition_matrix(regimes: pd.Series) -> pd.DataFrame:
    """
    Estimate the 3x3 transition matrix via maximum likelihood.

    Entry A[i, j] = P(next state = j | current state = i).
    Rows sum to 1. Zero-count rows are filled with uniform distribution.

    Returns:
        pd.DataFrame with index and columns = STATES.
    """
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    prev = None
    for state in regimes:
        if prev is not None:
            counts[prev][state] += 1
        prev = state

    A = pd.DataFrame(index=STATES, columns=STATES, dtype=float)
    for s in STATES:
        total = sum(counts[s].values())
        for t in STATES:
            A.loc[s, t] = counts[s][t] / total if total > 0 else 1.0 / 3
    return A


# ─── N-Step Forecast ───────────────────────────────────────────────────────

def nstep_forecast(
    A: pd.DataFrame,
    current_state: str,
    steps: int = 5,
) -> dict[str, float]:
    """
    Forecast regime probabilities n steps ahead via Chapman-Kolmogorov.

    A^n = A multiplied by itself n times.
    Starting from current_state with probability 1.0.

    Returns:
        Dict mapping state name → probability.
    """
    state_vec = np.array([1.0 if s == current_state else 0.0 for s in STATES])
    A_mat = A.values
    for _ in range(steps):
        state_vec = state_vec @ A_mat
    return dict(zip(STATES, state_vec))


# ─── Stationary Distribution ───────────────────────────────────────────────

def stationary_distribution(A: pd.DataFrame) -> dict[str, float]:
    """
    Compute the long-run stationary distribution via eigenvector decomposition.

    Solves π @ A = π, sum(π) = 1.
    The stationary vector is the left eigenvector corresponding to eigenvalue 1.

    Returns:
        Dict mapping state name → long-run probability.
    """
    from numpy.linalg import eig
    vals, vecs = eig(A.values.T)
    # Find eigenvector for eigenvalue closest to 1
    idx = np.argmin(np.abs(vals - 1.0))
    stat = np.real(vecs[:, idx])
    stat = np.abs(stat) / np.abs(stat).sum()
    return dict(zip(STATES, stat))


# ─── Directional Signal ────────────────────────────────────────────────────

def directional_signal(forecast: dict[str, float]) -> float:
    """
    Compute signed directional signal from n-step forecast.

    signal = P(Bull) - P(Bear)
    Range: [-1.0, +1.0]
      +1.0 → strong bull conviction
      -1.0 → strong bear conviction
       0.0 → uncertain / sideways
    """
    return forecast.get("Bull", 0.0) - forecast.get("Bear", 0.0)


# ─── Walk-Forward Backtest ─────────────────────────────────────────────────

def walk_forward_backtest(
    prices: pd.Series,
    window: int = 20,
    threshold: float = 0.05,
    min_train: int = 252,
    forecast_steps: int = 5,
    conviction_threshold: float = 0.53,
) -> dict:
    """
    No-lookahead walk-forward backtest.

    Retrains the transition matrix incrementally using only historical data.
    Enters long when directional_signal > conviction_threshold.
    Exits when signal drops to or below 0.

    Args:
        prices:               Daily close prices.
        window:               Regime classification window (default 20).
        threshold:            Bull/Bear boundary (default ±5%).
        min_train:            Minimum bars before first backtest signal (default 252).
        forecast_steps:       N-step Chapman-Kolmogorov horizon (default 5).
        conviction_threshold: Minimum bull signal to enter (default 0.53).

    Returns:
        Dict with keys: returns, sharpe, max_drawdown, n_trades, signals.
    """
    regimes = label_regimes(prices, window, threshold)
    returns  = prices.pct_change().dropna()

    strategy_returns = []
    invested = False
    n_trades = 0
    signals = {}

    dates = regimes.index[min_train:]
    for date in dates:
        hist_regimes = regimes.loc[:date].iloc[:-1]
        if len(hist_regimes) < window + 2:
            continue

        A = build_transition_matrix(hist_regimes)
        current = regimes.loc[date]
        forecast = nstep_forecast(A, current, forecast_steps)
        signal = directional_signal(forecast)
        signals[date] = signal

        if signal > conviction_threshold and not invested:
            invested = True
            n_trades += 1
        elif signal <= 0 and invested:
            invested = False

        day_ret = returns.get(date, 0.0)
        strategy_returns.append(day_ret if invested else 0.0)

    if not strategy_returns:
        return {"error": "Insufficient data for backtest."}

    rets = pd.Series(strategy_returns)
    cumulative = (1 + rets).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_dd = float(drawdown.min())

    sharpe = float(rets.mean() / rets.std() * np.sqrt(252)) if rets.std() > 0 else 0.0

    return {
        "sharpe":       round(sharpe, 3),
        "max_drawdown": round(max_dd, 4),
        "n_trades":     n_trades,
        "total_return": round(float(cumulative.iloc[-1] - 1), 4),
        "signals":      signals,
    }


# ─── Optional HMM ──────────────────────────────────────────────────────────

def fit_hmm(
    prices: pd.Series,
    n_components: int = 3,
    n_iter: int = 200,
    n_restarts: int = 5,
) -> Optional[object]:
    """
    Fit a Gaussian Hidden Markov Model using Baum-Welch (EM).

    HMM states are labelled by ascending mean return (lowest = Bear, highest = Bull).
    Local optima are common — tests multiple random seeds and picks best log-likelihood.

    Returns:
        Fitted GaussianHMM object, or None if hmmlearn is not installed.
    """
    try:
        from hmmlearn.hmm import GaussianHMM
    except ImportError:
        return None

    rets = prices.pct_change().dropna().values.reshape(-1, 1)
    best_model = None
    best_score = -np.inf

    for seed in range(n_restarts):
        model = GaussianHMM(
            n_components=n_components,
            covariance_type="full",
            n_iter=n_iter,
            random_state=seed,
        )
        try:
            model.fit(rets)
            score = model.score(rets)
            if score > best_score:
                best_score = score
                best_model = model
        except Exception:
            continue

    return best_model


# ─── CLI ───────────────────────────────────────────────────────────────────

def _fmt_matrix(A: pd.DataFrame) -> str:
    lines = ["         " + "  ".join(f"{s:>8}" for s in STATES)]
    for s in STATES:
        row = "  ".join(f"{A.loc[s, t]:>8.3f}" for t in STATES)
        lines.append(f"  {s:<6}  {row}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Markov Regime Detection")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--ticker", type=str, help="yfinance ticker, e.g. SPY or BTC-USD")
    src.add_argument("--csv",    type=str, help="CSV file with date + close columns")
    parser.add_argument("--window",    type=int,   default=20,   help="Rolling window (default 20)")
    parser.add_argument("--threshold", type=float, default=0.05, help="Return threshold (default 0.05 = ±5%%)")
    parser.add_argument("--steps",     type=int,   default=5,    help="Forecast horizon in steps (default 5)")
    parser.add_argument("--hmm",       action="store_true",       help="Also fit a Gaussian HMM (requires hmmlearn)")
    parser.add_argument("--json",      action="store_true",       help="Output JSON instead of terminal display")
    args = parser.parse_args()

    prices = load_ticker(args.ticker) if args.ticker else load_csv(args.csv)
    name   = args.ticker or Path(args.csv).stem

    regimes = label_regimes(prices, args.window, args.threshold)
    A       = build_transition_matrix(regimes)
    current = str(regimes.iloc[-1])
    forecast = nstep_forecast(A, current, args.steps)
    stat    = stationary_distribution(A)
    signal  = directional_signal(forecast)
    bt      = walk_forward_backtest(prices, args.window, args.threshold)

    # Regime counts
    counts_pct = regimes.value_counts(normalize=True).to_dict()

    result = {
        "asset":          name,
        "current_regime": current,
        "directional_signal": round(signal, 4),
        "forecast":       {k: round(v, 4) for k, v in forecast.items()},
        "stationary_distribution": {k: round(v, 4) for k, v in stat.items()},
        "historical_regime_pct": {k: round(v, 4) for k, v in counts_pct.items()},
        "transition_matrix": A.round(4).to_dict(),
        "backtest": {k: v for k, v in bt.items() if k != "signals"},
    }

    if args.hmm:
        hmm = fit_hmm(prices)
        result["hmm_available"] = hmm is not None
        if hmm is not None:
            result["hmm_means"]      = hmm.means_.flatten().round(6).tolist()
            result["hmm_covars"]     = [c.flatten()[0] for c in hmm.covars_]
            result["hmm_transmat"]   = hmm.transmat_.round(4).tolist()

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return

    # Terminal display
    print(f"\n{'─'*60}")
    print(f"  Markov Regime Report — {name}")
    print(f"{'─'*60}")
    print(f"  Current regime:       {current}")
    print(f"  Directional signal:   {signal:+.4f}  (Bull - Bear probability)")
    print(f"\n  {args.steps}-step forecast:")
    for s, p in forecast.items():
        bar = "█" * int(p * 30)
        print(f"    {s:<10} {p:.3f}  {bar}")
    print(f"\n  Stationary distribution (long-run):")
    for s, p in stat.items():
        bar = "█" * int(p * 30)
        print(f"    {s:<10} {p:.3f}  {bar}")
    print(f"\n  Transition matrix:")
    print(_fmt_matrix(A))
    print(f"\n  Walk-forward backtest:")
    print(f"    Sharpe ratio:   {bt.get('sharpe', 'n/a')}")
    print(f"    Max drawdown:   {bt.get('max_drawdown', 'n/a'):.2%}")
    print(f"    Total return:   {bt.get('total_return', 'n/a'):.2%}")
    print(f"    Trades:         {bt.get('n_trades', 'n/a')}")
    if result.get("hmm_available"):
        print(f"\n  HMM state means: {result['hmm_means']}")
    print(f"{'─'*60}\n")
    print("  Disclaimer: historical backtest only — not forward-looking.\n")


if __name__ == "__main__":
    main()
