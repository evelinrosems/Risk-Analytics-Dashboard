"""
tab_arima.py — Module 2: ARIMA Forecasting tab.
Model runs only when user clicks the button.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from .config import PEACH, AMBER, DARK, PLOT


def render(data: pd.DataFrame, current_price: float):
    st.markdown("###  ARIMA Forecasting")
    st.info("ARIMA walk-forward validation takes 1–3 minutes depending on data size.")

    if st.button("▶️ Run ARIMA Forecast (90 days)", type="primary", key="btn_arima"):
        st.session_state["arima_run"] = True

    if not st.session_state.get("arima_run"):
        return

    from .models import run_arima

    with st.spinner("Fitting ARIMA model (this may take 1–3 min)…"):
        arima_res = run_arima(data["Close"].to_json(), horizon=90)

    future_dates = pd.date_range(
        start=data.index[-1] + pd.Timedelta(days=1), periods=90, freq="B")

    forecast_vals = list(arima_res["forecast"])
    ci_arr        = arima_res["ci"]

    fig_ar = go.Figure()
    fig_ar.add_trace(go.Scatter(
        x=data.index, y=data["Close"], mode="lines",
        name="Actual Price", line=dict(color=DARK, width=2)))
    fig_ar.add_trace(go.Scatter(
        x=list(future_dates) + list(future_dates[::-1]),
        y=list(ci_arr[:, 1]) + list(ci_arr[:, 0][::-1]),
        fill="toself", fillcolor="rgba(255,107,61,0.15)",
        line=dict(color="rgba(0,0,0,0)"), name="95% CI"))
    fig_ar.add_trace(go.Scatter(
        x=future_dates, y=forecast_vals, mode="lines",
        name="ARIMA Forecast",
        line=dict(color=PEACH, width=2.5, dash="dash")))
    fig_ar.update_layout(**PLOT,
        title=f"90-Day ARIMA{arima_res['order']} Price Forecast",
        xaxis_title="Date", yaxis_title="Price (₹)", height=420)
    st.plotly_chart(fig_ar, use_container_width=True)

    fig_wf = go.Figure()
    fig_wf.add_trace(go.Scatter(
        x=arima_res["test"].index, y=arima_res["test"],
        mode="lines", name="Actual", line=dict(color=DARK, width=2)))
    fig_wf.add_trace(go.Scatter(
        x=arima_res["wf_preds"].index, y=arima_res["wf_preds"],
        mode="lines", name="Walk-Forward Prediction",
        line=dict(color=AMBER, width=2, dash="dot")))
    fig_wf.update_layout(**PLOT,
        title="Walk-Forward Validation — Out-of-Sample 20%",
        xaxis_title="Date", yaxis_title="Price (₹)", height=300)
    st.plotly_chart(fig_wf, use_container_width=True)

    direction = (" Uptrend" if forecast_vals[-1] > current_price
                 else "Downtrend")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("RMSE (Out-of-Sample)", f"{arima_res['rmse_out']:.2f}")
    m2.metric("MAE  (Out-of-Sample)", f"{arima_res['mae_out']:.2f}")
    m3.metric("MAPE (%)",             f"{arima_res['mape_out']:.2f}%")
    m4.metric("Direction",            direction)

    st.markdown("#### Model Summary")
    st.dataframe(pd.DataFrame({
        "Metric": ["Model Order", "AIC", "BIC",
                   "RMSE In-Sample", "RMSE Out-of-Sample", "In/Out Ratio"],
        "Value": [
            str(arima_res["order"]),
            f"{arima_res['aic']:.2f}", f"{arima_res['bic']:.2f}",
            f"{arima_res['rmse_in']:.2f}", f"{arima_res['rmse_out']:.2f}",
            f"{arima_res['rmse_in']/arima_res['rmse_out']:.2f}×",
        ],
    }), use_container_width=True, hide_index=True)
