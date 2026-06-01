# Risk Analytics Dashboard
### MCA · Financial Analytics · Capstone Project

> A fully functional, interactive 10-module Risk Analytics Dashboard built with Python, Streamlit, and Plotly — covering live NSE/BSE stock data, forecasting, valuation, portfolio optimization, and credit risk modelling.

---

## 📊 Dashboard Modules

| # | Module | Marks | Key Techniques |
|---|--------|-------|----------------|
| 1 | Executive Summary Panel | 15 | KPI cards, sparklines, BUY/HOLD/SELL signal |
| 2 | ARIMA Forecasting | 15 | auto_arima, walk-forward validation, AIC/BIC |
| 3 | GARCH Volatility | 12 | GARCH(1,1), regime detection (percentile), spike annotation |
| 4 | DCF Valuation | 13 | Gordon Growth Model, waterfall chart, margin of safety |
| 5 | Monte Carlo Simulation | 13 | GBM, 10,000 paths, probability summary |
| 6 | Value at Risk (VaR) | 15 | Historical + Parametric + MC VaR, CVaR, Kupiec test |
| 7 | Credit Risk Modelling | 13 | Logistic Regression, AUC-ROC, gauge chart, PD trend |
| 8 | Portfolio Optimisation | 12 | Efficient frontier (5,000 portfolios), max-Sharpe |
| 9 | Stress Testing | 10 | Factor betas, 6 scenarios, bar chart |
| 10 | Correlation Heatmap | 8 | Log-return correlation, ⚠ annotations, diversification insight |

**Total: 126 base marks + 20 bonus (deployed app)**

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+ (3.10 or 3.11 recommended)
- pip

### 1. Clone / extract the project
```bash
git clone <your-repo-url>
cd risk_dashboard
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the dashboard
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🗂️ Project Structure

```
risk_dashboard/
├── app.py                  # Main Streamlit application (all 10 modules)
├── requirements.txt        # Pinned dependencies
├── README.md               # This file
└── assets/
    └── style.css           # Custom dark-theme CSS
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Streamlit Frontend                 │
│  Sidebar: Ticker Selector · Date Picker · Portfolio  │
├──────────┬──────────┬──────────┬────────────────────┤
│ Module 1 │ Module 2 │ Module 3 │     ...            │
│ Exec Sum │  ARIMA   │  GARCH   │  Modules 4–10      │
├──────────┴──────────┴──────────┴────────────────────┤
│              Data & Computation Layer                │
│  @st.cache_data  ·  yFinance  ·  pandas / numpy     │
├─────────────────────────────────────────────────────┤
│              Modelling Libraries                     │
│  pmdarima · arch · scikit-learn · PyPortfolioOpt     │
│  scipy · statsmodels                                 │
└─────────────────────────────────────────────────────┘
```

---

## 📐 Key Formulas

### Investment Signal (Module 1)
```
BUY   : Margin of Safety > 20%  AND  VaR 95% > -5%
HOLD  : Margin of Safety 5–20%
SELL  : otherwise
```

### ARIMA Walk-Forward Validation (Module 2)
- Train: first 80% of data
- Test: rolling 1-step-ahead predictions on remaining 20%
- Metrics: RMSE (in-sample vs out-of-sample), MAE, MAPE

### GARCH Volatility Regime (Module 3)
```
HIGH     : current vol > 75th percentile of historical series
LOW      : current vol < 25th percentile
MODERATE : otherwise
```
Annualised: `conditional_volatility × √252`

### DCF / Gordon Growth Model (Module 4)
```
TV  = FCF_n × (1 + g) / (WACC - g)
EV  = Σ PV(FCF_t) + PV(TV)
MoS = (Intrinsic Value - Market Price) / Intrinsic Value × 100
```

### GBM Monte Carlo (Module 5)
```
S(t+1) = S(t) × exp((μ - 0.5σ²)Δt + σ√Δt × Z),  Z ~ N(0,1)
```

### VaR Methods (Module 6)
| Method | Formula |
|--------|---------|
| Historical | 5th percentile of empirical return distribution |
| Parametric | `μ + z_{0.05} × σ` (Normal distribution) |
| Monte Carlo | 5th percentile of 10,000 simulated returns |

### Kupiec POF Test (Module 6)
```
LR = -2 × [log L(p₀) - log L(p̂)]  ~  χ²(1)
Reject H₀ (model valid) if p-value < 0.05
```

### Credit Score Mapping (Module 7)
```
Score = 850 - PD(%) × 5.5   [clipped to 300–850]
```

---

## 📦 Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.35.0 | Dashboard framework |
| yfinance | 0.2.40 | Market data (NSE/BSE) |
| pandas | 2.2.2 | Data manipulation |
| numpy | 1.26.4 | Numerical computing |
| plotly | 5.22.0 | Interactive charts |
| pmdarima | 2.0.4 | Auto ARIMA model selection |
| statsmodels | 0.14.2 | Statistical models |
| arch | 7.0.0 | GARCH volatility models |
| pypfopt | 1.5.5 | Portfolio optimisation |
| scikit-learn | 1.5.0 | Credit risk (Logistic Regression) |
| scipy | 1.13.1 | Statistical distributions, Kupiec test |
| matplotlib | 3.9.0 | Supporting plots |
| seaborn | 0.13.2 | Supporting visualisations |

---

## 🌐 Data Sources

- **Price Data**: Yahoo Finance via `yfinance` (NSE suffix `.NS`)
- **Tickers covered**: RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, WIPRO.NS
- **Gold proxy**: GOLDBEES.NS
- **Market index**: ^NSEI (Nifty 50) for beta computation
- **Bond proxy**: Simulated using RBI repo rate (6.5% p.a.)
- **Cash Flow**: yFinance `.cashflow` attribute (quarterly)

---

## 🚢 Deployment (Bonus +20 marks)

### Streamlit Cloud (recommended)
1. Push project to a **public GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → connect your repo → set `app.py` as main file
4. Click **Deploy**

### Render
1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: risk-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```
2. Push to GitHub and connect to Render

---

## ⚠️ Academic Integrity

All code in this repository is original. Any use of AI tools for code generation
has been declared here. During viva, any team member may be asked to explain
any line of code — all logic, formulas, and design choices are documented in
this README and inline in `app.py`.

**AI tool usage disclosure**: Claude (Anthropic) was used to assist in
structuring the codebase. All financial formulas, model implementations, and
logic were verified against course material and standard quantitative finance
references.

---

## 📝 Known Limitations & Future Work

1. **Cash flow data** from yFinance may be missing for some tickers — the DCF
   module falls back to a synthetic FCF with a warning.
2. **ARIMA walk-forward** trains a new model per step which is slow for large
   datasets; a production system would use rolling-window fitting.
3. **Credit model** uses a synthetic training dataset; real-world PD would
   require Altman Z-score inputs or credit bureau data.
4. **Bond proxy** is simulated at a fixed rate; could be replaced with actual
   G-Sec yield data from FRED API.
5. **Future**: Add live WebSocket price streaming, multi-currency support, and
   PDF report export.

---

*Built with ♥ for MCA Financial Analytics Capstone — May 2026*
