"""
Macro Floor Model — Macro Floor & Forced Liquidation System
Professional Autonomous Fund Management Platform v4.0
"""

from __future__ import annotations

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pymongo
from datetime import datetime, timedelta
import json
import requests

st.set_page_config(
    page_title="Macro Floor Model | Autonomous Fund Platform",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════
# PREMIUM CSS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

  :root {
    --bg-primary: #111113;
    --bg-card: #1a1a1f;
    --bg-card-hover: #22222a;
    --bg-elevated: #252530;
    --border: #2a2a35;
    --border-light: #35354a;
    --text-primary: #ececf1;
    --text-secondary: #8e8ea0;
    --text-muted: #5a5a72;
    --accent-blue: #4f8ff7;
    --accent-green: #2dd4a8;
    --accent-red: #f87171;
    --accent-amber: #f59e0b;
    --accent-purple: #a78bfa;
  }

  html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
  }
  .stApp { background-color: var(--bg-primary); }

  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141418 0%, #111113 100%);
    border-right: 1px solid var(--border);
    padding-top: 0 !important;
  }
  section[data-testid="stSidebar"] .stRadio > label { display: none; }
  section[data-testid="stSidebar"] .stRadio > div {
    flex-direction: column;
    gap: 2px;
  }
  section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    padding: 10px 16px !important;
    border-radius: 6px !important;
    margin: 0 !important;
    transition: all 0.15s;
  }
  section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p:hover {
    color: var(--text-primary) !important;
    background: var(--bg-card) !important;
  }
  section[data-testid="stSidebar"] * { color: var(--text-secondary) !important; }
  section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3 {
    color: var(--text-muted) !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    margin-top: 24px !important;
    margin-bottom: 4px !important;
    padding: 0 16px !important;
  }

  /* ── Brand Header ── */
  .brand-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 20px 0 16px 0;
    margin-bottom: 8px;
  }
  .brand-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 1rem; color: #fff;
  }
  .brand-name {
    font-size: 1rem; font-weight: 700; color: var(--text-primary);
    letter-spacing: -0.01em;
  }
  .brand-tag {
    font-size: 0.65rem; color: var(--text-muted);
    margin-top: 1px;
  }

  /* ── Page Title ── */
  .page-header {
    margin-top: -30px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
  }
  .page-title {
    font-size: 1.4rem; font-weight: 700; color: var(--text-primary);
    letter-spacing: -0.02em;
  }
  .page-desc {
    font-size: 0.82rem; color: var(--text-secondary); margin-top: 4px;
  }

  /* ── KPI cards ── */
  .kpi-row {
    display: grid;
    gap: 12px;
    margin-bottom: 24px;
  }
  .kpi-row-5 { grid-template-columns: repeat(5, 1fr); }
  .kpi-row-4 { grid-template-columns: repeat(4, 1fr); }
  .kpi-row-3 { grid-template-columns: repeat(3, 1fr); }
  .kpi {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    transition: border-color 0.2s;
  }
  .kpi:hover { border-color: var(--border-light); }
  .kpi-label {
    font-size: 0.68rem; font-weight: 600;
    color: var(--text-muted); text-transform: uppercase;
    letter-spacing: 0.06em; margin-bottom: 10px;
  }
  .kpi-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem; font-weight: 600;
    color: var(--text-primary); line-height: 1;
  }
  .kpi-val.sm { font-size: 1.15rem; }
  .kpi-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; margin-top: 8px;
  }
  .kpi-sub.green { color: var(--accent-green); }
  .kpi-sub.red { color: var(--accent-red); }
  .kpi-sub.muted { color: var(--text-muted); }
  .kpi-sub.blue { color: var(--accent-blue); }

  /* ── Section Header ── */
  .sec {
    font-size: 0.72rem; font-weight: 700;
    color: var(--text-muted); letter-spacing: 0.1em;
    text-transform: uppercase;
    padding-bottom: 8px; border-bottom: 1px solid var(--border);
    margin: 28px 0 16px 0;
  }

  /* ── Card containers ── */
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
  }
  .card-title {
    font-size: 0.9rem; font-weight: 600;
    color: var(--text-primary); margin-bottom: 14px;
  }

  /* ── Tables ── */
  .ptable {
    width: 100%; border-collapse: collapse; font-size: 0.8rem;
  }
  .ptable th {
    font-size: 0.62rem; font-weight: 700;
    color: var(--text-muted); letter-spacing: 0.08em;
    text-transform: uppercase; padding: 10px 12px;
    text-align: left; border-bottom: 1px solid var(--border);
  }
  .ptable td {
    padding: 12px 12px; border-bottom: 1px solid #1e1e28;
    font-family: 'JetBrains Mono', monospace; color: var(--text-secondary);
  }
  .ptable tr:hover td { background: var(--bg-card-hover); color: var(--text-primary); }
  .ptable .tk { color: var(--text-primary); font-weight: 600; }
  .c-green { color: var(--accent-green) !important; }
  .c-red { color: var(--accent-red) !important; }
  .c-blue { color: var(--accent-blue) !important; }
  .c-amber { color: var(--accent-amber) !important; }
  .c-muted { color: var(--text-muted) !important; }

  /* ── Signal badge ── */
  .badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.04em;
  }
  .badge-green { background: #0d3d30; color: var(--accent-green); }
  .badge-amber { background: #3d2e0d; color: var(--accent-amber); }
  .badge-red { background: #3d0d0d; color: var(--accent-red); }
  .badge-muted { background: #1e1e28; color: var(--text-muted); }

  /* ── Progress bar ── */
  .pbar-wrap {
    width: 100%; height: 6px; background: #1e1e28; border-radius: 3px;
    overflow: hidden; margin-top: 6px;
  }
  .pbar-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }

  /* ── Buttons ── */
  .stButton > button {
    background: var(--bg-card) !important; color: var(--text-primary) !important;
    border: 1px solid var(--border) !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.82rem !important;
    font-weight: 500 !important; padding: 10px 24px !important;
    transition: all 0.15s !important;
  }
  .stButton > button:hover {
    background: var(--bg-elevated) !important; border-color: var(--border-light) !important;
  }
  .stButton > button[kind="primary"] {
    background: var(--accent-blue) !important; border-color: var(--accent-blue) !important;
    color: #fff !important;
  }
  .stButton > button[kind="primary"]:hover { opacity: 0.9; }

  /* ── Inputs ── */
  .stSlider [data-baseweb="slider"] { background: var(--border); }
  .stTextArea textarea, .stTextInput input {
    background: var(--bg-card) !important; border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important; border-radius: 8px !important;
  }

  /* ── Doc blocks ── */
  .doc-section {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 10px; padding: 28px; margin-bottom: 16px;
    color: var(--text-secondary); line-height: 1.7; font-size: 0.88rem;
  }
  .doc-section h3 {
    color: var(--text-primary); font-size: 1.05rem; font-weight: 600;
    margin-bottom: 12px; margin-top: 0;
  }
  .doc-section h3 .num {
    color: var(--accent-blue); font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem; margin-right: 8px;
  }
  .doc-section code {
    background: var(--bg-elevated); padding: 2px 8px; border-radius: 4px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;
    color: var(--accent-blue);
  }
  .doc-section ul { padding-left: 20px; }
  .doc-section li { margin-bottom: 6px; }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] { gap: 0; background: transparent; border-bottom: 1px solid var(--border); }
  .stTabs [data-baseweb="tab"] {
    background: transparent; color: var(--text-muted);
    font-weight: 500; font-size: 0.82rem; padding: 12px 20px;
    border-bottom: 2px solid transparent;
  }
  .stTabs [aria-selected="true"] {
    color: var(--text-primary) !important;
    border-bottom: 2px solid var(--accent-blue) !important;
  }

  /* ── Chart container ── */
  .stAreaChart, .stBarChart, .stLineChart {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 12px !important;
  }

  /* ── Misc ── */
  hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# WATCHLIST
# ═══════════════════════════════════════════════════════════════════════════
DEFAULT_TICKERS = [
    "AAPL", "TSLA", "NVDA", "AMZN", "MSFT", "META", "GOOG", "AMD",
    "NFLX", "INTC", "JPM", "BAC",
    "THYAO.IS", "AKBNK.IS", "ISCTR.IS", "TUPRS.IS", "GARAN.IS",
    "SISE.IS", "KCHOL.IS", "SAHOL.IS",
]


# ═══════════════════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_resource
def _mongo():
    try: uri = st.secrets["MONGO_URI"]
    except: uri = "mongodb://localhost:27017/"
    return pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)

def _col(): return _mongo()["macro_floor_db"]["portfolio"]

def load_pf() -> dict:
    try:
        doc = _col().find_one({"_id": "main_fund"})
        if doc: return doc
    except: pass
    if "pf" not in st.session_state:
        st.session_state.pf = _run_full_backtest()
    return st.session_state.pf

def save_pf(pf: dict):
    try: _col().update_one({"_id": "main_fund"}, {"$set": pf}, upsert=True)
    except: st.session_state.pf = pf


# ═══════════════════════════════════════════════════════════════════════════
# MACRO ENGINE
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=1800)
def fetch_macros() -> dict:
    us10 = 0.0525
    tr10 = 0.33
    try:
        d = yf.download("^TNX", period="5d", progress=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        if not d.empty: us10 = float(d["Close"].dropna().iloc[-1]) / 100.0
    except: pass

    try:
        url = 'https://scanner.tradingview.com/global/scan'
        payload = {'symbols': {'tickers': ['TVC:TR10Y']}, 'columns': ['close']}
        r = requests.post(url, json=payload, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('data'):
                tr10 = float(data['data'][0]['d'][0]) / 100.0
    except: pass

    return {"us_10y": us10, "tr_10y": tr10, "cds": 0.025, "local_risk": 0.10}


# ═══════════════════════════════════════════════════════════════════════════
# SIGNAL ENGINE V4 — Enhanced with Signal Proximity Scoring
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=900, show_spinner=False)
def deep_analyze(ticker: str, tr_10y: float, total_prem: float) -> dict | None:
    """
    Enhanced V4 analysis: computes bond floor, bank bottom,
    signal proximity score (0-100), volatility, and trend.
    """
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index().dropna(subset=["Close"])
        if len(df) < 20: return None

        close = df["Close"].values.astype(float)
        opn = df["Open"].values.astype(float)
        high = df["High"].values.astype(float)
        low = df["Low"].values.astype(float)
        vol = df["Volume"].values.astype(float) if "Volume" in df.columns else np.ones(len(close))

        cur = float(close[-1])
        yr_high = float(np.max(high))
        yr_low = float(np.min(low))
        rolling_base = yr_low

        bond_fv = rolling_base * (1 + tr_10y)
        bank_bot = bond_fv * (1 + total_prem)
        target = max(bond_fv, cur * 1.25)

        # Signal proximity score (0 = far above, 100 = deep below bank bottom)
        if cur >= bond_fv:
            proximity = max(0, 100 - ((cur - bank_bot) / bank_bot * 100))
            proximity = max(0, min(proximity, 50))
        elif cur >= bank_bot:
            proximity = 50 + ((bond_fv - cur) / (bond_fv - bank_bot) * 30)
        else:
            proximity = 80 + min(20, ((bank_bot - cur) / bank_bot * 100))
        proximity = round(min(100, max(0, proximity)), 1)

        # Bearish exhaustion pattern
        prev_close = np.roll(close, 1); prev_close[0] = np.nan
        cond_below = (close < bond_fv) & (close < bank_bot)
        bearish = (high > opn) & (close < prev_close) & (close < opn)
        b_prev = np.roll(bearish, 1); b_prev[0] = False
        signal = bool(cond_below[-1] & bearish[-1] & b_prev[-1])

        # Volatility (20-day)
        returns = np.diff(close) / close[:-1]
        vol_20d = float(np.std(returns[-20:]) * np.sqrt(252) * 100) if len(returns) >= 20 else 0

        # Trend (50-day SMA direction)
        sma50 = float(np.mean(close[-50:])) if len(close) >= 50 else cur
        trend = "Uptrend" if cur > sma50 else "Downtrend"

        # Distance metrics
        dist_bond = round((cur - bond_fv) / bond_fv * 100, 2)
        dist_bank = round((cur - bank_bot) / bank_bot * 100, 2)
        from_high = round((cur - yr_high) / yr_high * 100, 1)

        # Average volume
        avg_vol = float(np.mean(vol[-20:])) if len(vol) >= 20 else 0

        return {
            "price": cur, "bond_fv": bond_fv, "bank_bot": bank_bot,
            "target": target, "signal": signal, "proximity": proximity,
            "dist_bond": dist_bond, "dist_bank": dist_bank,
            "from_high": from_high, "yr_high": yr_high, "yr_low": yr_low,
            "vol_20d": round(vol_20d, 1), "trend": trend,
            "avg_vol": avg_vol,
        }
    except: return None


# ═══════════════════════════════════════════════════════════════════════════
# 5-YEAR BACKTEST ENGINE
# ═══════════════════════════════════════════════════════════════════════════
def _run_full_backtest() -> dict:
    tr_10y = 0.33
    total_prem = 0.0525 + 0.025 + 0.10

    dfs = {}
    for t in DEFAULT_TICKERS:
        try:
            df = yf.download(t, period="5y", progress=False)
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.dropna(subset=['Close'])
            if len(df) < 252: continue

            df['Rolling_Base'] = df['Low'].rolling(252, min_periods=252).min()
            df['Bond_FV'] = df['Rolling_Base'] * (1 + tr_10y)
            df['Bank_Bot'] = df['Bond_FV'] * (1 + total_prem)

            close = df['Close'].values.astype(float)
            opn = df['Open'].values.astype(float)
            high = df['High'].values.astype(float)

            prev_close = np.roll(close, 1); prev_close[0] = np.nan
            cond1 = (close < df['Bond_FV'].values) & (close < df['Bank_Bot'].values)
            bearish = (high > opn) & (close < prev_close) & (close < opn)
            b_prev = np.roll(bearish, 1); b_prev[0] = False

            df['Signal'] = cond1 & bearish & b_prev
            dfs[t] = df
        except: pass

    all_dates = sorted(set(d for df in dfs.values() for d in df.index.tolist()))
    cash, holdings, history = 100_000.0, {}, []
    equity_curve = {}
    pos_pct, trail, time_days = 0.25, 0.12, 90
    peak_equity = 100_000.0
    max_dd = 0.0

    for d in all_dates:
        h_val = sum(
            h['qty'] * float(dfs[t].loc[d, 'Close']) if d in dfs[t].index else h['qty'] * h['cost']
            for t, h in holdings.items()
        )
        equity = cash + h_val
        peak_equity = max(peak_equity, equity)
        dd = (peak_equity - equity) / peak_equity * 100
        max_dd = max(max_dd, dd)
        equity_curve[d.strftime('%Y-%m-%d')] = round(equity, 2)

        sold = set()
        for t, h in list(holdings.items()):
            if d not in dfs[t].index: continue
            row = dfs[t].loc[d]
            price, hi = float(row['Close']), float(row['High'])
            buy_d = pd.to_datetime(h['buy_date'])

            if (d - buy_d).days >= time_days:
                prof = h['qty'] * price - h['qty'] * h['cost']
                cash += h['qty'] * price
                history.append(f"{d.strftime('%Y-%m-%d')} | TIME | {t:<12} | Exit: ${price:.2f} | P&L: ${prof:>+,.0f}")
                del holdings[t]; sold.add(t)
            elif hi >= h['target']:
                prof = h['qty'] * h['target'] - h['qty'] * h['cost']
                cash += h['qty'] * h['target']
                history.append(f"{d.strftime('%Y-%m-%d')} | SELL | {t:<12} | Exit: ${h['target']:.2f} | P&L: ${prof:>+,.0f}")
                del holdings[t]; sold.add(t)
            elif price <= h['trailing_high'] * (1 - trail):
                prof = h['qty'] * price - h['qty'] * h['cost']
                cash += h['qty'] * price
                history.append(f"{d.strftime('%Y-%m-%d')} | STOP | {t:<12} | Exit: ${price:.2f} | P&L: ${prof:>+,.0f}")
                del holdings[t]; sold.add(t)
            else:
                holdings[t]['trailing_high'] = max(h['trailing_high'], hi)

        for t, df in dfs.items():
            if t in holdings or t in sold or d not in df.index: continue
            row = df.loc[d]
            if bool(row['Signal']):
                invest = equity * pos_pct
                if cash >= invest >= 100:
                    price = float(row['Close'])
                    if pd.isna(row['Bond_FV']) or pd.isna(price): continue
                    tgt = max(float(row['Bond_FV']), price * 1.25)
                    qty = invest / price
                    cash -= invest
                    holdings[t] = {'qty': qty, 'cost': price, 'target': tgt,
                                   'trailing_high': price, 'buy_date': d.strftime('%Y-%m-%d %H:%M')}
                    history.append(f"{d.strftime('%Y-%m-%d')} | BUY  | {t:<12} | Entry: ${price:.2f}")

    return {
        "_id": "main_fund", "cash": round(cash, 2), "holdings": holdings,
        "history": history, "equity_curve": equity_curve,
        "max_dd": round(max_dd, 2),
        "inception": all_dates[0].strftime('%Y-%m-%d') if all_dates else "2021-10-01"
    }


# ═══════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════════════════════
pf = load_pf()
macros = fetch_macros()
tp = macros["us_10y"] + macros["cds"] + macros["local_risk"]

hv = sum(h["qty"] * (deep_analyze(t, macros["tr_10y"], tp) or {}).get("price", h["cost"])
         for t, h in pf.get("holdings", {}).items())
total_eq = pf.get("cash", 100_000) + hv
total_pnl = total_eq - 100_000
pnl_pct = total_pnl / 100_000 * 100
inception = pf.get("inception", "2021-10-01")

hist = pf.get("history", [])
exits = [h for h in hist if "| SELL |" in h or "| STOP |" in h or "| TIME |" in h]
n_trades = len(exits)
n_wins = len([h for h in exits if "P&L: $+" in h])
wr = f"{n_wins/n_trades*100:.0f}%" if n_trades else "—"

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="brand-bar">
      <div class="brand-icon">U</div>
      <div>
        <div class="brand-name">Macro Floor Model</div>
        <div class="brand-tag">Autonomous Fund Platform</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Navigation")
    page = st.radio("nav", [
        "◆  Overview",
        "◈  Signal Radar",
        "◇  Portfolio & Trades",
        "▣  Performance",
        "▢  How It Works",
    ], label_visibility="collapsed")

    st.markdown("### Parameters")
    pos_pct = st.slider("Position Size", 5, 50, 25, format="%d%%") / 100
    trail_stop = st.slider("Trailing Stop", 5, 25, 12, format="%d%%") / 100
    time_stop = st.slider("Time Stop", 30, 365, 90, format="%d days")

    st.markdown("### Universe")
    custom = st.text_area("", ", ".join(DEFAULT_TICKERS), height=120, label_visibility="collapsed")
    tickers = [t.strip().upper() for t in custom.split(",") if t.strip()]

    st.markdown("---")
    st.markdown(f"<div style='font-size:0.7rem;color:#5a5a72;padding:0 16px'>Inception: {inception}<br>Engine: V4.0<br>Universe: {len(tickers)} instruments</div>", unsafe_allow_html=True)

    if st.button("Reset & Rebuild"):
        with st.spinner("Downloading 5 years of data..."):
            save_pf(_run_full_backtest())
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════
if "Overview" in page:
    st.markdown(f"""
    <div class="page-header">
      <div class="page-title">Dashboard Overview</div>
      <div class="page-desc">Real-time portfolio summary and macro environment.</div>
    </div>
    """, unsafe_allow_html=True)

    dc = "green" if total_pnl >= 0 else "red"
    da = "+" if total_pnl >= 0 else ""

    st.markdown(f"""
    <div class="kpi-row kpi-row-5">
      <div class="kpi"><div class="kpi-label">Total AUM</div><div class="kpi-val">${total_eq:,.0f}</div><div class="kpi-sub {dc}">{da}${total_pnl:,.0f} ({da}{pnl_pct:.1f}%)</div></div>
      <div class="kpi"><div class="kpi-label">Cash Available</div><div class="kpi-val">${pf.get('cash',100000):,.0f}</div><div class="kpi-sub muted">{pf.get('cash',100000)/total_eq*100:.1f}% of AUM</div></div>
      <div class="kpi"><div class="kpi-label">Open Positions</div><div class="kpi-val">{len(pf.get('holdings',{}))}</div><div class="kpi-sub muted">${hv:,.0f} deployed</div></div>
      <div class="kpi"><div class="kpi-label">Win Rate</div><div class="kpi-val">{wr}</div><div class="kpi-sub muted">{n_wins}/{n_trades} profitable</div></div>
      <div class="kpi"><div class="kpi-label">Max Drawdown</div><div class="kpi-val sm">{pf.get('max_dd',0):.1f}%</div><div class="kpi-sub muted">since inception</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Macro environment
    st.markdown('<div class="sec">Macro Environment</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="kpi-row kpi-row-4">
      <div class="kpi"><div class="kpi-label">US 10Y Treasury</div><div class="kpi-val sm">{macros['us_10y']*100:.2f}%</div><div class="kpi-sub blue">Live Global Feed</div></div>
      <div class="kpi"><div class="kpi-label">TR 10Y Sovereign</div><div class="kpi-val sm">{macros['tr_10y']*100:.2f}%</div><div class="kpi-sub blue">Live from TradingView</div></div>
      <div class="kpi"><div class="kpi-label">Total Borrowing Cost</div><div class="kpi-val sm">{tp*100:.1f}%</div><div class="kpi-sub muted">US10Y + CDS + Local</div></div>
      <div class="kpi"><div class="kpi-label">Risk Parameters</div><div class="kpi-val sm">{pos_pct*100:.0f}% / {trail_stop*100:.0f}% / {time_stop}d</div><div class="kpi-sub muted">Size / Stop / Time</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Quick equity preview
    eq_curve = pf.get("equity_curve", {})
    if eq_curve:
        st.markdown('<div class="sec">Equity Curve</div>', unsafe_allow_html=True)
        df_eq = pd.DataFrame(list(eq_curve.items()), columns=["Date", "Equity"])
        df_eq["Date"] = pd.to_datetime(df_eq["Date"])
        df_eq = df_eq.set_index("Date")
        st.area_chart(df_eq, height=280, color="#4f8ff7")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: SIGNAL RADAR
# ═══════════════════════════════════════════════════════════════════════════
elif "Signal Radar" in page:
    st.markdown("""
    <div class="page-header">
      <div class="page-title">Signal Radar</div>
      <div class="page-desc">Real-time proximity analysis — which assets are approaching crisis buy zones.</div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 5])
    with col_a:
        run_scan = st.button("Scan Now", type="primary")

    if run_scan:
        progress = st.progress(0, text="Initializing...")
        results = []
        actions = []

        for idx, t in enumerate(tickers):
            progress.progress((idx+1)/len(tickers), text=f"Analyzing {t}...")
            d = deep_analyze(t, macros["tr_10y"], tp)
            if not d: continue

            now_ts = datetime.now().strftime("%Y-%m-%d %H:%M")

            # Auto execute trades
            if t in pf["holdings"]:
                h = pf["holdings"][t]
                bd = h.get("buy_date","")[:10]
                bd = datetime.strptime(bd, "%Y-%m-%d") if len(bd)>=10 else datetime.now()

                if (datetime.now()-bd).days >= time_stop:
                    prof = h["qty"]*d["price"] - h["qty"]*h["cost"]
                    pf["cash"] += h["qty"]*d["price"]
                    pf["history"].append(f"{now_ts} | TIME | {t:<12} | Exit: ${d['price']:.2f} | P&L: ${prof:>+,.0f}")
                    del pf["holdings"][t]; actions.append(("TIME",t,d["price"],prof))
                elif d["price"] >= h["target"]:
                    prof = h["qty"]*d["price"] - h["qty"]*h["cost"]
                    pf["cash"] += h["qty"]*d["price"]
                    pf["history"].append(f"{now_ts} | SELL | {t:<12} | Exit: ${d['price']:.2f} | P&L: ${prof:>+,.0f}")
                    del pf["holdings"][t]; actions.append(("SELL",t,d["price"],prof))
                elif d["price"] <= h.get("trailing_high",h["cost"])*(1-trail_stop):
                    prof = h["qty"]*d["price"] - h["qty"]*h["cost"]
                    pf["cash"] += h["qty"]*d["price"]
                    pf["history"].append(f"{now_ts} | STOP | {t:<12} | Exit: ${d['price']:.2f} | P&L: ${prof:>+,.0f}")
                    del pf["holdings"][t]; actions.append(("STOP",t,d["price"],prof))
                else:
                    pf["holdings"][t]["trailing_high"] = max(h.get("trailing_high",h["cost"]), d["price"])

            if d["signal"] and t not in pf["holdings"]:
                invest = pf["cash"] * pos_pct
                if invest >= 100:
                    qty = invest/d["price"]
                    pf["cash"] -= invest
                    pf["holdings"][t] = {"qty":qty,"cost":d["price"],"target":d["target"],"trailing_high":d["price"],"buy_date":now_ts}
                    pf["history"].append(f"{now_ts} | BUY  | {t:<12} | Entry: ${d['price']:.2f}")
                    actions.append(("BUY",t,d["price"],0))

            results.append(d | {"ticker": t})

        save_pf(pf)
        progress.empty()

        if actions:
            for a, t, p, pr in actions:
                if a=="BUY": st.success(f"Position opened — {t} at ${p:.2f}")
                elif a=="SELL": st.success(f"Target hit — {t} at ${p:.2f} | P&L: ${pr:+,.0f}")
                elif a=="TIME": st.info(f"Time stop — {t} at ${p:.2f} | P&L: ${pr:+,.0f}")
                else: st.warning(f"Stop-loss — {t} at ${p:.2f} | P&L: ${pr:+,.0f}")

        # Sort by proximity descending (closest to signal first)
        results.sort(key=lambda x: x["proximity"], reverse=True)

        st.markdown('<div class="sec">Signal Proximity Ranking</div>', unsafe_allow_html=True)

        header = "<table class='ptable'><tr><th></th><th>Instrument</th><th>Price</th><th>Bond Floor</th><th>Bank Bottom</th><th>vs Floor</th><th>From 52W High</th><th>Volatility</th><th>Signal Proximity</th><th>Status</th></tr>"
        rows = ""
        for i, r in enumerate(results):
            prox = r["proximity"]
            if prox >= 80:
                bcls, blbl = "badge-green", "ACTIVE" if r["signal"] else "ALERT"
                pcol = "#2dd4a8"
            elif prox >= 50:
                bcls, blbl = "badge-amber", "WATCHLIST"
                pcol = "#f59e0b"
            elif prox >= 25:
                bcls, blbl = "badge-muted", "DISTANT"
                pcol = "#5a5a72"
            else:
                bcls, blbl = "badge-muted", "FAR"
                pcol = "#35354a"

            rows += f"""<tr>
              <td style='color:var(--text-muted);font-size:0.7rem'>{i+1}</td>
              <td class='tk'>{r['ticker']}</td>
              <td>${r['price']:.2f}</td>
              <td>${r['bond_fv']:.2f}</td>
              <td>${r['bank_bot']:.2f}</td>
              <td class='{"c-green" if r["dist_bond"]<0 else "c-red"}'>{r['dist_bond']:+.1f}%</td>
              <td class='c-red'>{r['from_high']:.1f}%</td>
              <td>{r['vol_20d']}%</td>
              <td>
                <div style='display:flex;align-items:center;gap:10px'>
                  <span style='color:{pcol};font-weight:600;min-width:35px'>{prox:.0f}</span>
                  <div class='pbar-wrap'><div class='pbar-fill' style='width:{prox}%;background:{pcol}'></div></div>
                </div>
              </td>
              <td><span class='badge {bcls}'>{blbl}</span></td>
            </tr>"""

        st.markdown(header + rows + "</table>", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:60px 20px">
          <div style="font-size:2rem;color:var(--text-muted);margin-bottom:12px">◈</div>
          <div style="font-size:0.95rem;color:var(--text-secondary)">Press <b>Scan Now</b> to analyze all instruments in the universe.</div>
          <div style="font-size:0.8rem;color:var(--text-muted);margin-top:8px">The radar will rank every asset by how close it is to a crisis buy signal.</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: PORTFOLIO & TRADES
# ═══════════════════════════════════════════════════════════════════════════
elif "Portfolio" in page:
    st.markdown("""
    <div class="page-header">
      <div class="page-title">Portfolio & Execution History</div>
      <div class="page-desc">Current holdings and complete trade log since inception.</div>
    </div>
    """, unsafe_allow_html=True)

    tab_pos, tab_log = st.tabs(["Open Positions", "Trade History"])

    with tab_pos:
        holdings = pf.get("holdings", {})
        if not holdings:
            st.markdown("<div class='card' style='text-align:center;padding:40px'><div style='color:var(--text-muted)'>No open positions. The system is waiting for crisis entry conditions.</div></div>", unsafe_allow_html=True)
        else:
            h_html = "<table class='ptable'><tr><th>Ticker</th><th>Entry Price</th><th>Target</th><th>Current</th><th>Unrealized P&L</th><th>Days Held</th></tr>"
            for t, h in holdings.items():
                lp = (deep_analyze(t, macros["tr_10y"], tp) or {}).get("price", h["cost"])
                u = (lp - h["cost"]) * h["qty"]
                pc = (lp / h["cost"] - 1) * 100
                cls, sgn = ("c-green", "+") if u >= 0 else ("c-red", "")
                bd = h.get("buy_date","")[:10]
                days = (datetime.now() - datetime.strptime(bd, "%Y-%m-%d")).days if len(bd)>=10 else 0
                h_html += f"<tr><td class='tk'>{t}</td><td>${h['cost']:.2f}</td><td>${h['target']:.2f}</td><td>${lp:.2f}</td><td class='{cls}'>{sgn}${u:,.0f} ({sgn}{pc:.1f}%)</td><td>{days}</td></tr>"
            st.markdown(h_html + "</table>", unsafe_allow_html=True)

    with tab_log:
        if not hist:
            st.markdown("<div class='card' style='text-align:center;padding:40px'><div style='color:var(--text-muted)'>No trades recorded yet.</div></div>", unsafe_allow_html=True)
        else:
            l_html = "<div style='max-height:500px;overflow-y:auto'><table class='ptable'><tr><th>Date</th><th>Action</th><th>Ticker</th><th>Details</th></tr>"
            for entry in reversed(hist):
                parts = [p.strip() for p in entry.split("|")]
                if len(parts) >= 3:
                    dt, side, tk = parts[0], parts[1], parts[2]
                    det = " | ".join(parts[3:]) if len(parts)>3 else ""
                    sc = "c-blue" if side.strip()=="BUY" else ("c-green" if side.strip()=="SELL" else "c-red")
                    l_html += f"<tr><td class='c-muted'>{dt}</td><td class='{sc}' style='font-weight:600'>{side}</td><td>{tk}</td><td class='c-muted'>{det}</td></tr>"
            st.markdown(l_html + "</table></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════
elif "Performance" in page:
    st.markdown("""
    <div class="page-header">
      <div class="page-title">Performance Analytics</div>
      <div class="page-desc">Historical returns, drawdowns, and risk-adjusted metrics.</div>
    </div>
    """, unsafe_allow_html=True)

    dc = "green" if total_pnl >= 0 else "red"
    da = "+" if total_pnl >= 0 else ""

    # Compute Sharpe from equity curve
    eq_curve = pf.get("equity_curve", {})
    sharpe_val = "—"
    if eq_curve and len(eq_curve) > 30:
        eqvals = list(eq_curve.values())
        rets = np.diff(eqvals) / eqvals[:-1]
        if np.std(rets) > 0:
            sharpe_val = f"{(np.mean(rets)/np.std(rets))*np.sqrt(252):.2f}"

    st.markdown(f"""
    <div class="kpi-row kpi-row-4">
      <div class="kpi"><div class="kpi-label">Total Return</div><div class="kpi-val">{da}{pnl_pct:.1f}%</div><div class="kpi-sub {dc}">{da}${total_pnl:,.0f}</div></div>
      <div class="kpi"><div class="kpi-label">Sharpe Ratio</div><div class="kpi-val sm">{sharpe_val}</div><div class="kpi-sub muted">annualized</div></div>
      <div class="kpi"><div class="kpi-label">Max Drawdown</div><div class="kpi-val sm">{pf.get('max_dd',0):.1f}%</div><div class="kpi-sub red">peak to trough</div></div>
      <div class="kpi"><div class="kpi-label">Win Rate</div><div class="kpi-val sm">{wr}</div><div class="kpi-sub muted">{n_wins} wins / {n_trades} total</div></div>
    </div>
    """, unsafe_allow_html=True)

    if eq_curve:
        st.markdown('<div class="sec">Equity Curve</div>', unsafe_allow_html=True)
        df_eq = pd.DataFrame(list(eq_curve.items()), columns=["Date", "Equity"])
        df_eq["Date"] = pd.to_datetime(df_eq["Date"])
        df_eq = df_eq.set_index("Date")
        st.area_chart(df_eq, height=350, color="#4f8ff7")

        # Drawdown chart
        st.markdown('<div class="sec">Drawdown</div>', unsafe_allow_html=True)
        eq_arr = df_eq["Equity"].values
        peak = np.maximum.accumulate(eq_arr)
        dd_series = (eq_arr - peak) / peak * 100
        df_dd = pd.DataFrame({"Drawdown (%)": dd_series}, index=df_eq.index)
        st.area_chart(df_dd, height=200, color="#f87171")

    # Allocation
    st.markdown('<div class="sec">Current Allocation</div>', unsafe_allow_html=True)
    alloc = {"Cash": pf.get("cash", 100_000)}
    for t, h in pf.get("holdings", {}).items():
        alloc[t] = h["qty"] * h["cost"]
    df_al = pd.DataFrame(list(alloc.items()), columns=["Asset", "Value"]).set_index("Asset")
    st.bar_chart(df_al, height=250, color="#2dd4a8")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: HOW IT WORKS
# ═══════════════════════════════════════════════════════════════════════════
elif "How It Works" in page:
    st.markdown("""
    <div class="page-header">
      <div class="page-title">How The Model Works</div>
      <div class="page-desc">A complete guide to the algorithm, its math, and its philosophy.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="doc-section">
      <h3><span class="num">01</span> Philosophy</h3>
      <p>The Macro Floor Model rejects all conventional technical analysis — no RSI, no MACD, no Bollinger Bands. Instead, it is built on a single macroeconomic axiom: <b>Rational capital always flows to the highest risk-adjusted yield available.</b></p>
      <p>When a government bond guarantees 5% annually with zero risk, equity markets must offer a dramatically higher potential return to justify the risk. When they don't, capital exits. When too much leveraged capital exits at once, forced liquidations create a mathematically identifiable crisis — and that is where the model strikes.</p>
    </div>

    <div class="doc-section">
      <h3><span class="num">02</span> Bond Floor (Sovereign Opportunity Cost)</h3>
      <p>For every stock, the model computes a <b>Bond Floor</b> — the price at which that stock's expected return equals the risk-free government bond yield.</p>
      <p>The formula is simple but powerful:</p>
      <p><code>Bond Floor = 52-Week Rolling Low × (1 + Local Sovereign Bond Yield)</code></p>
      <p>If a stock trades above this level in a high-rate environment, it is fundamentally expensive relative to a guaranteed government return. The model will never buy above this line.</p>
    </div>

    <div class="doc-section">
      <h3><span class="num">03</span> Bank Bottom (Total Borrowing Cost Floor)</h3>
      <p>Below the Bond Floor exists a more extreme level — the <b>Bank Bottom</b>. This incorporates the full cost of leveraged capital:</p>
      <p><code>Bank Bottom = Bond Floor × (1 + US 10Y Yield + CDS Spread + Local Risk Premium)</code></p>
      <p>When prices fall below this level, institutional investors who bought using borrowed money face <b>margin calls</b>. Their brokers demand immediate cash, and when they cannot pay, their positions are <b>forcibly liquidated</b> — sold at any price, regardless of value.</p>
    </div>

    <div class="doc-section">
      <h3><span class="num">04</span> Forced Liquidation Exhaustion (The Buy Trigger)</h3>
      <p>The model does not buy simply because a stock is cheap. Buying into a panic is suicidal — the "falling knife" problem. Instead, it waits for a very specific multi-bar capitulation pattern that signals the forced selling has <b>exhausted itself</b>:</p>
      <ul>
        <li>Price is trading <b>below both</b> the Bond Floor and Bank Bottom.</li>
        <li>A bearish exhaustion candle appears: sellers pushed the high above the open, but the close fell below the previous close — maximum effort, minimum reward.</li>
        <li>This pattern repeats for <b>two consecutive sessions</b>, confirming that forced sellers are running out of inventory.</li>
      </ul>
      <p>Only when all three conditions align does the model fire a <code>BUY</code> signal.</p>
    </div>

    <div class="doc-section">
      <h3><span class="num">05</span> Signal Proximity Score (Radar System)</h3>
      <p>Not every stock is either a buy or not-a-buy. The model computes a <b>Signal Proximity Score (0–100)</b> for every instrument in the universe:</p>
      <ul>
        <li><b>0–25 (Far):</b> Trading well above the Bond Floor. No action warranted.</li>
        <li><b>25–50 (Distant):</b> Approaching the Bond Floor zone. Worth monitoring.</li>
        <li><b>50–80 (Watchlist):</b> Below the Bond Floor or near the Bank Bottom. A macro shock could trigger a buy signal within days.</li>
        <li><b>80–100 (Alert/Active):</b> Deep below the Bank Bottom with exhaustion patterns forming. Buy signal is imminent or already active.</li>
      </ul>
    </div>

    <div class="doc-section">
      <h3><span class="num">06</span> Exit Strategy (Three-Layer Defense)</h3>
      <p>Once a position is opened, the model monitors it autonomously with three independent exit mechanisms:</p>
      <ul>
        <li><b>Target Exit (SELL):</b> The stock recovers to or above its Bond Floor valuation — where it becomes fairly valued again. This is the ideal outcome.</li>
        <li><b>Trailing Stop (STOP):</b> A dynamic stop-loss that follows the price upward. If the stock rises 20% then drops 12% from that peak, the stop triggers — locking in an 8% gain instead of riding it back to zero. If the stock never rises, the stop caps the maximum loss at the configured percentage (default: 12%).</li>
        <li><b>Time Stop (TIME):</b> If a position shows no meaningful movement for 90 days, the model liquidates it regardless of P&L. Capital must never be held hostage — it must be freed for the next crisis opportunity.</li>
      </ul>
    </div>

    <div class="doc-section">
      <h3><span class="num">07</span> Position Sizing & Risk Management</h3>
      <p>The model allocates a fixed percentage of total equity (default: 25%) to each new position. This ensures:</p>
      <ul>
        <li>No single position can destroy the fund. Even a 100% loss on one trade loses only 25% of capital.</li>
        <li>Up to 4 concurrent positions can be held, providing diversification across crises.</li>
        <li>Position size scales with fund growth — as the fund grows, so does each position in absolute terms.</li>
      </ul>
    </div>

    <div class="doc-section">
      <h3><span class="num">08</span> Data Sources</h3>
      <ul>
        <li><b>Stock Prices:</b> Live Market Data Feeds (real-time/15-min delayed)</li>
        <li><b>US 10Y Treasury Yield:</b> Global Fixed Income Feed (<code>^TNX</code>)</li>
        <li><b>Emerging Market Risk (TR 10Y):</b> Live real-time yield data via TradingView API (<code>TVC:TR10Y</code>).</li>
        <li><b>Portfolio State:</b> Encrypted cloud persistence via MongoDB Atlas.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)
