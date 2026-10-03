"""
Uncle Model — Macro Floor & Forced Liquidation System
Professional autonomous trading dashboard.
"""

from __future__ import annotations

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pymongo
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="Uncle Model | Macro Floor & Forced Liquidation System",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Professional CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0e1a;
    color: #c9d1e0;
  }

  .stApp { background-color: #0a0e1a; }

  /* Hide Streamlit defaults */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background-color: #0d1120;
    border-right: 1px solid #1e2740;
  }
  section[data-testid="stSidebar"] * { color: #8892a4 !important; }
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3 {
    color: #e2e8f0 !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
  }

  /* Top header strip */
  .sys-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    padding: 0 0 24px 0;
    border-bottom: 1px solid #1e2740;
    margin-bottom: 28px;
  }
  .sys-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #e2e8f0;
    letter-spacing: 0.04em;
  }
  .sys-sub {
    font-size: 0.72rem;
    color: #4a5568;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 4px;
  }
  .sys-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #38a169;
    letter-spacing: 0.06em;
    text-align: right;
  }
  .sys-status span { color: #4a5568; }

  /* KPI cards */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: #1e2740;
    border: 1px solid #1e2740;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 28px;
  }
  .kpi-card {
    background: #0d1120;
    padding: 18px 20px;
  }
  .kpi-label {
    font-size: 0.65rem;
    font-weight: 600;
    color: #4a5568;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  .kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.35rem;
    font-weight: 500;
    color: #e2e8f0;
    line-height: 1;
  }
  .kpi-delta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    margin-top: 6px;
  }
  .kpi-delta.pos { color: #38a169; }
  .kpi-delta.neg { color: #e53e3e; }
  .kpi-delta.neu { color: #4a5568; }

  /* Section titles */
  .sec-title {
    font-size: 0.68rem;
    font-weight: 600;
    color: #4a5568;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding-bottom: 10px;
    border-bottom: 1px solid #1e2740;
    margin-bottom: 16px;
  }

  /* Macro bar */
  .macro-bar {
    display: flex;
    gap: 32px;
    background: #0d1120;
    border: 1px solid #1e2740;
    border-radius: 6px;
    padding: 14px 20px;
    margin-bottom: 28px;
    flex-wrap: wrap;
  }
  .macro-item { display: flex; flex-direction: column; gap: 4px; }
  .macro-key {
    font-size: 0.62rem;
    color: #4a5568;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    font-weight: 600;
  }
  .macro-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    color: #a0aec0;
  }
  .macro-live { color: #d4a017; }

  /* Scan table */
  .scan-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
  }
  .scan-table th {
    font-size: 0.62rem;
    font-weight: 600;
    color: #4a5568;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #1e2740;
  }
  .scan-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #111827;
    font-family: 'JetBrains Mono', monospace;
    color: #8892a4;
  }
  .scan-table tr:hover td { background: #0d1120; color: #c9d1e0; }
  .scan-table .ticker { color: #e2e8f0; font-weight: 500; }
  .signal-active { color: #38a169 !important; font-weight: 600; }
  .signal-none { color: #2d3748 !important; }

  /* Positions table */
  .pos-row {
    display: grid;
    grid-template-columns: 80px 1fr 1fr 1fr 1fr 80px;
    gap: 0;
    padding: 12px 14px;
    border-bottom: 1px solid #111827;
    align-items: center;
    font-size: 0.8rem;
  }
  .pos-row:hover { background: #0d1120; }
  .pos-ticker { font-weight: 600; color: #e2e8f0; letter-spacing: 0.04em; font-size: 0.85rem; }
  .pos-num { font-family: 'JetBrains Mono', monospace; color: #8892a4; }
  .pos-pnl-pos { font-family: 'JetBrains Mono', monospace; color: #38a169; font-weight: 500; }
  .pos-pnl-neg { font-family: 'JetBrains Mono', monospace; color: #e53e3e; font-weight: 500; }
  .pos-header {
    display: grid;
    grid-template-columns: 80px 1fr 1fr 1fr 1fr 80px;
    gap: 0;
    padding: 8px 14px;
    font-size: 0.62rem;
    font-weight: 600;
    color: #4a5568;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    border-bottom: 1px solid #1e2740;
  }

  /* Trade log */
  .trade-row {
    display: grid;
    grid-template-columns: 110px 70px 80px 1fr 90px;
    gap: 0;
    padding: 9px 14px;
    border-bottom: 1px solid #111827;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #4a5568;
    align-items: center;
  }
  .trade-row:hover { color: #8892a4; background: #0d1120; }
  .trade-buy { color: #38a169 !important; font-weight: 600; }
  .trade-sell { color: #a0aec0 !important; }
  .trade-stop { color: #e53e3e !important; }
  .trade-profit-pos { color: #38a169 !important; }
  .trade-profit-neg { color: #e53e3e !important; }

  /* Action button */
  .stButton > button {
    background: #0d1120 !important;
    color: #e2e8f0 !important;
    border: 1px solid #1e2740 !important;
    border-radius: 4px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 10px 24px !important;
    transition: all 0.15s !important;
  }
  .stButton > button:hover {
    background: #1e2740 !important;
    border-color: #2d3a58 !important;
    color: #fff !important;
  }
  .stButton > button[kind="primary"] {
    background: #1a2a4a !important;
    border-color: #2563eb !important;
    color: #93c5fd !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: #1e3a6e !important;
    color: #bfdbfe !important;
  }

  /* Slider */
  .stSlider [data-baseweb="slider"] { background: #1e2740; }

  /* Selectbox / input */
  .stTextArea textarea {
    background: #0d1120 !important;
    border: 1px solid #1e2740 !important;
    color: #8892a4 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
  }

  /* Progress bar */
  .stProgress > div > div { background: #2563eb !important; }

  /* Divider */
  hr { border-color: #1e2740 !important; margin: 24px 0 !important; }

  /* Hide index in st.dataframe */
  .stDataFrame { border: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Watchlist ─────────────────────────────────────────────────────────────────
DEFAULT_TICKERS = [
    "AAPL", "TSLA", "NVDA", "AMZN", "MSFT", "META", "GOOG", "AMD",
    "NFLX", "INTC", "JPM", "BAC",
    "THYAO.IS", "AKBNK.IS", "ISCTR.IS", "TUPRS.IS", "GARAN.IS",
    "SISE.IS", "KCHOL.IS", "SAHOL.IS",
]

# ── MongoDB ───────────────────────────────────────────────────────────────────
@st.cache_resource
def _mongo_client():
    try:
        uri = st.secrets["MONGO_URI"]
    except Exception:
        uri = "mongodb://localhost:27017/"
    return pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)

def _collection():
    return _mongo_client()["uncle_bot_db"]["portfolio"]

def _empty_portfolio() -> dict:
    return {"_id": "main_fund", "cash": 100_000.0, "holdings": {}, "history": []}

def load_portfolio() -> dict:
    try:
        doc = _collection().find_one({"_id": "main_fund"})
        if doc:
            return doc
    except Exception:
        pass
    if "ram_pf" not in st.session_state:
        st.session_state.ram_pf = _build_real_history()
    return st.session_state.ram_pf

def save_portfolio(pf: dict):
    try:
        _collection().update_one({"_id": "main_fund"}, {"$set": pf}, upsert=True)
    except Exception:
        st.session_state.ram_pf = pf

# ── Synthetic 5-year history generator ───────────────────────────────────────
def _build_real_history() -> dict:
    """
    Runs a real 5-year backtest on the DEFAULT_TICKERS universe to 
    reconstruct the exact portfolio state and history the model 
    would have generated over the last 5 years.
    """
    tr_10y = 0.33
    total_prem = 0.0525 + 0.025 + 0.10  # US 10Y + CDS + Local

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
        except Exception:
            pass

    all_dates = set()
    for df in dfs.values():
        all_dates.update(df.index.tolist())
    sorted_dates = sorted(list(all_dates))

    cash = 100_000.0
    holdings = {}
    history = []
    position_pct = 0.25
    trailing_stop = 0.12

    for d in sorted_dates:
        # Calculate current equity for position sizing
        h_val = 0.0
        for t, h in holdings.items():
            if d in dfs[t].index:
                h_val += h['qty'] * float(dfs[t].loc[d, 'Close'])
            else:
                h_val += h['qty'] * h['cost']
        
        equity = cash + h_val

        # Exits
        sold_this_day = set()
        for t, h in list(holdings.items()):
            if d not in dfs[t].index: continue
            row = dfs[t].loc[d]
            price = float(row['Close'])
            high = float(row['High'])
            
            if high >= h['target']:
                rev = h['qty'] * h['target']
                prof = rev - (h['qty'] * h['cost'])
                cash += rev
                pct = (h['target']/h['cost']-1)*100
                history.append(f"{d.strftime('%Y-%m-%d %H:%M')} | SELL | {t:<12} | Exit: ${h['target']:.2f}  | P&L: ${prof:>+,.0f}  ({pct:+.1f}%)")
                del holdings[t]
                sold_this_day.add(t)
            elif price <= h['trailing_high'] * (1 - trailing_stop):
                rev = h['qty'] * price
                prof = rev - (h['qty'] * h['cost'])
                cash += rev
                pct = (price/h['cost']-1)*100
                history.append(f"{d.strftime('%Y-%m-%d %H:%M')} | STOP | {t:<12} | Exit: ${price:.2f}  | P&L: ${prof:>+,.0f}  ({pct:+.1f}%)")
                del holdings[t]
                sold_this_day.add(t)
            else:
                holdings[t]['trailing_high'] = max(holdings[t]['trailing_high'], high)

        # Entries
        for t, df in dfs.items():
            if t in holdings or t in sold_this_day: continue
            if d not in df.index: continue
            
            row = df.loc[d]
            if bool(row['Signal']):
                invest = equity * position_pct
                if cash >= invest and invest >= 100:
                    price = float(row['Close'])
                    if pd.isna(row['Bond_FV']) or pd.isna(price): continue
                    target = max(float(row['Bond_FV']), price * 1.25)
                    qty = invest / price
                    
                    cash -= invest
                    holdings[t] = {
                        'qty': qty,
                        'cost': price,
                        'target': target,
                        'trailing_high': price,
                        'buy_date': d.strftime('%Y-%m-%d %H:%M')
                    }
                    history.append(f"{d.strftime('%Y-%m-%d %H:%M')} | BUY  | {t:<12} | Entry: ${price:.2f} | Target: ${target:.2f}")

    return {
        "_id": "main_fund",
        "cash": round(cash, 2),
        "holdings": holdings,
        "history": history,
        "inception": sorted_dates[0].strftime('%Y-%m-%d') if sorted_dates else "2019-10-01"
    }

# ── Live Macro ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def fetch_macros() -> dict:
    us_10y = 0.0525
    try:
        data = yf.download("^TNX", period="5d", progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        if not data.empty:
            us_10y = float(data["Close"].dropna().iloc[-1]) / 100.0
    except Exception:
        pass
    return {
        "us_10y": us_10y,
        "tr_10y": 0.33,
        "cds": 0.025,
        "local_risk": 0.10,
    }

# ── Stock Analysis ────────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def analyze_stock(ticker: str, tr_10y: float, total_premium: float) -> dict | None:
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index().dropna(subset=["Close"])
        if len(df) < 10:
            return None

        close = df["Close"].values.astype(float)
        opn   = df["Open"].values.astype(float)
        high  = df["High"].values.astype(float)

        rolling_base = float(df["Low"].min())
        bond_fv  = rolling_base * (1 + tr_10y)
        bank_bot = bond_fv * (1 + total_premium)
        cur = float(close[-1])

        prev_close   = np.roll(close, 1); prev_close[0] = np.nan
        cond1        = (close < bond_fv) & (close < bank_bot)
        bearish      = (high > opn) & (close < prev_close) & (close < opn)
        b_prev       = np.roll(bearish, 1); b_prev[0] = False
        signal       = bool(cond1[-1] & bearish[-1] & b_prev[-1])

        return {
            "price":        cur,
            "bond_fv":      bond_fv,
            "bank_bot":     bank_bot,
            "target":       max(bond_fv, cur * 1.25),
            "signal":       signal,
            "distance_pct": round((cur - bond_fv) / bond_fv * 100, 2),
        }
    except Exception:
        return None

# ════════════════════════════════════════════════════════════════════════════
# DATA LOAD
# ════════════════════════════════════════════════════════════════════════════
pf     = load_portfolio()
macros = fetch_macros()
total_prem = macros["us_10y"] + macros["cds"] + macros["local_risk"]

# Portfolio math
holdings_value = sum(
    h["qty"] * (analyze_stock(t, macros["tr_10y"], total_prem) or {}).get("price", h["cost"])
    for t, h in pf.get("holdings", {}).items()
)
total_equity   = pf.get("cash", 100_000) + holdings_value
total_pnl      = total_equity - 100_000
total_pnl_pct  = total_pnl / 100_000 * 100
inception      = pf.get("inception", "2019-10-01")

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## System Parameters")
    position_pct  = st.slider("Position Size (%)", 5, 50, 25) / 100
    trailing_stop = st.slider("Trailing Stop-Loss (%)", 5, 25, 12) / 100

    st.markdown("---")
    st.markdown("## Universe")
    custom_tickers = st.text_area("", ", ".join(DEFAULT_TICKERS), height=160)
    tickers = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]

    st.markdown("---")
    st.markdown("## System")
    st.markdown(f"<div style='font-size:0.7rem;color:#2d3748;line-height:1.8'>Inception: {inception}<br>Engine: V3.0<br>Universe: {len(tickers)} instruments</div>", unsafe_allow_html=True)
    if st.button("Reset to $100K & Re-run 5Y Backtest"):
        with st.spinner("Downloading 5 years of market data and reconstructing portfolio... (Takes ~15 secs)"):
            save_portfolio(_build_real_history())
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════
now_str = datetime.now().strftime("%d %b %Y  %H:%M:%S")
st.markdown(f"""
<div class="sys-header">
  <div>
    <div class="sys-title">Macro Floor &amp; Forced Liquidation System</div>
    <div class="sys-sub">Sovereign Opportunity Cost · Crisis Signal Detection · Autonomous Execution</div>
  </div>
  <div class="sys-status">
    LIVE &nbsp;·&nbsp; <span>{now_str}</span><br>
    <span>INCEPTION {inception} &nbsp;·&nbsp; ENGINE V3.0</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# KPI STRIP
# ════════════════════════════════════════════════════════════════════════════
delta_class = "pos" if total_pnl >= 0 else "neg"
delta_arrow = "+" if total_pnl >= 0 else ""

open_pos     = len(pf.get("holdings", {}))
history      = pf.get("history", [])
sell_trades  = [h for h in history if "| SELL |" in h or "SELL (" in h]
num_trades   = len(sell_trades)
win_trades   = len([h for h in sell_trades if "+$" in h or "(+" in h or "P&L: $+" in h])
win_rate     = f"{win_trades/num_trades*100:.0f}%" if num_trades else "—"

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Total AUM</div>
    <div class="kpi-value">${total_equity:,.0f}</div>
    <div class="kpi-delta {delta_class}">{delta_arrow}${total_pnl:,.0f} &nbsp; ({delta_arrow}{total_pnl_pct:.1f}%)</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Available Cash</div>
    <div class="kpi-value">${pf.get('cash', 100_000):,.0f}</div>
    <div class="kpi-delta neu">{pf.get('cash', 100_000)/total_equity*100:.1f}% of AUM</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Open Positions</div>
    <div class="kpi-value">{open_pos}</div>
    <div class="kpi-delta neu">${holdings_value:,.0f} deployed</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Total Executions</div>
    <div class="kpi-value">{num_trades}</div>
    <div class="kpi-delta neu">since {inception}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Win Rate</div>
    <div class="kpi-value">{win_rate}</div>
    <div class="kpi-delta neu">{win_trades} profitable closes</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# MACRO BAR
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="macro-bar">
  <div class="macro-item">
    <span class="macro-key">US 10Y Yield</span>
    <span class="macro-val macro-live">{macros['us_10y']*100:.2f}%</span>
  </div>
  <div class="macro-item">
    <span class="macro-key">TR 10Y Yield</span>
    <span class="macro-val">{macros['tr_10y']*100:.1f}%</span>
  </div>
  <div class="macro-item">
    <span class="macro-key">CDS Premium</span>
    <span class="macro-val">{macros['cds']*100:.1f}%</span>
  </div>
  <div class="macro-item">
    <span class="macro-key">Local Risk Margin</span>
    <span class="macro-val">{macros['local_risk']*100:.1f}%</span>
  </div>
  <div class="macro-item">
    <span class="macro-key">Total Borrowing Cost</span>
    <span class="macro-val">{total_prem*100:.1f}%</span>
  </div>
  <div class="macro-item">
    <span class="macro-key">Position Size</span>
    <span class="macro-val">{position_pct*100:.0f}% per signal</span>
  </div>
  <div class="macro-item">
    <span class="macro-key">Trailing Stop</span>
    <span class="macro-val">{trailing_stop*100:.0f}%</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SCAN PANEL
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">Market Scan &amp; Autopilot Execution</div>', unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns([1, 6])
with col_btn1:
    run_scan = st.button("Run Scan", type="primary")

if run_scan:
    progress = st.progress(0, text="Initializing scan...")
    rows     = []
    actions  = []

    for idx, t in enumerate(tickers):
        progress.progress((idx + 1) / len(tickers), text=f"Scanning {t}...")
        data = analyze_stock(t, macros["tr_10y"], total_prem)
        if not data:
            continue

        signal_label = "ACTIVE" if data["signal"] else "—"
        signal_class = "signal-active" if data["signal"] else "signal-none"
        now_ts       = datetime.now().strftime("%Y-%m-%d %H:%M")

        rows.append({
            "ticker":       t,
            "price":        f"${data['price']:.2f}",
            "bond_floor":   f"${data['bond_fv']:.2f}",
            "bank_floor":   f"${data['bank_bot']:.2f}",
            "distance":     f"{data['distance_pct']:+.1f}%",
            "signal_label": signal_label,
            "signal_class": signal_class,
        })

        # AUTO SELL
        if t in pf["holdings"]:
            h = pf["holdings"][t]
            if data["price"] >= h["target"]:
                rev    = h["qty"] * data["price"]
                profit = rev - (h["qty"] * h["cost"])
                pf["cash"] += rev
                pf["history"].append(
                    f"{now_ts} | SELL | {t:<12} | Exit: ${data['price']:.2f}  | P&L: ${profit:>+,.0f}  (+{(data['price']/h['cost']-1)*100:.1f}%)"
                )
                del pf["holdings"][t]
                actions.append(("SELL", t, data["price"], profit))
            elif data["price"] <= h.get("trailing_high", h["cost"]) * (1 - trailing_stop):
                rev    = h["qty"] * data["price"]
                profit = rev - (h["qty"] * h["cost"])
                pf["cash"] += rev
                pf["history"].append(
                    f"{now_ts} | STOP | {t:<12} | Exit: ${data['price']:.2f}  | P&L: ${profit:>+,.0f}"
                )
                del pf["holdings"][t]
                actions.append(("STOP", t, data["price"], profit))
            else:
                pf["holdings"][t]["trailing_high"] = max(
                    h.get("trailing_high", h["cost"]), data["price"]
                )

        # AUTO BUY
        if data["signal"] and t not in pf["holdings"]:
            invest = pf["cash"] * position_pct
            if invest >= 100:
                qty = invest / data["price"]
                pf["cash"] -= invest
                pf["holdings"][t] = {
                    "qty": qty, "cost": data["price"],
                    "target": data["target"],
                    "trailing_high": data["price"],
                    "buy_date": now_ts,
                }
                pf["history"].append(
                    f"{now_ts} | BUY  | {t:<12} | Entry: ${data['price']:.2f} | Target: ${data['target']:.2f}"
                )
                actions.append(("BUY", t, data["price"], 0))

    save_portfolio(pf)
    progress.empty()

    # Action summary
    if actions:
        for action, t, price, profit in actions:
            if action == "BUY":
                st.success(f"Position opened — {t} at ${price:.2f}")
            elif action == "SELL":
                st.success(f"Position closed — {t} at ${price:.2f}  |  P&L: ${profit:+,.0f}")
            else:
                st.warning(f"Stop-loss triggered — {t} at ${price:.2f}  |  P&L: ${profit:+,.0f}")
    else:
        st.info("Scan complete. No signals detected. System monitoring.")

    # Results table
    if rows:
        header = "<table class='scan-table'><tr><th>Instrument</th><th>Last Price</th><th>Bond Floor</th><th>Bank Floor</th><th>vs Floor</th><th>Signal</th></tr>"
        body   = ""
        for r in rows:
            body += f"""<tr>
              <td class='ticker'>{r['ticker']}</td>
              <td>{r['price']}</td>
              <td>{r['bond_floor']}</td>
              <td>{r['bank_floor']}</td>
              <td>{r['distance']}</td>
              <td class='{r['signal_class']}'>{r['signal_label']}</td>
            </tr>"""
        st.markdown(header + body + "</table>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# POSITIONS + HISTORY
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
left, right = st.columns([1, 1])

with left:
    st.markdown('<div class="sec-title">Open Positions</div>', unsafe_allow_html=True)
    holdings = pf.get("holdings", {})
    if not holdings:
        st.markdown("<div style='color:#2d3748;font-size:0.8rem;padding:12px 0'>No open positions. System awaiting entry conditions.</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="pos-header">
          <span>Ticker</span><span>Entry</span><span>Target</span><span>Current</span><span>P&L</span><span>Date</span>
        </div>
        """, unsafe_allow_html=True)
        for t, h in holdings.items():
            live  = analyze_stock(t, macros["tr_10y"], total_prem)
            live_p = live["price"] if live else h["cost"]
            unr   = (live_p - h["cost"]) * h["qty"]
            pct   = (live_p - h["cost"]) / h["cost"] * 100
            pcls  = "pos-pnl-pos" if unr >= 0 else "pos-pnl-neg"
            sign  = "+" if unr >= 0 else ""
            date_short = h["buy_date"][:10] if "buy_date" in h else "—"
            st.markdown(f"""
            <div class="pos-row">
              <span class="pos-ticker">{t}</span>
              <span class="pos-num">${h['cost']:.2f}</span>
              <span class="pos-num">${h['target']:.2f}</span>
              <span class="pos-num">${live_p:.2f}</span>
              <span class="{pcls}">{sign}${unr:,.0f} ({sign}{pct:.1f}%)</span>
              <span class="pos-num" style="font-size:0.7rem">{date_short}</span>
            </div>
            """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="sec-title">Execution Log</div>', unsafe_allow_html=True)
    hist = pf.get("history", [])
    if not hist:
        st.markdown("<div style='color:#2d3748;font-size:0.8rem;padding:12px 0'>No executions recorded.</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='max-height:360px;overflow-y:auto;'>
        <table class='scan-table' style='width:100%'>
        <tr><th>Date</th><th>Side</th><th>Ticker</th><th>Details</th></tr>
        """, unsafe_allow_html=True)

        rows_html = ""
        for entry in reversed(hist[-60:]):
            parts = [p.strip() for p in entry.split("|")]
            if len(parts) >= 3:
                date_p  = parts[0] if len(parts) > 0 else ""
                side_p  = parts[1] if len(parts) > 1 else ""
                tick_p  = parts[2] if len(parts) > 2 else ""
                detail  = " | ".join(parts[3:]) if len(parts) > 3 else ""

                side_clean = side_p.strip()
                if side_clean == "BUY":
                    scls = "trade-buy"
                elif side_clean in ("SELL", "SATIŞ"):
                    scls = "trade-sell"
                else:
                    scls = "trade-stop"

                rows_html += f"""<tr class='trade-row' style='display:table-row'>
                  <td style='font-family:JetBrains Mono,monospace;font-size:0.72rem;color:#4a5568'>{date_p}</td>
                  <td class='{scls}' style='font-family:JetBrains Mono,monospace;font-size:0.72rem'>{side_clean}</td>
                  <td style='font-family:JetBrains Mono,monospace;font-size:0.72rem;color:#a0aec0'>{tick_p}</td>
                  <td style='font-family:JetBrains Mono,monospace;font-size:0.7rem;color:#4a5568'>{detail}</td>
                </tr>"""

        st.markdown(rows_html + "</table></div>", unsafe_allow_html=True)
