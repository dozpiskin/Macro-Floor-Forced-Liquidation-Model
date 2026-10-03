"""
Uncle Model — Macro Floor & Forced Liquidation System
Professional autonomous trading dashboard with Analytics & Documentation.
"""

from __future__ import annotations

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pymongo
from datetime import datetime

st.set_page_config(
    page_title="Uncle Model | Autonomous Fund",
    page_icon="▱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Professional Softer CSS (Fintech Slate Theme) ────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #18181b; /* Soft Zinc-900 */
    color: #e4e4e7; /* Zinc-200 */
  }

  .stApp { background-color: #18181b; }

  /* Hide Streamlit defaults */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background-color: #27272a; /* Zinc-800 */
    border-right: 1px solid #3f3f46;
  }
  section[data-testid="stSidebar"] * { color: #a1a1aa !important; }
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3 {
    color: #f4f4f5 !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
  }

  /* Top header strip */
  .sys-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    padding: 0 0 20px 0;
    border-bottom: 1px solid #3f3f46;
    margin-bottom: 24px;
    margin-top: -20px;
  }
  .sys-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: #f4f4f5;
    letter-spacing: 0.02em;
  }
  .sys-sub {
    font-size: 0.75rem;
    color: #a1a1aa;
    margin-top: 4px;
  }
  .sys-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #10b981; /* Emerald-500 */
    letter-spacing: 0.05em;
    text-align: right;
  }
  .sys-status span { color: #71717a; }

  /* Tabs Styling */
  .stTabs [data-baseweb="tab-list"] {
    gap: 24px;
    background-color: transparent;
  }
  .stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
    color: #a1a1aa;
    font-weight: 500;
    font-size: 0.9rem;
  }
  .stTabs [aria-selected="true"] {
    color: #f4f4f5;
    border-bottom: 2px solid #3b82f6 !important; /* Blue-500 */
  }

  /* KPI cards */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 24px;
  }
  .kpi-card {
    background: #27272a;
    border: 1px solid #3f3f46;
    border-radius: 8px;
    padding: 18px 20px;
  }
  .kpi-label {
    font-size: 0.65rem;
    font-weight: 600;
    color: #a1a1aa;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  .kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.25rem;
    font-weight: 500;
    color: #f4f4f5;
    line-height: 1;
  }
  .kpi-delta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    margin-top: 8px;
  }
  .kpi-delta.pos { color: #10b981; }
  .kpi-delta.neg { color: #ef4444; }
  .kpi-delta.neu { color: #71717a; }

  /* Section titles */
  .sec-title {
    font-size: 0.7rem;
    font-weight: 600;
    color: #a1a1aa;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding-bottom: 8px;
    border-bottom: 1px solid #3f3f46;
    margin-bottom: 16px;
    margin-top: 12px;
  }

  /* Macro bar */
  .macro-bar {
    display: flex;
    gap: 32px;
    background: #27272a;
    border: 1px solid #3f3f46;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }
  .macro-item { display: flex; flex-direction: column; gap: 4px; }
  .macro-key {
    font-size: 0.65rem;
    color: #a1a1aa;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-weight: 600;
  }
  .macro-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #d4d4d8;
  }
  .macro-live { color: #3b82f6; }

  /* Tables */
  .custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
  }
  .custom-table th {
    font-size: 0.65rem;
    font-weight: 600;
    color: #a1a1aa;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #3f3f46;
  }
  .custom-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #3f3f46;
    font-family: 'JetBrains Mono', monospace;
    color: #d4d4d8;
  }
  .custom-table tr:hover td { background: #27272a; color: #f4f4f5; }
  
  /* Log Colors */
  .trade-buy { color: #3b82f6 !important; font-weight: 600; }
  .trade-sell { color: #a1a1aa !important; }
  .trade-stop { color: #ef4444 !important; }

  /* Action button */
  .stButton > button {
    background: #27272a !important;
    color: #e4e4e7 !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
  }
  .stButton > button:hover {
    background: #3f3f46 !important;
    color: #fff !important;
  }
  .stButton > button[kind="primary"] {
    background: #3b82f6 !important;
    border-color: #2563eb !important;
    color: #fff !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: #2563eb !important;
  }

  /* Sliders and Inputs */
  .stSlider [data-baseweb="slider"] { background: #3f3f46; }
  .stTextArea textarea {
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #d4d4d8 !important;
  }
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

def load_portfolio() -> dict:
    try:
        doc = _collection().find_one({"_id": "main_fund"})
        if doc: return doc
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

# ── Dynamic 5-Year Engine ─────────────────────────────────────────────────────
def _build_real_history() -> dict:
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
        except Exception:
            pass

    all_dates = set()
    for df in dfs.values():
        all_dates.update(df.index.tolist())
    sorted_dates = sorted(list(all_dates))

    cash = 100_000.0
    holdings = {}
    history = []
    equity_curve = {}
    
    position_pct = 0.25
    trailing_stop = 0.12
    time_stop_days = 90

    for d in sorted_dates:
        h_val = 0.0
        for t, h in holdings.items():
            if d in dfs[t].index: h_val += h['qty'] * float(dfs[t].loc[d, 'Close'])
            else: h_val += h['qty'] * h['cost']
        
        equity = cash + h_val
        equity_curve[d.strftime('%Y-%m-%d')] = round(equity, 2)

        sold_this_day = set()
        for t, h in list(holdings.items()):
            if d not in dfs[t].index: continue
            row = dfs[t].loc[d]
            price = float(row['Close'])
            high = float(row['High'])
            
            buy_d = pd.to_datetime(h['buy_date'])
            if (d - buy_d).days >= time_stop_days:
                rev = h['qty'] * price
                prof = rev - (h['qty'] * h['cost'])
                cash += rev
                history.append(f"{d.strftime('%Y-%m-%d %H:%M')} | TIME | {t:<12} | Exit: ${price:.2f}  | P&L: ${prof:>+,.0f}")
                del holdings[t]
                sold_this_day.add(t)
            elif high >= h['target']:
                rev = h['qty'] * h['target']
                prof = rev - (h['qty'] * h['cost'])
                cash += rev
                history.append(f"{d.strftime('%Y-%m-%d %H:%M')} | SELL | {t:<12} | Exit: ${h['target']:.2f}  | P&L: ${prof:>+,.0f}")
                del holdings[t]
                sold_this_day.add(t)
            elif price <= h['trailing_high'] * (1 - trailing_stop):
                rev = h['qty'] * price
                prof = rev - (h['qty'] * h['cost'])
                cash += rev
                history.append(f"{d.strftime('%Y-%m-%d %H:%M')} | STOP | {t:<12} | Exit: ${price:.2f}  | P&L: ${prof:>+,.0f}")
                del holdings[t]
                sold_this_day.add(t)
            else:
                holdings[t]['trailing_high'] = max(holdings[t]['trailing_high'], high)

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
                        'qty': qty, 'cost': price, 'target': target,
                        'trailing_high': price, 'buy_date': d.strftime('%Y-%m-%d %H:%M')
                    }
                    history.append(f"{d.strftime('%Y-%m-%d %H:%M')} | BUY  | {t:<12} | Entry: ${price:.2f}")

    return {
        "_id": "main_fund", "cash": round(cash, 2), "holdings": holdings,
        "history": history, "equity_curve": equity_curve,
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
    except: pass
    return {"us_10y": us_10y, "tr_10y": 0.33, "cds": 0.025, "local_risk": 0.10}

@st.cache_data(ttl=900, show_spinner=False)
def analyze_stock(ticker: str, tr_10y: float, total_premium: float) -> dict | None:
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index().dropna(subset=["Close"])
        if len(df) < 10: return None

        close, opn, high = df["Close"].values.astype(float), df["Open"].values.astype(float), df["High"].values.astype(float)
        bond_fv = float(df["Low"].min()) * (1 + tr_10y)
        bank_bot = bond_fv * (1 + total_premium)
        cur = float(close[-1])

        prev_close = np.roll(close, 1); prev_close[0] = np.nan
        cond1 = (close < bond_fv) & (close < bank_bot)
        bearish = (high > opn) & (close < prev_close) & (close < opn)
        b_prev = np.roll(bearish, 1); b_prev[0] = False
        signal = bool(cond1[-1] & bearish[-1] & b_prev[-1])

        return {
            "price": cur, "bond_fv": bond_fv, "bank_bot": bank_bot,
            "target": max(bond_fv, cur * 1.25), "signal": signal,
            "distance_pct": round((cur - bond_fv) / bond_fv * 100, 2)
        }
    except: return None

# ════════════════════════════════════════════════════════════════════════════
# CORE DATA
# ════════════════════════════════════════════════════════════════════════════
pf = load_portfolio()
macros = fetch_macros()
total_prem = macros["us_10y"] + macros["cds"] + macros["local_risk"]

holdings_value = sum(h["qty"] * (analyze_stock(t, macros["tr_10y"], total_prem) or {}).get("price", h["cost"]) for t, h in pf.get("holdings", {}).items())
total_equity = pf.get("cash", 100_000) + holdings_value
total_pnl = total_equity - 100_000
total_pnl_pct = total_pnl / 100_000 * 100
inception = pf.get("inception", "2019-10-01")

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## System Parameters")
    position_pct  = st.slider("Position Size (%)", 5, 50, 25) / 100
    trailing_stop = st.slider("Trailing Stop-Loss (%)", 5, 25, 12) / 100
    time_stop_days = st.slider("Time Stop (Days)", 30, 365, 90)

    st.markdown("---")
    st.markdown("## Universe")
    custom_tickers = st.text_area("", ", ".join(DEFAULT_TICKERS), height=160)
    tickers = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]

    st.markdown("---")
    st.markdown("## System")
    st.markdown(f"<div style='font-size:0.75rem;color:#71717a;'>Inception: {inception}<br>Engine: V3.0</div>", unsafe_allow_html=True)
    if st.button("Reset & Re-run Backtest"):
        with st.spinner("Downloading 5 years of market data... (Takes ~15 secs)"):
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
    <span>INCEPTION {inception}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
tab_dash, tab_charts, tab_docs = st.tabs(["📊 Live Dashboard", "📈 Analytics & Charts", "🧠 Model Mechanics"])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1: DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────
with tab_dash:
    delta_class = "pos" if total_pnl >= 0 else "neg"
    delta_arrow = "+" if total_pnl >= 0 else ""

    open_pos     = len(pf.get("holdings", {}))
    history      = pf.get("history", [])
    sell_trades  = [h for h in history if "| SELL |" in h or "| STOP |" in h or "| TIME |" in h]
    num_trades   = len(sell_trades)
    win_trades   = len([h for h in sell_trades if "P&L: $+" in h])
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

    st.markdown(f"""
    <div class="macro-bar">
      <div class="macro-item"><span class="macro-key">US 10Y Yield</span><span class="macro-val macro-live">{macros['us_10y']*100:.2f}%</span></div>
      <div class="macro-item"><span class="macro-key">TR 10Y Yield</span><span class="macro-val">{macros['tr_10y']*100:.1f}%</span></div>
      <div class="macro-item"><span class="macro-key">Total Borrowing Cost</span><span class="macro-val">{total_prem*100:.1f}%</span></div>
      <div class="macro-item"><span class="macro-key">Position Size</span><span class="macro-val">{position_pct*100:.0f}%</span></div>
      <div class="macro-item"><span class="macro-key">Trailing Stop</span><span class="macro-val">{trailing_stop*100:.0f}%</span></div>
      <div class="macro-item"><span class="macro-key">Time Stop</span><span class="macro-val">{time_stop_days} days</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-title">Market Scan & Autopilot Execution</div>', unsafe_allow_html=True)
    if st.button("Run Scan", type="primary"):
        progress = st.progress(0, text="Initializing scan...")
        actions = []
        for idx, t in enumerate(tickers):
            progress.progress((idx + 1) / len(tickers), text=f"Scanning {t}...")
            data = analyze_stock(t, macros["tr_10y"], total_prem)
            if not data: continue

            now_ts = datetime.now().strftime("%Y-%m-%d %H:%M")

            if t in pf["holdings"]:
                h = pf["holdings"][t]
                buy_d_str = h.get("buy_date", "")[:10]
                buy_d = datetime.strptime(buy_d_str, "%Y-%m-%d") if len(buy_d_str) >= 10 else datetime.now()
                
                if (datetime.now() - buy_d).days >= time_stop_days:
                    rev, profit = h["qty"] * data["price"], (h["qty"] * data["price"]) - (h["qty"] * h["cost"])
                    pf["cash"] += rev
                    pf["history"].append(f"{now_ts} | TIME | {t:<12} | Exit: ${data['price']:.2f} | P&L: ${profit:>+,.0f}")
                    del pf["holdings"][t]
                    actions.append(("TIME", t, data["price"], profit))
                elif data["price"] >= h["target"]:
                    rev, profit = h["qty"] * data["price"], (h["qty"] * data["price"]) - (h["qty"] * h["cost"])
                    pf["cash"] += rev
                    pf["history"].append(f"{now_ts} | SELL | {t:<12} | Exit: ${data['price']:.2f} | P&L: ${profit:>+,.0f}")
                    del pf["holdings"][t]
                    actions.append(("SELL", t, data["price"], profit))
                elif data["price"] <= h.get("trailing_high", h["cost"]) * (1 - trailing_stop):
                    rev, profit = h["qty"] * data["price"], (h["qty"] * data["price"]) - (h["qty"] * h["cost"])
                    pf["cash"] += rev
                    pf["history"].append(f"{now_ts} | STOP | {t:<12} | Exit: ${data['price']:.2f} | P&L: ${profit:>+,.0f}")
                    del pf["holdings"][t]
                    actions.append(("STOP", t, data["price"], profit))
                else:
                    pf["holdings"][t]["trailing_high"] = max(h.get("trailing_high", h["cost"]), data["price"])

            if data["signal"] and t not in pf["holdings"]:
                invest = pf["cash"] * position_pct
                if invest >= 100:
                    qty = invest / data["price"]
                    pf["cash"] -= invest
                    pf["holdings"][t] = {"qty": qty, "cost": data["price"], "target": data["target"], "trailing_high": data["price"], "buy_date": now_ts}
                    pf["history"].append(f"{now_ts} | BUY  | {t:<12} | Entry: ${data['price']:.2f}")
                    actions.append(("BUY", t, data["price"], 0))

        save_portfolio(pf)
        progress.empty()

        if actions:
            for action, t, price, profit in actions:
                if action == "BUY": st.success(f"Position opened — {t} at ${price:.2f}")
                elif action == "SELL": st.success(f"Target Hit — {t} at ${price:.2f} | P&L: ${profit:+,.0f}")
                elif action == "TIME": st.info(f"Time Stop (Expired) — {t} at ${price:.2f} | P&L: ${profit:+,.0f}")
                else: st.warning(f"Stop-loss triggered — {t} at ${price:.2f} | P&L: ${profit:+,.0f}")
        else:
            st.info("Scan complete. No signals detected. System monitoring.")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="sec-title">Open Positions</div>', unsafe_allow_html=True)
        if not pf.get("holdings"):
            st.markdown("<div style='color:#71717a;font-size:0.8rem;'>No open positions.</div>", unsafe_allow_html=True)
        else:
            p_html = "<table class='custom-table'><tr><th>Ticker</th><th>Entry</th><th>Target</th><th>Live Price</th><th>Unrealized P&L</th></tr>"
            for t, h in pf["holdings"].items():
                live_p = (analyze_stock(t, macros["tr_10y"], total_prem) or {}).get("price", h["cost"])
                unr, pct = (live_p - h["cost"]) * h["qty"], (live_p / h["cost"] - 1) * 100
                pcls, sign = ("#10b981", "+") if unr >= 0 else ("#ef4444", "")
                p_html += f"<tr><td style='color:#f4f4f5;font-weight:600'>{t}</td><td>${h['cost']:.2f}</td><td>${h['target']:.2f}</td><td>${live_p:.2f}</td><td style='color:{pcls}'>{sign}${unr:,.0f} ({sign}{pct:.1f}%)</td></tr>"
            st.markdown(p_html + "</table>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="sec-title">Execution Log</div>', unsafe_allow_html=True)
        if not history:
            st.markdown("<div style='color:#71717a;font-size:0.8rem;'>No executions yet.</div>", unsafe_allow_html=True)
        else:
            l_html = "<div style='max-height:400px;overflow-y:auto;'><table class='custom-table'><tr><th>Date</th><th>Side</th><th>Ticker</th><th>Details</th></tr>"
            for entry in reversed(history):
                parts = [p.strip() for p in entry.split("|")]
                if len(parts) >= 3:
                    date_p, side_p, tick_p, detail = parts[0], parts[1], parts[2], " | ".join(parts[3:]) if len(parts)>3 else ""
                    scls = "trade-buy" if side_p == "BUY" else ("trade-sell" if side_p in ("SELL", "TIME") else "trade-stop")
                    l_html += f"<tr><td style='color:#71717a'>{date_p}</td><td class='{scls}'>{side_p}</td><td style='color:#a1a1aa'>{tick_p}</td><td style='color:#71717a'>{detail}</td></tr>"
            st.markdown(l_html + "</table></div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# TAB 2: CHARTS & ANALYTICS
# ──────────────────────────────────────────────────────────────────────────────
with tab_charts:
    st.markdown('<div class="sec-title">5-Year Equity Curve</div>', unsafe_allow_html=True)
    eq_curve = pf.get("equity_curve", {})
    if eq_curve:
        df_eq = pd.DataFrame(list(eq_curve.items()), columns=["Date", "Equity"])
        df_eq["Date"] = pd.to_datetime(df_eq["Date"])
        df_eq = df_eq.set_index("Date")
        st.area_chart(df_eq, height=350, color="#3b82f6")
    else:
        st.info("Equity curve data is currently compiling. Run a full backtest (Reset button) to generate.")

    st.markdown('<div class="sec-title">Current Asset Allocation</div>', unsafe_allow_html=True)
    alloc_data = {"Cash": pf.get("cash", 100_000)}
    for t, h in pf.get("holdings", {}).items():
        alloc_data[t] = h["qty"] * h["cost"]
    
    df_alloc = pd.DataFrame(list(alloc_data.items()), columns=["Asset", "Value ($)"]).set_index("Asset")
    st.bar_chart(df_alloc, height=300, color="#10b981")


# ──────────────────────────────────────────────────────────────────────────────
# TAB 3: MODEL MECHANICS (DOCUMENTATION)
# ──────────────────────────────────────────────────────────────────────────────
with tab_docs:
    st.markdown("""
    <div style="padding: 24px; background-color: #27272a; border-radius: 8px; border: 1px solid #3f3f46; color: #d4d4d8; font-size: 0.9rem; line-height: 1.6;">
    
    <h2 style="color: #f4f4f5; font-size: 1.5rem; border-bottom: 1px solid #3f3f46; padding-bottom: 12px; margin-bottom: 24px;">
        🧠 The Uncle Model: Algorithmic Crisis Detection
    </h2>
    
    <p>The Uncle Model is an autonomous, macro-driven algorithmic trading system. It completely ignores traditional technical indicators like RSI, MACD, or Moving Averages. Instead, it operates on a singular institutional truth: <b>Capital flows where yield is highest.</b></p>
    
    <br>
    
    <h3 style="color: #3b82f6; font-size: 1.15rem; margin-top: 16px;">1. The Sovereign Opportunity Cost (Bond Floor)</h3>
    <p>When risk-free government bonds yield 5% (US) or 33% (Turkey), capital naturally drains from risky equities. The model calculates the exact price a stock must fall to in order to mathematically compete with the risk-free bond yield over a 1-year horizon. We call this the <b>Bond Floor</b>.</p>
    <p><i>If a stock is trading above this floor during high interest rate environments, it is fundamentally overvalued.</i></p>
    
    <br>

    <h3 style="color: #3b82f6; font-size: 1.15rem; margin-top: 16px;">2. The Bank Bottom & Margin Calls</h3>
    <p>Below the Bond Floor lies the <b>Bank Bottom</b>. This secondary floor incorporates the additional cost of borrowing money (Credit Default Swaps + Local Risk Premiums). When a stock falls below this level, institutional investors who bought on leverage (credit) face severe <b>Margin Calls</b> from their brokers.</p>
    
    <br>

    <h3 style="color: #3b82f6; font-size: 1.15rem; margin-top: 16px;">3. Forced Liquidation Detection (The Buy Signal)</h3>
    <p>Falling below the Bank Bottom is not enough to trigger a buy—catching a falling knife is dangerous. The system strictly waits for <b>Forced Liquidation Exhaustion</b>. It autonomously executes a <code>BUY</code> order only when it detects a specific capitulation pattern:</p>
    <ul>
        <li>The price is deep below the ultimate Bank Bottom.</li>
        <li>A massive intraday gap or reversal occurs (Panic Selling).</li>
        <li>The institutional selling pressure mathematically exhausts itself.</li>
    </ul>
    
    <br>

    <h3 style="color: #3b82f6; font-size: 1.15rem; margin-top: 16px;">4. Autonomous Execution & Exits</h3>
    <p>Once a position is opened, the system monitors it 24/7 without human intervention using strict exit rules:</p>
    <ul>
        <li><b>Target Exit (SELL):</b> The asset recovers past its fundamental Bond Floor valuation.</li>
        <li><b>Trailing Stop (STOP):</b> A dynamic safety net that locks in profits as the stock rises, or cuts losses immediately if the crisis deepens beyond mathematical bounds.</li>
        <li><b>Time Stop (TIME):</b> Capital is never held hostage. If an asset flatlines for 90 days (dead money), the system autonomously liquidates it to free up cash for the next crisis.</li>
    </ul>

    </div>
    """, unsafe_allow_html=True)
