"""
Uncle Model — Algorithmic Valuation & Liquidity Crisis Engine
=============================================================
Core OOP engine. Calculates 6-phase macro valuation levels,
scans candlestick data for margin-call exhaustion signals,
and renders interactive Plotly charts.

Usage:
    from uncle_model import UncleModel
    model = UncleModel("AKBNK.IS", base_price=51, peak_price=90, current_price=71)
    model.print_report()
    model.generate_signals()
    model.plot_chart()
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

warnings.filterwarnings("ignore", category=FutureWarning)


# ---------------------------------------------------------------------------
# Data-class for macro parameters (clean defaults, zero boilerplate)
# ---------------------------------------------------------------------------
@dataclass
class MacroParams:
    """Encapsulates every macro-economic input the model needs."""
    inflation_rate: float = 0.32
    tr_10y_yield: float = 0.38
    us_10y_yield: float = 0.055
    cds_risk_premium: float = 0.02
    margin_loan_rate: float = 0.08
    fx_depreciation_rate: float = 0.18
    local_risk_margin: float = 0.10

    @property
    def total_borrowing_premium(self) -> float:
        """Government Charisma Rule: no bank borrows cheaper than the sovereign."""
        return self.us_10y_yield + self.cds_risk_premium + self.local_risk_margin


# ---------------------------------------------------------------------------
# Phase-level result container
# ---------------------------------------------------------------------------
@dataclass
class PhaseLevels:
    """Holds the computed price levels for all 6 phases."""
    support_1: float = 0.0
    support_2: float = 0.0
    inflation_bottom: float = 0.0
    bond_fair_value: float = 0.0
    bank_borrowing_bottom: float = 0.0
    fx_carry_bottom: float = 0.0
    margin_call_limit: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "Phase 1: Support 1": self.support_1,
            "Phase 1: Support 2": self.support_2,
            "Phase 2: Inflation Bottom": self.inflation_bottom,
            "Phase 3: Bond Fair Value": self.bond_fair_value,
            "Phase 4: Bank Borrowing Bottom": self.bank_borrowing_bottom,
            "Phase 5: FX Carry Bottom": self.fx_carry_bottom,
            "Phase 6: Margin Call Limit": self.margin_call_limit,
        }

    def to_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame(
            list(self.to_dict().items()),
            columns=["Phase / Level", "Price"],
        )
        df["Price"] = df["Price"].map(lambda x: f"{x:.2f}")
        return df


# ---------------------------------------------------------------------------
# Helper: robust yfinance download
# ---------------------------------------------------------------------------
def _download(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Download OHLCV from yfinance with multi-index flattening."""
    df = yf.download(ticker, period=period, progress=False)
    if df.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return (
        df.reset_index()
        .rename(columns={"Date": "Date", "Datetime": "Date"})
        .dropna(subset=["Open", "High", "Low", "Close"])
    )


# ---------------------------------------------------------------------------
# Main model
# ---------------------------------------------------------------------------
class UncleModel:
    """
    Uncle's Algorithmic Valuation and Liquidity Crisis Model.

    Determines whether a stock is trading below its macro-economic
    opportunity-cost floor and detects margin-call exhaustion signals
    that mark the end of forced liquidations.
    """

    __slots__ = ("ticker", "base_price", "peak_price", "current_price",
                 "macros", "levels", "_df")

    def __init__(
        self,
        ticker: str,
        base_price: float,
        peak_price: float,
        current_price: float,
        macros: Optional[MacroParams] = None,
        # Legacy keyword pass-through for backward compatibility
        inflation_rate: float | None = None,
        tr_10y_yield: float | None = None,
        us_10y_yield: float | None = None,
        cds_risk_premium: float | None = None,
        margin_loan_rate: float | None = None,
        fx_depreciation_rate: float | None = None,
        local_risk_margin: float | None = None,
    ):
        self.ticker = ticker
        self.base_price = base_price
        self.peak_price = peak_price
        self.current_price = current_price

        if macros is not None:
            self.macros = macros
        else:
            kw: dict = {}
            if inflation_rate is not None:
                kw["inflation_rate"] = inflation_rate
            if tr_10y_yield is not None:
                kw["tr_10y_yield"] = tr_10y_yield
            if us_10y_yield is not None:
                kw["us_10y_yield"] = us_10y_yield
            if cds_risk_premium is not None:
                kw["cds_risk_premium"] = cds_risk_premium
            if margin_loan_rate is not None:
                kw["margin_loan_rate"] = margin_loan_rate
            if fx_depreciation_rate is not None:
                kw["fx_depreciation_rate"] = fx_depreciation_rate
            if local_risk_margin is not None:
                kw["local_risk_margin"] = local_risk_margin
            self.macros = MacroParams(**kw)

        self.levels: Optional[PhaseLevels] = None
        self._df: Optional[pd.DataFrame] = None

    # ---- Phase calculations ------------------------------------------------

    def calculate_levels(self) -> PhaseLevels:
        m = self.macros
        margin = (self.peak_price - self.base_price) / 3.0

        self.levels = PhaseLevels(
            support_1=self.peak_price - margin,
            support_2=self.peak_price - 2 * margin,
            inflation_bottom=self.base_price * (1 + m.inflation_rate),
            bond_fair_value=self.base_price * (1 + m.tr_10y_yield),
            bank_borrowing_bottom=(
                self.base_price
                * (1 + m.tr_10y_yield)
                * (1 + m.total_borrowing_premium)
            ),
            fx_carry_bottom=self.base_price * (1 + m.fx_depreciation_rate),
            margin_call_limit=self.current_price * (1 + m.margin_loan_rate),
        )
        return self.levels

    # ---- Report ------------------------------------------------------------

    def print_report(self) -> pd.DataFrame:
        if self.levels is None:
            self.calculate_levels()

        header = f" UNCLE MODEL VALUATION REPORT: {self.ticker.upper()}"
        print(f"\n{'=' * 65}\n{header}\n{'=' * 65}")
        df = self.levels.to_dataframe()
        print(df.to_string(index=False, justify="left"))
        print("=" * 65 + "\n")
        return df

    # ---- Data fetch --------------------------------------------------------

    def fetch_data(self, period: str = "1y") -> pd.DataFrame:
        self._df = _download(self.ticker, period)
        return self._df

    # ---- Signal generation (fully vectorized, no loops) --------------------

    def generate_signals(self) -> pd.DataFrame:
        if self._df is None:
            self.fetch_data()
        if self.levels is None:
            self.calculate_levels()

        df = self._df.copy()
        close = df["Close"].values
        high = df["High"].values
        opn = df["Open"].values

        prev_close = np.empty_like(close)
        prev_close[0] = np.nan
        prev_close[1:] = close[:-1]

        bond_fv = self.levels.bond_fair_value
        bank_bot = self.levels.bank_borrowing_bottom

        # Condition 1: Price under both macro floors
        cond1 = (close < bond_fv) & (close < bank_bot)

        # Condition 2: Bearish rejection (upper shadow + negative close)
        bearish = (high > opn) & (close < prev_close) & (close < opn)
        bearish_prev = np.empty_like(bearish)
        bearish_prev[0] = False
        bearish_prev[1:] = bearish[:-1]
        cond2 = bearish & bearish_prev

        df["Uncle_Signal"] = cond1 & cond2
        self._df = df

        signals = df.loc[df["Uncle_Signal"]]
        print(f"--- SIGNAL SCANNER ({self.ticker}) ---")
        if signals.empty:
            print("No Uncle Signal in available data.")
        else:
            for _, r in signals.iterrows():
                d = r["Date"]
                ds = d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)
                print(f"[{ds}] MARGIN CALL CLEANSING COMPLETE — STRONG BUY")
        print("-" * 60 + "\n")
        return df

    # ---- Visualization -----------------------------------------------------

    _LEVEL_COLORS = {
        "Phase 1: Support 1": "#5dade2",
        "Phase 1: Support 2": "#2e86c1",
        "Phase 2: Inflation Bottom": "#f39c12",
        "Phase 3: Bond Fair Value": "#27ae60",
        "Phase 4: Bank Borrowing Bottom": "#8e44ad",
        "Phase 5: FX Carry Bottom": "#e67e22",
        "Phase 6: Margin Call Limit": "#c0392b",
    }

    def plot_chart(self) -> go.Figure:
        if self._df is None or "Uncle_Signal" not in self._df.columns:
            self.generate_signals()

        df = self._df
        fig = go.Figure()

        # Candlesticks
        fig.add_trace(go.Candlestick(
            x=df["Date"], open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"], name="Price",
            increasing_line_color="green", decreasing_line_color="red",
        ))

        # Horizontal level lines
        for name, value in self.levels.to_dict().items():
            color = self._LEVEL_COLORS.get(name, "white")
            fig.add_hline(
                y=value, line_dash="dash", line_color=color, line_width=1.5,
                annotation_text=f"{name} ({value:.2f})",
                annotation_position="top left",
                annotation_font=dict(size=10, color=color),
            )

        # Buy markers
        sigs = df.loc[df["Uncle_Signal"]]
        if not sigs.empty:
            fig.add_trace(go.Scatter(
                x=sigs["Date"], y=sigs["Low"] * 0.95,
                mode="markers+text",
                marker=dict(symbol="triangle-up", size=16, color="#00ff00",
                            line=dict(width=2, color="darkgreen")),
                text=["BUY"] * len(sigs), textposition="bottom center",
                textfont=dict(color="#00ff00", size=12, family="Arial Black"),
                name="Uncle Signal",
            ))

        fig.update_layout(
            title=f"<b>{self.ticker} — Uncle Model Valuation & Crisis Chart</b>",
            yaxis_title="Price", xaxis_title="Date",
            template="plotly_dark", height=800, width=1200,
            hovermode="x unified", showlegend=False,
            margin=dict(l=50, r=50, t=80, b=50),
        )
        fig.update_xaxes(rangeslider_visible=False)
        return fig


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    model = UncleModel(
        ticker="AKBNK.IS",
        base_price=51.0,
        peak_price=90.0,
        current_price=71.0,
        inflation_rate=0.32,
        tr_10y_yield=0.38,
        us_10y_yield=0.055,
        cds_risk_premium=0.02,
        margin_loan_rate=0.08,
        fx_depreciation_rate=0.18,
        local_risk_margin=0.10,
    )
    model.print_report()
    model.generate_signals()
    # model.plot_chart().show()
