"""
app.py — Risk Analytics Dashboard entry-point.
"""

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import numpy as np

st.set_page_config(
    page_title="Risk Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

from modules.config      import RISK_FREE_RATE
from modules.data_loader import load_stock_data
from modules.ui_helpers  import render_sidebar, render_header, render_footer

(selected_ticker, start_date, end_date,
 portfolio_stocks, add_bond, add_gold) = render_sidebar()

with st.spinner("⏳ Fetching market data…"):
    data = load_stock_data(selected_ticker, str(start_date), str(end_date))

if data.empty:
    st.error("❌ No data for the selected ticker / date range.")
    st.stop()

current_price = float(data["Close"].iloc[-1])
returns       = data["Returns"].dropna()
ann_return    = float(returns.mean()) * 252 * 100
ann_vol       = float(returns.std()) * np.sqrt(252) * 100
sharpe        = (ann_return / 100 - RISK_FREE_RATE) / (ann_vol / 100 + 1e-10)
var_95_hist   = float(np.percentile(returns, 5) * 100)
var_99_hist   = float(np.percentile(returns, 1) * 100)
price_chg     = (current_price / float(data["Close"].iloc[-2]) - 1) * 100

render_header(selected_ticker, current_price, price_chg,
              start_date, end_date, len(data))

(tab_exec, tab_ar, tab_ga, tab_dc,
 tab_mc, tab_v, tab_cr, tab_pt,
 tab_st, tab_co) = st.tabs([
    "📋 Executive Summary",
    "📈 ARIMA Forecast",
    "🌊 GARCH Volatility",
    "💰 DCF Valuation",
    "🎲 Monte Carlo",
    "⚠️ Value at Risk",
    "🏦 Credit Risk",
    "🗂️ Portfolio",
    "🔥 Stress Testing",
    "🔗 Correlation",
])

# Each tab is imported and rendered only inside its own `with` block.
# Streamlit only executes the active tab's block on each rerun.

with tab_exec:
    from modules import tab_executive
    tab_executive.render(data, selected_ticker, current_price,
                         returns, ann_return, ann_vol, sharpe,
                         var_95_hist, var_99_hist, price_chg)

with tab_ar:
    from modules import tab_arima
    tab_arima.render(data, current_price)

with tab_ga:
    from modules import tab_garch
    tab_garch.render(data)

with tab_dc:
    from modules import tab_dcf
    tab_dcf.render(selected_ticker, current_price)

with tab_mc:
    from modules import tab_monte_carlo
    tab_monte_carlo.render(returns, current_price)

with tab_v:
    from modules import tab_var
    tab_var.render(returns)

with tab_cr:
    from modules import tab_credit
    tab_credit.render(selected_ticker)

with tab_pt:
    from modules import tab_portfolio
    tab_portfolio.render(portfolio_stocks, start_date, end_date, add_bond, add_gold)

with tab_st:
    from modules import tab_stress
    tab_stress.render(returns, start_date, end_date)

with tab_co:
    from modules import tab_correlation
    tab_correlation.render(portfolio_stocks, start_date, end_date, add_bond, add_gold)

render_footer()
