"""
Uncle Model — 5-Year Backtest Engine (V3.0)
============================================
Vectorized backtest with trailing stop-loss, position sizing,
cooldown period, and performance analytics (Sharpe, max drawdown).
Falls back to synthetic crisis data when yfinance is unavailable.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import yfinance as yf


# ---------------------------------------------------------------------------
# Synthetic data generator (fallback when yfinance fails)
# ---------------------------------------------------------------------------
def generate_synthetic_data(ticker: str = "SIM", years: int = 5) -> pd.DataFrame:
    print(f"[FALLBACK] Generating {years}Y synthetic data for {ticker}...")
    rng = np.random.default_rng(seed=42)
    days = years * 252
    dates = pd.bdate_range(end=pd.Timestamp.today(), periods=days)

    returns = rng.normal(0.0005, 0.02, days)

    # Inject 3 major crises
    crisis_pts = [int(days * f) for f in (0.2, 0.5, 0.8)]
    for cp in crisis_pts:
        returns[cp:cp + 15] = rng.normal(-0.04, 0.02, 15)
        returns[cp + 15:cp + 20] = rng.normal(-0.01, 0.04, 5)
        returns[cp + 20:cp + 40] = rng.normal(0.02, 0.02, 20)

    close = 10.0 * np.exp(np.cumsum(returns))
    opn = close * rng.normal(1.0, 0.005, days)
    high = np.maximum(opn, close) * rng.normal(1.01, 0.005, days)
    low = np.minimum(opn, close) * rng.normal(0.99, 0.005, days)

    # Force bearish-rejection candles at crisis bottoms
    for cp in crisis_pts:
        for d in (cp + 18, cp + 19):
            opn[d] = close[d - 1] * 0.98
            high[d] = opn[d] * 1.05
            close[d] = opn[d] * 0.95
            low[d] = close[d] * 0.98

    return pd.DataFrame({
        "Date": dates, "Open": opn, "High": high,
        "Low": low, "Close": close,
        "Volume": rng.integers(1_000_000, 50_000_000, size=days),
    })


# ---------------------------------------------------------------------------
# Data loader
# ---------------------------------------------------------------------------
def load_data(ticker: str, period: str = "5y") -> tuple[pd.DataFrame, str]:
    print(f"\nFetching {period} data for {ticker}...")
    try:
        df = yf.download(ticker, period=period, progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.reset_index().dropna(subset=["Close"])
            if "Datetime" in df.columns:
                df = df.rename(columns={"Datetime": "Date"})
            if len(df) >= 252:
                return df, ticker
    except Exception as e:
        print(f"  yfinance error: {e}")

    df = generate_synthetic_data(f"{ticker}_SIM")
    return df, f"{ticker}_SIM"


# ---------------------------------------------------------------------------
# Vectorized signal computation
# ---------------------------------------------------------------------------
def compute_signals(df: pd.DataFrame, tr_10y: float, total_premium: float) -> pd.DataFrame:
    df = df.copy()
    df["Rolling_Base"] = df["Low"].rolling(252, min_periods=252).min()
    df["Rolling_Peak"] = df["High"].rolling(252, min_periods=252).max()
    df["Bond_FV"] = df["Rolling_Base"] * (1 + tr_10y)
    df["Bank_Bottom"] = df["Bond_FV"] * (1 + total_premium)

    close = df["Close"].values
    prev_close = np.roll(close, 1)
    prev_close[0] = np.nan
    opn = df["Open"].values
    high = df["High"].values

    cond1 = (close < df["Bond_FV"].values) & (close < df["Bank_Bottom"].values)
    bearish = (high > opn) & (close < prev_close) & (close < opn)
    bearish_prev = np.roll(bearish, 1)
    bearish_prev[0] = False

    df["Uncle_Signal"] = cond1 & bearish & bearish_prev
    return df


# ---------------------------------------------------------------------------
# Backtest runner
# ---------------------------------------------------------------------------
def run_backtest(
    ticker: str = "THYAO.IS",
    initial_capital: float = 100_000,
    position_pct: float = 0.25,        # Risk at most 25% of capital per trade
    trailing_stop_pct: float = 0.12,   # 12% trailing stop-loss
    time_stop_days: int = 126,         # 6-month time stop
    cooldown_days: int = 10,           # Cooldown between consecutive entries
    min_profit_target: float = 0.25,   # Minimum 25% take-profit target
    tr_10y_yield: float = 0.38,
    us_10y_yield: float = 0.055,
    cds_risk_premium: float = 0.02,
    local_risk_margin: float = 0.10,
) -> pd.DataFrame:

    total_premium = us_10y_yield + cds_risk_premium + local_risk_margin
    df, resolved_ticker = load_data(ticker)
    df = compute_signals(df, tr_10y_yield, total_premium)

    # Pre-extract numpy arrays for speed
    dates = df["Date"].values
    close_arr = df["Close"].values
    high_arr = df["High"].values
    bond_fv_arr = df["Bond_FV"].values
    signal_arr = df["Uncle_Signal"].values
    rolling_base = df["Rolling_Base"].values
    n = len(df)

    capital = initial_capital
    position = 0.0
    entry_price = 0.0
    locked_target = 0.0
    trailing_high = 0.0
    days_in_trade = 0
    last_exit_idx = -cooldown_days  # Allow immediate first trade
    trades: list[dict] = []
    equity_curve = np.full(n, np.nan)

    for i in range(n):
        if np.isnan(rolling_base[i]):
            equity_curve[i] = capital
            continue

        price = close_arr[i]

        if position > 0:
            days_in_trade += 1
            trailing_high = max(trailing_high, high_arr[i])
            trailing_stop_price = trailing_high * (1 - trailing_stop_pct)

            sell_price = 0.0
            sell_reason = ""

            # EXIT 1: Locked target reached
            if high_arr[i] >= locked_target:
                sell_price = locked_target
                sell_reason = "Target Reached"

            # EXIT 2: Trailing stop-loss hit
            elif price <= trailing_stop_price and days_in_trade >= 5:
                sell_price = price
                sell_reason = "Trailing Stop"

            # EXIT 3: Time stop
            elif days_in_trade >= time_stop_days:
                sell_price = price
                sell_reason = f"Time Stop {time_stop_days}D"

            if sell_price > 0:
                revenue = position * sell_price
                profit = revenue - (position * entry_price)
                pct = (sell_price - entry_price) / entry_price * 100
                capital += revenue
                trades.append({
                    "Action": f"SELL ({sell_reason})",
                    "Date": pd.Timestamp(dates[i]).strftime("%Y-%m-%d"),
                    "Price": round(sell_price, 2),
                    "Capital": round(capital, 2),
                    "Profit": round(profit, 2),
                    "Profit %": round(pct, 2),
                })
                position = 0
                days_in_trade = 0
                last_exit_idx = i

        # BUY LOGIC
        if position == 0 and signal_arr[i] and (i - last_exit_idx) >= cooldown_days:
            invest = capital * position_pct
            if invest >= 100:
                entry_price = price
                position = invest / entry_price
                capital -= invest
                trailing_high = high_arr[i]
                locked_target = max(bond_fv_arr[i], entry_price * (1 + min_profit_target))

                trades.append({
                    "Action": "BUY",
                    "Date": pd.Timestamp(dates[i]).strftime("%Y-%m-%d"),
                    "Price": round(entry_price, 2),
                    "Capital": round(invest, 2),
                    "Profit": 0,
                    "Profit %": 0,
                })

        equity_curve[i] = capital + (position * price if position > 0 else 0)

    # Close any open position at end
    if position > 0:
        sell_price = close_arr[-1]
        revenue = position * sell_price
        profit = revenue - (position * entry_price)
        pct = (sell_price - entry_price) / entry_price * 100
        capital += revenue
        trades.append({
            "Action": "SELL (End of Backtest)",
            "Date": pd.Timestamp(dates[-1]).strftime("%Y-%m-%d"),
            "Price": round(sell_price, 2),
            "Capital": round(capital, 2),
            "Profit": round(profit, 2),
            "Profit %": round(pct, 2),
        })
        equity_curve[-1] = capital

    # ---------- Analytics ----------
    final_capital = capital
    total_return = (final_capital - initial_capital) / initial_capital * 100
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
    sell_trades = trades_df[trades_df["Action"].str.contains("SELL")] if not trades_df.empty else pd.DataFrame()
    num_trades = len(sell_trades)
    wins = len(sell_trades[sell_trades["Profit"] > 0]) if num_trades else 0
    win_rate = (wins / num_trades * 100) if num_trades else 0

    # Max drawdown from equity curve
    eq = pd.Series(equity_curve).ffill().bfill()
    running_max = eq.cummax()
    drawdown = (eq - running_max) / running_max * 100
    max_dd = drawdown.min()

    # Annualized Sharpe (daily equity returns, 252 trading days)
    eq_returns = eq.pct_change().dropna()
    sharpe = (eq_returns.mean() / eq_returns.std() * np.sqrt(252)) if eq_returns.std() > 0 else 0

    # ---------- Report ----------
    w = 90
    print(f"\n{'=' * w}")
    print(f" UNCLE MODEL V3.0 — 5-YEAR BACKTEST: {resolved_ticker}")
    print(f"{'=' * w}")
    print(f"  Initial Capital  : ${initial_capital:>12,.2f}")
    print(f"  Final Capital    : ${final_capital:>12,.2f}")
    print(f"  Net Profit       : ${(final_capital - initial_capital):>12,.2f}")
    print(f"  Total Return     : {total_return:>11.2f}%")
    print(f"  Win Rate         : {win_rate:>11.2f}%  ({wins}/{num_trades})")
    print(f"  Max Drawdown     : {max_dd:>11.2f}%")
    print(f"  Sharpe Ratio     : {sharpe:>11.2f}")
    print(f"{'=' * w}")

    if not trades_df.empty:
        print("\n  TRADE LOG:")
        print(trades_df.to_string(index=False))
    else:
        print("\n  No trades executed.")

    return trades_df


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    run_backtest("THYAO.IS", 100_000)
