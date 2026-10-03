# Uncle Model — Algorithmic Valuation & Liquidity Crisis Engine

An autonomous quantitative trading bot that detects **macro-economic crisis bottoms** by comparing stock prices against their opportunity-cost floors (government bond yields, inflation, FX carry, sovereign borrowing costs) and waits for **margin-call exhaustion signals** before entering positions.

---

## Core Philosophy

> The value of a stock is not solely determined by its balance sheet; it is heavily influenced by inflation, the 10-year government bond yield (risk-free alternative), FX carry-trade costs, sovereign borrowing costs (Eurobond + CDS risk premium), and forced liquidations from margin calls.

The model calculates **6 valuation phases** that represent different layers of opportunity cost. When a stock's price falls below these floors **and** forced liquidations are detected in the candlestick patterns, the system triggers a **"buy the crisis"** signal.

---

## The 6-Phase Valuation Algorithm

| Phase | Name | Formula | Logic |
|-------|------|---------|-------|
| **1** | Technical Retracement | `(peak - base) / 3` | Classic 1/3 correction supports |
| **2** | Inflation Bottom | `base × (1 + inflation)` | Below this, investor loses to inflation |
| **3** | Bond Fair Value | `base × (1 + 10Y yield)` | Minimum fair value vs risk-free return |
| **4** | Bank Borrowing Bottom | `Phase3 × (1 + US10Y + CDS + local)` | No bank borrows cheaper than the sovereign |
| **5** | FX Carry Bottom | `base × (1 + FX depreciation)` | Foreign investor's breakeven after FX loss |
| **6** | Margin Call Limit | `price × (1 + margin rate)` | Forced liquidation pressure zone |

---

## Signal Logic (Finding the Bottom)

The bot does **not** buy when the price first enters the crisis zone. It waits for **margin-call exhaustion**:

1. **Condition 1 — Liquidity Pressure:** Price is below both Phase 3 (Bond Floor) and Phase 4 (Borrowing Floor)
2. **Condition 2 — Seller Exhaustion:** For 2 consecutive days, the stock attempted to rise intraday (`High > Open`) but failed to hold, closing negative (`Close < Previous Close AND Close < Open`)

When both conditions are met → **Uncle Signal: STRONG BUY**

---

## Exit Rules

| Rule | Trigger | Purpose |
|------|---------|---------|
| **Take Profit** | Price reaches locked target (max of Bond FV or entry + 25%) | Capture crisis recovery gains |
| **Trailing Stop** | Price drops 12% from post-entry high | Protect profits if recovery stalls |
| **Time Stop** | 126 trading days (6 months) without target | Free capital for next opportunity |

---

## Project Structure

```
uncle-model-fund/
├── uncle_model.py          # Core OOP engine (phases, signals, charts)
├── backtest_uncle.py       # 5-year backtest with performance analytics
├── live_uncle_tracker.py   # Streamlit autonomous dashboard (deploy this)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Quick Start (Local)

```bash
pip install -r requirements.txt

# Run the core model
python uncle_model.py

# Run the 5-year backtest
python backtest_uncle.py

# Launch the live dashboard
streamlit run live_uncle_tracker.py
```

---

## Cloud Deployment (Free, 24/7)

### 1. GitHub
Push this repository to a public GitHub repo.

### 2. MongoDB Atlas (Free Tier)
Create a free M0 cluster at [mongodb.com](https://mongodb.com). Get the connection string:
```
mongodb+srv://username:password@cluster0...
```

### 3. Streamlit Community Cloud
Deploy at [share.streamlit.io](https://share.streamlit.io):
- Select this repository
- Set `live_uncle_tracker.py` as the main file
- In **Advanced Settings → Secrets**, add:
  ```toml
  MONGO_URI = "mongodb+srv://username:password@cluster0..."
  ```

### 4. UptimeRobot
Add a free HTTP monitor at [uptimerobot.com](https://uptimerobot.com) pointing to your Streamlit URL with a 5-minute interval to prevent sleep.

---

## Dashboard Features

- **Autopilot Mode:** One-click scan of 20+ tickers with automatic buy/sell execution
- **Live Macro Feed:** US 10-Year Treasury yield pulled from Yahoo Finance
- **Position Sizing:** Configurable % of capital per trade (default 25%)
- **Trailing Stop-Loss:** Adjustable via sidebar (default 12%)
- **Real-time P&L:** Per-position and total portfolio tracking
- **MongoDB Persistence:** Portfolio survives server restarts
- **Portfolio Reset:** One-click reset to $100K starting capital

---

## Backtest Analytics (V3.0)

The backtest engine reports:
- **Total Return** and **Net Profit**
- **Win Rate** (profitable trades / total trades)
- **Max Drawdown** (largest peak-to-trough decline)
- **Sharpe Ratio** (risk-adjusted return, annualized)
- Complete **trade log** with entry/exit prices and reasons

---

## License

This project is provided for educational and research purposes only. It is not financial advice. Use at your own risk.
