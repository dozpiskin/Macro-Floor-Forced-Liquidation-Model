"""
Uncle Model — Autonomous Cloud Dashboard (V3.0)
=================================================
Streamlit app with MongoDB persistence, live macro data,
multi-ticker scanning, autopilot trading, position sizing,
trailing stop-loss management, and portfolio P&L tracking.
"""

from __future__ import annotations

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pymongo
from datetime import datetime

st.set_page_config(
    page_title="Uncle Model Fund",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Watchlist ────────────────────────────────────────────────────────────────
DEFAULT_TICKERS = [
    "AAPL", "TSLA", "NVDA", "AMZN", "MSFT", "META", "GOOG", "AMD",
    "NFLX", "INTC", "JPM", "BAC",
    "THYAO.IS", "AKBNK.IS", "ISCTR.IS", "TUPRS.IS", "GARAN.IS",
    "SISE.IS", "KCHOL.IS", "SAHOL.IS",
]

# ── MongoDB ──────────────────────────────────────────────────────────────────
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
        if doc:
            return doc
    except Exception:
        pass
    # Fallback to RAM
    if "ram_pf" not in st.session_state:
        st.session_state.ram_pf = _empty_portfolio()
    return st.session_state.ram_pf


def save_portfolio(pf: dict):
    try:
        _collection().update_one({"_id": "main_fund"}, {"$set": pf}, upsert=True)
    except Exception:
        st.session_state.ram_pf = pf


def _empty_portfolio() -> dict:
    return {"_id": "main_fund", "cash": 100_000.0, "holdings": {}, "history": []}


# ── Live Macro Data ──────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def fetch_macros() -> dict:
    us_10y = 0.0525  # fallback
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


# ── Model Logic (vectorized) ────────────────────────────────────────────────
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
        opn = df["Open"].values.astype(float)
        high = df["High"].values.astype(float)

        rolling_base = float(df["Low"].min())
        bond_fv = rolling_base * (1 + tr_10y)
        bank_bot = bond_fv * (1 + total_premium)
        cur = float(close[-1])

        prev_close = np.roll(close, 1)
        prev_close[0] = np.nan
        cond1 = (close < bond_fv) & (close < bank_bot)
        bearish = (high > opn) & (close < prev_close) & (close < opn)
        b_prev = np.roll(bearish, 1)
        b_prev[0] = False
        signal = bool(cond1[-1] & bearish[-1] & b_prev[-1])

        return {
            "price": cur,
            "bond_fv": bond_fv,
            "bank_bot": bank_bot,
            "target": max(bond_fv, cur * 1.25),
            "signal": signal,
            "distance_pct": round((cur - bond_fv) / bond_fv * 100, 2),
        }
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════
pf = load_portfolio()
macros = fetch_macros()
total_prem = macros["us_10y"] + macros["cds"] + macros["local_risk"]

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Ayarlar")
    position_pct = st.slider("Pozisyon Büyüklüğü (%)", 5, 100, 25) / 100
    trailing_stop = st.slider("Trailing Stop-Loss (%)", 5, 30, 12) / 100
    st.markdown("---")
    st.subheader("📊 Canlı Makro")
    st.metric("ABD 10Y Tahvil", f"%{macros['us_10y']*100:.2f}")
    st.metric("TR 10Y Tahvil", f"%{macros['tr_10y']*100:.1f}")
    st.metric("CDS + Yerel Risk", f"%{(macros['cds']+macros['local_risk'])*100:.1f}")
    st.markdown("---")
    custom_tickers = st.text_area("Takip Listesi", ", ".join(DEFAULT_TICKERS))
    tickers = [t.strip().upper() for t in custom_tickers.split(",") if t.strip()]

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🤖 Uncle Model — Autonomous Fund")

holdings_value = 0.0
for t, h in pf.get("holdings", {}).items():
    try:
        d = analyze_stock(t, macros["tr_10y"], total_prem)
        if d:
            holdings_value += h["qty"] * d["price"]
    except Exception:
        holdings_value += h["qty"] * h["cost"]  # fallback to cost

total_equity = pf.get("cash", 100_000) + holdings_value
total_pnl = total_equity - 100_000

c1, c2, c3, c4 = st.columns(4)
c1.metric("Toplam Varlık", f"${total_equity:,.2f}")
c2.metric("Nakit Kasa", f"${pf.get('cash', 100_000):,.2f}")
c3.metric("Açık Pozisyonlar", str(len(pf.get("holdings", {}))))
c4.metric("Toplam P&L", f"${total_pnl:,.2f}", delta=f"{total_pnl/1000:.1f}K")

st.markdown("---")

# ── Autopilot ────────────────────────────────────────────────────────────────
if st.button("🚀  AUTOPILOT — Radarı Çalıştır & İşlemleri Otomatik Yap", type="primary", use_container_width=True):
    progress = st.progress(0, text="Taranıyor...")
    rows = []
    actions_taken = []

    for idx, t in enumerate(tickers):
        progress.progress((idx + 1) / len(tickers), text=f"{t} analiz ediliyor...")
        data = analyze_stock(t, macros["tr_10y"], total_prem)
        if not data:
            continue

        status = "🟢 AL SİNYALİ" if data["signal"] else "🔴 Sinyal Yok"
        rows.append({
            "Hisse": t,
            "Fiyat": f"${data['price']:.2f}",
            "Tahvil Hedefi": f"${data['bond_fv']:.2f}",
            "Dibe Uzaklık": f"{data['distance_pct']:.1f}%",
            "Sinyal": status,
        })

        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # AUTO SELL (target reached or trailing stop)
        if t in pf["holdings"]:
            h = pf["holdings"][t]
            if data["price"] >= h["target"]:
                rev = h["qty"] * data["price"]
                profit = rev - (h["qty"] * h["cost"])
                pf["cash"] += rev
                pf["history"].append(f"🎯 [SATIŞ] {now} | {t} hedefe ulaştı! Kâr: ${profit:.2f}")
                del pf["holdings"][t]
                actions_taken.append(f"🎯 {t} SATILDI (Kâr: ${profit:.2f})")
            elif data["price"] <= h.get("trailing_high", h["cost"]) * (1 - trailing_stop):
                rev = h["qty"] * data["price"]
                profit = rev - (h["qty"] * h["cost"])
                pf["cash"] += rev
                pf["history"].append(f"🛑 [STOP] {now} | {t} trailing stop tetiklendi. P&L: ${profit:.2f}")
                del pf["holdings"][t]
                actions_taken.append(f"🛑 {t} STOP (P&L: ${profit:.2f})")
            else:
                # Update trailing high
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
                    "qty": qty,
                    "cost": data["price"],
                    "target": data["target"],
                    "trailing_high": data["price"],
                    "buy_date": now,
                }
                pf["history"].append(f"🟢 [ALIM] {now} | {t} | Fiyat: ${data['price']:.2f} | Hedef: ${data['target']:.2f}")
                actions_taken.append(f"🟢 {t} ALINDI (${data['price']:.2f})")

    save_portfolio(pf)
    progress.empty()

    if actions_taken:
        for a in actions_taken:
            st.success(a)
    else:
        st.info("Bugün sinyal yok. Bot fırsat bekliyor...")

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── Portfolio & History ──────────────────────────────────────────────────────
st.markdown("---")
left, right = st.columns(2)

with left:
    st.subheader("💼 Aktif Pozisyonlar")
    if not pf.get("holdings"):
        st.caption("Açık pozisyon yok. Fırsat bekleniyor...")
    else:
        for t, h in pf["holdings"].items():
            live = analyze_stock(t, macros["tr_10y"], total_prem)
            live_p = live["price"] if live else h["cost"]
            unrealized = (live_p - h["cost"]) * h["qty"]
            pnl_pct = (live_p - h["cost"]) / h["cost"] * 100
            color = "green" if unrealized >= 0 else "red"
            st.markdown(
                f"**{t}** &nbsp; Alış: \\${h['cost']:.2f} → Şimdi: \\${live_p:.2f} "
                f"&nbsp; | &nbsp; Hedef: \\${h['target']:.2f} "
                f"&nbsp; | &nbsp; P&L: **:{color}[\\${unrealized:+,.2f} ({pnl_pct:+.1f}%)]** "
                f"&nbsp; | &nbsp; {h['buy_date']}"
            )

with right:
    st.subheader("📜 İşlem Geçmişi")
    if not pf.get("history"):
        st.caption("Henüz işlem yapılmadı.")
    else:
        for h in reversed(pf["history"][-50:]):
            st.text(h)

# ── Reset ────────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button("🗑️ Portföyü Sıfırla (100.000$ ile yeniden başla)"):
    new_pf = _empty_portfolio()
    save_portfolio(new_pf)
    st.session_state.ram_pf = new_pf
    st.rerun()
