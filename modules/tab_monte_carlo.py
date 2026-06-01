"""
tab_monte_carlo.py — Module 5: Monte Carlo Simulation tab.
"""

import time
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from .config import PEACH, RED, GREEN, DARK, PLOT


def render(returns: pd.Series, current_price: float):
    st.markdown("###  Monte Carlo Simulation")

    mc_c1, mc_c2 = st.columns(2)
    with mc_c1:
        num_sims = st.slider("Number of Simulations", 500, 5000, 1000,
                             step=500, key="mc_nsims")
    with mc_c2:
        time_horizon = st.slider("Time Horizon (trading days)", 63, 252, 252,
                                 step=21, key="mc_th")

    if st.button("▶️ Run Monte Carlo Simulation", type="primary", key="btn_mc"):
        st.session_state["mc_run"] = True

    if not st.session_state.get("mc_run"):
        st.info("Adjust the sliders above, then click the button to run the simulation.")
        return

    from .models import run_monte_carlo

    t0 = time.time()
    with st.spinner(f"Running {num_sims:,} simulations…"):
        sims = run_monte_carlo(float(returns.mean()), float(returns.std()),
                               current_price, num_sims, time_horizon)
    elapsed = time.time() - t0

    final = sims[-1]
    p5    = np.percentile(final, 5)
    p95   = np.percentile(final, 95)

    fig_mc = go.Figure()
    idx_all  = list(range(time_horizon + 1))
    bot_mask = final < p5
    top_mask = final > p95

    for i in np.where(bot_mask)[0][:60]:
        fig_mc.add_trace(go.Scatter(x=idx_all, y=sims[:, i], mode="lines",
            line=dict(color="rgba(231,76,60,0.25)", width=0.7),
            showlegend=False))
    for i in np.where(top_mask)[0][:60]:
        fig_mc.add_trace(go.Scatter(x=idx_all, y=sims[:, i], mode="lines",
            line=dict(color="rgba(46,204,113,0.25)", width=0.7),
            showlegend=False))
    for i in np.where(~bot_mask & ~top_mask)[0][:200]:
        fig_mc.add_trace(go.Scatter(x=idx_all, y=sims[:, i], mode="lines",
            line=dict(color="rgba(255,107,61,0.07)", width=0.5),
            showlegend=False))
    fig_mc.add_trace(go.Scatter(
        x=idx_all, y=np.median(sims, axis=1), mode="lines",
        name="Median Path", line=dict(color=DARK, width=2.5)))

    fig_mc.update_layout(**PLOT,
        title=f"Monte Carlo GBM — {num_sims:,} Paths · {time_horizon} Days",
        xaxis_title="Trading Days", yaxis_title="Price (₹)", height=450)
    st.plotly_chart(fig_mc, use_container_width=True)
    st.caption(f"⏱ Computation: {elapsed:.2f} s")

    prob_up   = float(np.mean(final > current_price * 1.10) * 100)
    prob_down = float(np.mean(final < current_price * 0.90) * 100)

    st.markdown("#### 1-Year Probability Summary")
    st.dataframe(pd.DataFrame({
        "Metric": ["Expected Price", "Median Price", "Best Case (95th)", "Worst Case (5th)",
                   "Prob(Price > +10%)", "Prob(Price < -10%)"],
        "Value":  [f"₹{np.mean(final):,.2f}", f"₹{np.median(final):,.2f}",
                   f"₹{p95:,.2f}", f"₹{p5:,.2f}",
                   f"{prob_up:.2f}%", f"{prob_down:.2f}%"],
    }), use_container_width=True, hide_index=True)

    pr1, pr2, pr3 = st.columns(3)
    pr1.metric("Expected Price",  f"₹{np.mean(final):,.2f}")
    pr2.metric("Prob(+10% Gain)", f"{prob_up:.1f}%")
    pr3.metric("Prob(-10% Loss)", f"{prob_down:.1f}%")
