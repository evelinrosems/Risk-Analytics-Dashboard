"""
tab_garch.py — Module 3: GARCH Volatility Modelling tab.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from .config import PEACH, RED, GREEN, AMBER, DARK, PLOT


def render(data: pd.DataFrame):
    st.markdown("###  GARCH Volatility Modelling")

    if st.button("▶️ Fit GARCH(1,1) Model", type="primary", key="btn_garch"):
        st.session_state["garch_run"] = True

    if not st.session_state.get("garch_run"):
        st.info("Click the button above to fit the GARCH model.")
        return

    from .models import run_garch

    with st.spinner("Fitting GARCH(1,1)…"):
        cond_vol, roll_vol, garch_params = run_garch(data["Log_Returns"].to_json())

    cur_vol  = float(cond_vol.iloc[-1])
    lt_avg   = float(cond_vol.mean())
    p75, p25 = cond_vol.quantile(0.75), cond_vol.quantile(0.25)
    spike_idx = cond_vol.idxmax()
    spike_val = float(cond_vol.max())

    if cur_vol > p75:
        regime, reg_color = "HIGH",     RED
    elif cur_vol < p25:
        regime, reg_color = "LOW",      GREEN
    else:
        regime, reg_color = "MODERATE", AMBER

    fig_g = go.Figure()
    fig_g.add_trace(go.Scatter(
        x=cond_vol.index, y=cond_vol, mode="lines",
        name="Conditional Volatility (GARCH)",
        line=dict(color=PEACH, width=2)))
    fig_g.add_trace(go.Scatter(
        x=roll_vol.dropna().index, y=roll_vol.dropna(), mode="lines",
        name="20-Day Rolling Volatility",
        line=dict(color=DARK, width=1.5, dash="dot")))
    # add_vline is broken in Plotly 6 on date axes — use scatter trace instead
    fig_g.add_trace(go.Scatter(
        x=[str(spike_idx), str(spike_idx)],
        y=[float(cond_vol.min()), float(cond_vol.max())],
        mode="lines+text",
        line=dict(color=RED, width=2, dash="dash"),
        text=["", f"Spike: {spike_val:.1f}%"],
        textposition="top center",
        textfont=dict(color=RED, size=11),
        showlegend=False, name="Spike"))
    fig_g.update_layout(**PLOT,
        title="GARCH(1,1) Conditional vs 20-Day Rolling Volatility",
        xaxis_title="Date", yaxis_title="Annualised Volatility (%)", height=420)
    st.plotly_chart(fig_g, use_container_width=True)

    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Current Volatility", f"{cur_vol:.2f}%")
    g2.metric("Long-Term Average",  f"{lt_avg:.2f}%")
    g3.metric("Last Spike Date",    str(spike_idx.date()))
    with g4:
        st.markdown(f"""
        <div style='text-align:center;padding:8px;'>
            <div style='color:#A0614A;font-size:11px;font-weight:700;
                        text-transform:uppercase;'>Volatility Regime</div>
            <div style='background:{reg_color};padding:10px 20px;border-radius:10px;
                        color:white;font-weight:700;font-size:18px;margin-top:8px;'>
                {regime}
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("#### GARCH Parameters")
    st.dataframe(pd.DataFrame({
        "Parameter": garch_params.index,
        "Value": [f"{v:.6f}" for v in garch_params.values],
    }), use_container_width=True, hide_index=True)
