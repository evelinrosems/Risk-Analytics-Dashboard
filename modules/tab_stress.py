"""
tab_stress.py — Module 9: Stress Testing & Scenario Analysis tab.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from .config import GREEN, RED, PLOT
from .data_loader import compute_beta


def render(returns: pd.Series, start_date, end_date):
    st.markdown("### Stress Testing & Scenario Analysis")

    if st.button("▶️ Run Stress Test (fetches Nifty beta)", type="primary", key="btn_stress"):
        st.session_state["stress_run"] = True

    if not st.session_state.get("stress_run"):
        st.info("Click the button above to compute market beta and run scenario analysis.")
        return

    with st.spinner("Computing market beta vs Nifty…"):
        beta_market = compute_beta(returns.to_json(), str(start_date), str(end_date))

    custom_pct = st.slider("Custom Scenario Shock (%)", -30, 30, 5, key="stress_custom")

    scenarios = {
        "Market Crash (-20%)":       -20 * beta_market,
        "Interest Rate Hike (+2%)":  -8  * beta_market,
        "Recession Scenario":        -15 * beta_market,
        "Oil Price Shock (+25%)":    -10 * beta_market,
        "Best Case Scenario (+15%)":  15 * beta_market,
        f"Custom ({custom_pct:+}%)":  custom_pct * beta_market,
    }

    sc_df = pd.DataFrame({
        "Scenario":             list(scenarios.keys()),
        "Portfolio Impact (%)": [round(v, 2) for v in scenarios.values()],
    }).sort_values("Portfolio Impact (%)")

    bar_colors = [RED if v < 0 else GREEN for v in sc_df["Portfolio Impact (%)"]]
    fig_st = go.Figure(go.Bar(
        x=sc_df["Portfolio Impact (%)"], y=sc_df["Scenario"],
        orientation="h", marker_color=bar_colors,
        text=[f"{v:+.2f}%" for v in sc_df["Portfolio Impact (%)"]],
        textposition="outside"))
    fig_st.update_layout(**PLOT, title="Portfolio Stress Test Results",
                          xaxis_title="Impact (%)", xaxis_range=[-32, 32],
                          height=380)
    st.plotly_chart(fig_st, use_container_width=True)
    st.dataframe(sc_df, use_container_width=True, hide_index=True)

    worst = sc_df.iloc[0]
    best  = sc_df.iloc[-1]
    st.markdown(f"""
    #### 📝 Risk Interpretation
    - **Highest-risk scenario**: *{worst['Scenario']}* → projected impact
      **{worst['Portfolio Impact (%)']:.2f}%** (β = {beta_market:.2f})
    - **Primary exposure**: Market beta risk — a 1% market move implies
      **{beta_market:.2f}%** stock move
    - **Recommended hedge**: Nifty put options or 10–15% allocation to
      Gold / Bonds to dampen directional beta
    - **Best upside**: *{best['Scenario']}* → **+{best['Portfolio Impact (%)']:.2f}%**
    """)

    ss1, ss2 = st.columns(2)
    with ss1:
        st.markdown(f"""
        <div style='background:{RED};padding:20px;border-radius:14px;color:white;'>
            <b>⚠️ Highest Risk</b><br>
            {worst['Scenario']}<br>
            <span style='font-size:28px;font-weight:700;'>
                {worst['Portfolio Impact (%)']:.2f}%
            </span>
        </div>""", unsafe_allow_html=True)
    with ss2:
        st.markdown(f"""
        <div style='background:{GREEN};padding:20px;border-radius:14px;color:white;'>
            <b>✅ Best Case</b><br>
            {best['Scenario']}<br>
            <span style='font-size:28px;font-weight:700;'>
                +{best['Portfolio Impact (%)']:.2f}%
            </span>
        </div>""", unsafe_allow_html=True)
