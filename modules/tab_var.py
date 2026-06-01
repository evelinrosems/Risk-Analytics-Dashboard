"""
tab_var.py — Module 6: Value at Risk (VaR) Analysis tab.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

from .config import PEACH_L, RED, AMBER, PLOT


def render(returns: pd.Series):
    st.markdown("###  Value at Risk (VaR) Analysis")

    if st.button("▶️ Compute VaR (3 Methods)", type="primary", key="btn_var"):
        st.session_state["var_run"] = True

    if not st.session_state.get("var_run"):
        st.info("Click the button above to compute Historical, Parametric, and Monte Carlo VaR.")
        return

    from .models import compute_var_all

    with st.spinner("Computing VaR (3 methods)…"):
        h95, h99, p95, p99, m95, m99, cvar_val, mc_pnl = compute_var_all(
            returns.to_json(), n_paths=10000)

    st.dataframe(pd.DataFrame({
        "Method":        ["Historical", "Historical", "Parametric Normal",
                          "Parametric Normal", "Monte Carlo", "Monte Carlo"],
        "Confidence":    ["95%", "99%", "95%", "99%", "95%", "99%"],
        "VaR (1-Day %)": [f"{v:.4f}%" for v in [h95, h99, p95, p99, m95, m99]],
    }), use_container_width=True, hide_index=True)

    st.markdown(f"""
    <div style='background:#FFF0E8;border:2px solid {RED};border-radius:10px;
                padding:16px;margin:12px 0;'>
        <span style='color:{RED};font-weight:700;font-size:15px;'>
            Expected Shortfall (CVaR) @ 95%: {cvar_val:.4f}%
        </span><br>
        <span style='color:#7A4030;font-size:12px;'>
            CVaR is the mean loss beyond the VaR threshold — it captures true
            tail risk and is always larger in magnitude than VaR.
        </span>
    </div>""", unsafe_allow_html=True)

    fig_ld = go.Figure()
    fig_ld.add_trace(go.Histogram(x=mc_pnl, nbinsx=100,
        marker_color=PEACH_L, opacity=0.8, name="Monte Carlo P&L"))
    tail_x = mc_pnl[mc_pnl <= m95]
    if len(tail_x) > 0:
        hv, be = np.histogram(tail_x, bins=50)
        fig_ld.add_trace(go.Bar(
            x=(be[:-1]+be[1:])/2, y=hv, width=np.diff(be),
            marker_color=RED, opacity=0.9, name="Tail Loss (beyond VaR 95%)"))
    # add_vline broken in Plotly 6 — use shapes instead
    fig_ld.add_shape(type="line", x0=m95, x1=m95, y0=0, y1=1,
                     yref="paper", line=dict(color=RED, dash="dash", width=2))
    fig_ld.add_annotation(x=m95, y=1, yref="paper", text=f"VaR 95%={m95:.2f}%",
                          showarrow=False, font=dict(color=RED), xanchor="left")
    fig_ld.add_shape(type="line", x0=m99, x1=m99, y0=0, y1=1,
                     yref="paper", line=dict(color=AMBER, dash="dash", width=2))
    fig_ld.add_annotation(x=m99, y=0.9, yref="paper", text=f"VaR 99%={m99:.2f}%",
                          showarrow=False, font=dict(color=AMBER), xanchor="left")
    fig_ld.update_layout(**PLOT, title="Loss Distribution (10,000 MC paths)",
                          xaxis_title="1-Day Return (%)",
                          yaxis_title="Frequency", height=360)
    st.plotly_chart(fig_ld, use_container_width=True)

    # Kupiec POF backtesting
    st.markdown("#### Kupiec Proportion of Failures (POF) Backtesting")
    window  = min(252, len(returns))
    recent  = returns.tail(window)
    thr_k   = float(np.percentile(returns, 5))
    exc     = int((recent < thr_k).sum())
    exp_exc = window * 0.05

    if exc == 0:
        pval = 1.0
    else:
        ph = exc / window
        lr_stat = -2 * (
            np.log((0.95)**(window-exc) * 0.05**exc) -
            np.log((1-ph)**(window-exc) * (ph+1e-300)**exc)
        )
        pval = float(1 - stats.chi2.cdf(lr_stat, df=1))

    verdict = "✅ Model Valid" if pval >= 0.05 else "❌ Model Invalid"
    st.dataframe(pd.DataFrame({
        "Metric": ["Exceptions", "Expected Exceptions", "p-value", "Verdict"],
        "Value":  [str(exc), f"{exp_exc:.1f}", f"{pval:.4f}", verdict],
    }), use_container_width=True, hide_index=True)

    kv1, kv2, kv3, kv4 = st.columns(4)
    kv1.metric("Historical VaR 95%",  f"{h95:.4f}%")
    kv2.metric("Parametric VaR 95%",  f"{p95:.4f}%")
    kv3.metric("Monte Carlo VaR 95%", f"{m95:.4f}%")
    kv4.metric("CVaR 95%",            f"{cvar_val:.4f}%")
