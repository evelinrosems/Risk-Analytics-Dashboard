"""
tab_executive.py — Module 1: Executive Summary tab.
Heavy models are computed lazily (only when tab is active).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

from .config import GREEN, RED, AMBER, BLUE, PURPLE, PEACH, DARK, PLOT
from .ui_helpers import kpi_card


def render(data: pd.DataFrame, selected_ticker: str,
           current_price: float, returns: pd.Series,
           ann_return: float, ann_vol: float,
           sharpe: float, var_95_hist: float, var_99_hist: float,
           price_chg: float):

    st.markdown("###  Executive Summary Panel")

    # ── KPI row 2 (instant — no models needed) ───────────────
    st.markdown("####  Live Risk Metrics")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Expected Return (1Y)",  f"{ann_return:.2f}%")
    k2.metric("Portfolio Risk (σ)",    f"{ann_vol:.2f}%")
    k3.metric("VaR 95% (1D)",          f"{var_95_hist:.2f}%")
    k4.metric("VaR 99% (1D)",          f"{var_99_hist:.2f}%")
    k5.metric("Prob. of Default",      "—")
    k6.metric("Sharpe Ratio (1Y)",     f"{sharpe:.2f}")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Lazy-load heavy models behind a button ────────────────
    if st.button(" Compute ARIMA Forecast, DCF & Credit Score", type="primary"):
        st.session_state["exec_computed"] = True

    if st.session_state.get("exec_computed"):
        _render_heavy(data, selected_ticker, current_price, returns,
                      ann_return, ann_vol, sharpe, var_95_hist, var_99_hist,
                      price_chg)
    else:
        st.info("Click the button above to compute ARIMA forecast, DCF intrinsic value, and investment signal (takes ~30–60 s).")

        # Show instant bar chart of key metrics while waiting
        cats   = ["Ann. Return", "Ann. Volatility", "Sharpe × 10", "VaR 95% (abs)"]
        vals   = [ann_return, ann_vol, sharpe * 10, abs(var_95_hist)]
        colors = [PEACH, PURPLE, GREEN, RED]
        fig_kpi = go.Figure(go.Bar(
            x=cats, y=vals, marker_color=colors,
            text=[f"{v:.2f}" for v in vals], textposition="outside"))
        fig_kpi.update_layout(**PLOT, title="Key Metrics Overview",
                              height=260, showlegend=False)
        st.plotly_chart(fig_kpi, use_container_width=True)


def _render_heavy(data, selected_ticker, current_price, returns,
                  ann_return, ann_vol, sharpe, var_95_hist, var_99_hist,
                  price_chg):
    from .models import quick_arima_forecast, quick_dcf, compute_pd_model

    with st.spinner("Computing ARIMA forecast…"):
        forecasted_price = quick_arima_forecast(data["Close"].to_json(), steps=5)
    with st.spinner("Computing DCF valuation…"):
        dcf_intrinsic = quick_dcf(selected_ticker)
    with st.spinner("Computing probability of default…"):
        pd_value = compute_pd_model(selected_ticker)

    margin_of_safety = (
        (dcf_intrinsic - current_price) / dcf_intrinsic * 100
        if dcf_intrinsic > 0 else 0.0
    )

    if margin_of_safety > 20 and var_95_hist > -5:
        signal, sig_color, sig_bg = "BUY",  GREEN, "#e8f8f0"
    elif margin_of_safety >= 5:
        signal, sig_color, sig_bg = "HOLD", AMBER, "#fef6e8"
    else:
        signal, sig_color, sig_bg = "SELL", RED,   "#fdecea"

    var_pct = stats.percentileofscore(returns * 100, var_95_hist)
    if var_pct < 25:
        risk_level, rl_color = "LOW",    GREEN
    elif var_pct < 75:
        risk_level, rl_color = "MEDIUM", AMBER
    else:
        risk_level, rl_color = "HIGH",   RED

    close_tail = data["Close"].tail(30)
    fc_chg     = (forecasted_price / current_price - 1) * 100
    mos_label  = ("UNDERVALUED" if margin_of_safety > 15
                  else "FAIRLY VALUED" if margin_of_safety >= 0
                  else "OVERVALUED")
    mos_color  = GREEN if margin_of_safety > 15 else AMBER if margin_of_safety >= 0 else RED

    c1, c2, c3 = st.columns(3)
    kpi_card(c1, "Current Price",
             f"₹{current_price:,.2f}",
             f"{'▲' if price_chg>=0 else '▼'} {abs(price_chg):.2f}% (1D)",
             GREEN if price_chg >= 0 else RED,
             close_tail, PEACH, "spark1")
    kpi_card(c2, "ARIMA Forecast (5D)",
             f"₹{forecasted_price:,.2f}",
             f"{'▲' if fc_chg>=0 else '▼'} {abs(fc_chg):.2f}% vs current",
             GREEN if fc_chg >= 0 else RED,
             pd.Series([current_price*(1+fc_chg/100*i/29) for i in range(30)]),
             PURPLE, "spark2")
    kpi_card(c3, "DCF Intrinsic Value",
             f"₹{dcf_intrinsic:,.0f}" if dcf_intrinsic > 0 else "N/A",
             f"{mos_label} · MoS {margin_of_safety:.1f}%",
             mos_color, close_tail, BLUE, "spark3")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Update PD metric
    st.markdown(f"**Probability of Default:** `{pd_value:.2f}%`")

    s1, s2 = st.columns([1, 3])
    with s1:
        st.markdown(f"""
        <div style='text-align:center;padding:16px;'>
            <div style='color:#A0614A;font-size:11px;font-weight:700;
                        text-transform:uppercase;letter-spacing:0.08em;
                        margin-bottom:10px;'>Investment Signal</div>
            <div style='background:{sig_bg};border:3px solid {sig_color};
                        border-radius:14px;padding:20px 30px;
                        color:{sig_color};font-size:34px;font-weight:700;
                        font-family:Space Mono,monospace;'>
                {signal}
            </div>
            <div style='margin-top:14px;'>
                <div style='color:#A0614A;font-size:11px;font-weight:700;
                            text-transform:uppercase;margin-bottom:6px;'>
                    Risk Level
                </div>
                <div style='background:{rl_color};border-radius:20px;
                            color:white;font-weight:700;font-size:15px;
                            padding:8px 22px;display:inline-block;'>
                    {risk_level}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with s2:
        logic_df = pd.DataFrame([
            ["Margin of Safety",
             f"{margin_of_safety:.2f}%",
             ">20% for BUY / 5–20% HOLD",
             "✅" if margin_of_safety > 20 else "⚠️" if margin_of_safety > 5 else "❌"],
            ["VaR 95% (1D)",
             f"{var_95_hist:.2f}%",
             ">-5% for BUY",
             "✅" if var_95_hist > -5 else "❌"],
            ["Signal", signal,
             "BUY: MoS>20% AND VaR>-5%; HOLD: MoS 5–20%; else SELL", "—"],
        ], columns=["Metric", "Value", "Threshold", "Status"])
        st.dataframe(logic_df, use_container_width=True, hide_index=True)

        cats   = ["Ann. Return", "Ann. Volatility", "Sharpe × 10", "VaR 95% (abs)"]
        vals   = [ann_return, ann_vol, sharpe*10, abs(var_95_hist)]
        colors = [PEACH, PURPLE, GREEN, RED]
        fig_kpi = go.Figure(go.Bar(
            x=cats, y=vals, marker_color=colors,
            text=[f"{v:.2f}" for v in vals], textposition="outside"))
        fig_kpi.update_layout(**PLOT, title="Key Metrics Overview",
                              height=240, showlegend=False)
        st.plotly_chart(fig_kpi, use_container_width=True)
