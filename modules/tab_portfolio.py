"""
tab_portfolio.py — Module 8: Portfolio Optimisation tab.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from .config import PEACH, PEACH_L, GREEN, AMBER, PURPLE, BLUE, RED, DARK, PLOT, RISK_FREE_RATE
from .data_loader import load_portfolio_with_bond


def render(portfolio_stocks: list, start_date, end_date,
           add_bond: bool, add_gold: bool):
    st.markdown("###  Portfolio Optimisation")

    if len(portfolio_stocks) < 2:
        st.warning("Select at least 2 assets in the sidebar.")
        return

    if st.button("▶️ Run Portfolio Optimisation (Efficient Frontier)", type="primary", key="btn_portfolio"):
        st.session_state["portfolio_run"] = True

    if not st.session_state.get("portfolio_run"):
        st.info("Click the button above to load portfolio data and compute the efficient frontier.")
        return

    with st.spinner("Fetching portfolio data…"):
        port_prices = load_portfolio_with_bond(
            portfolio_stocks, str(start_date), str(end_date), add_bond, add_gold)

    if port_prices is None or port_prices.empty:
        st.error("Could not fetch portfolio data. Check ticker symbols and date range.")
        return
    if port_prices.shape[1] < 2:
        st.error("Need at least 2 assets with data.")
        return

    log_r = np.log(port_prices / port_prices.shift(1)).dropna()
    mu_r  = log_r.mean() * 252
    cov_r = log_r.cov() * 252
    n_ass = len(port_prices.columns)

    with st.spinner("Running 5,000 portfolio simulations…"):
        np.random.seed(0)
        N   = 5000
        res = np.zeros((3, N))
        wts = np.zeros((N, n_ass))
        for i in range(N):
            w = np.random.random(n_ass); w /= w.sum()
            wts[i] = w
            ret = np.dot(w, mu_r)
            vol = np.sqrt(w @ cov_r @ w)
            res[0, i] = vol * 100
            res[1, i] = ret * 100
            res[2, i] = (ret - RISK_FREE_RATE) / (vol + 1e-10)

    best = res[2].argmax()
    opt_w, opt_ret, opt_vol, opt_sr = (
        wts[best], res[1, best], res[0, best], res[2, best])

    fig_ef = go.Figure()
    fig_ef.add_trace(go.Scatter(
        x=res[0], y=res[1], mode="markers",
        marker=dict(color=res[2], colorscale="RdYlGn",
                    size=3, opacity=0.55,
                    colorbar=dict(title="Sharpe")),
        name="Portfolios"))
    fig_ef.add_trace(go.Scatter(
        x=[opt_vol], y=[opt_ret], mode="markers+text",
        marker=dict(color=PEACH, size=18, symbol="star",
                    line=dict(color=DARK, width=1)),
        text=["Max Sharpe"], textposition="top center",
        textfont=dict(color=DARK, size=12),
        name="Max Sharpe"))
    fig_ef.update_layout(**PLOT,
        title="Efficient Frontier — 5,000 Random Portfolios",
        xaxis_title="Portfolio Volatility (%)",
        yaxis_title="Expected Return (%)", height=440)
    st.plotly_chart(fig_ef, use_container_width=True)

    pie_col, met_col = st.columns(2)
    with pie_col:
        fig_pie = go.Figure(go.Pie(
            labels=[c.replace(".NS", "") for c in port_prices.columns],
            values=opt_w, hole=0.45,
            marker_colors=[PEACH, PEACH_L, AMBER, PURPLE, GREEN, BLUE, RED]))
        fig_pie.update_layout(**PLOT, title="Optimal Allocation", height=340)
        st.plotly_chart(fig_pie, use_container_width=True)
    with met_col:
        pm1, pm2, pm3 = st.columns(3)
        pm1.metric("Expected Return",      f"{opt_ret:.2f}%")
        pm2.metric("Portfolio Volatility", f"{opt_vol:.2f}%")
        pm3.metric("Sharpe Ratio",         f"{opt_sr:.3f}")
        st.dataframe(pd.DataFrame({
            "Asset":  [c.replace(".NS", "") for c in port_prices.columns],
            "Weight": [f"{w*100:.2f}%" for w in opt_w],
        }).sort_values("Weight", ascending=False),
        use_container_width=True, hide_index=True)
