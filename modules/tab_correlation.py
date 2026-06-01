"""
tab_correlation.py — Module 10: Correlation Heatmap tab.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

from .config import GREEN, RED, BLUE, PLOT
from .data_loader import load_portfolio_with_bond


def render(portfolio_stocks: list, start_date, end_date,
           add_bond: bool, add_gold: bool):
    st.markdown("### 🔗 Correlation Heatmap")

    if len(portfolio_stocks) < 2:
        st.warning("Select at least 2 assets for the heatmap.")
        return

    if st.button("▶️ Compute Correlation Matrix", type="primary", key="btn_corr"):
        st.session_state["corr_run"] = True

    if not st.session_state.get("corr_run"):
        st.info("Click the button above to compute the correlation matrix.")
        return

    with st.spinner("Fetching data and computing correlations…"):
        hm_prices = load_portfolio_with_bond(
            portfolio_stocks, str(start_date), str(end_date), add_bond, add_gold)

    if hm_prices is None or hm_prices.empty:
        st.error("Could not fetch data. Check ticker symbols and date range.")
        return

    log_r_hm = np.log(hm_prices / hm_prices.shift(1)).dropna()
    corr = log_r_hm.corr().round(2)

    ann = corr.copy().astype(str)
    for r in corr.index:
        for c in corr.columns:
            v = corr.loc[r, c]
            ann.loc[r, c] = f"{v:.2f}" + (" ⚠" if r != c and abs(v) > 0.70 else "")

    fig_hm = go.Figure(go.Heatmap(
        z=corr.values,
        x=[c.replace(".NS", "") for c in corr.columns],
        y=[c.replace(".NS", "") for c in corr.index],
        text=ann.values, texttemplate="%{text}",
        colorscale=[[0, BLUE], [0.5, "#FFF8F5"], [1, RED]],
        zmid=0, zmin=-1, zmax=1,
        colorbar=dict(title="Correlation")))
    fig_hm.update_layout(**PLOT,
        title="Correlation Matrix — Log Returns (⚠ = |r| > 0.70)",
        height=480)
    st.plotly_chart(fig_hm, use_container_width=True)

    mask = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    uns  = mask.unstack().dropna()
    if len(uns) > 0:
        lo = uns.idxmin(); hi = uns.idxmax()
        st.markdown(f"""
        <div style='background:#FFF0E8;border:1.5px solid #FFD0BB;
                    border-radius:12px;padding:16px;margin-top:12px;'>
            <div style='color:{GREEN};font-weight:700;font-size:14px;'>
                ✅ Most Diversifying Pair:
                <b>{str(lo[0]).replace('.NS','')} &amp;
                {str(lo[1]).replace('.NS','')}</b>
                — Correlation: {uns.min():.2f}
            </div>
            <div style='color:{RED};font-weight:700;font-size:14px;
                        margin-top:8px;'>
                ⚠️ Most Redundant Pair:
                <b>{str(hi[0]).replace('.NS','')} &amp;
                {str(hi[1]).replace('.NS','')}</b>
                — Correlation: {uns.max():.2f}
            </div>
        </div>""", unsafe_allow_html=True)
