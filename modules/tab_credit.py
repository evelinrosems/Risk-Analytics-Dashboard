"""
tab_credit.py — Module 7: Credit Risk Modelling tab.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from .config import GREEN, RED, AMBER, PEACH, CREAM, DARK, PLOT
from .data_loader import get_ticker_info


def render(selected_ticker: str):
    st.markdown("###  Credit Risk Modelling")

    if st.button("▶️ Run Credit Risk Model", type="primary", key="btn_credit"):
        st.session_state["credit_run"] = True

    if not st.session_state.get("credit_run"):
        st.info("Click the button above to train the logistic regression credit model.")
        return

    from .models import build_credit_model

    with st.spinner("Training credit model…"):
        lr_model, scaler_cr, acc, auc, cm = build_credit_model()

    info    = get_ticker_info(selected_ticker)
    de_val  = float(info.get("debtToEquity", 1.5) or 1.5)
    de_val  = min(de_val / 100.0 if de_val > 20 else de_val, 10.0)
    cr_val  = float(info.get("currentRatio",  1.5) or 1.5)
    roe_val = float((info.get("returnOnEquity", 0.1) or 0.1) * 100)
    npm_val = float((info.get("profitMargins", 0.1)  or 0.1) * 100)
    icr_val = float(max((info.get("ebitdaMargins", 0.1) or 0.1) * 10, 0.1))

    X_pred = scaler_cr.transform([[de_val, icr_val, cr_val, roe_val, npm_val]])
    pd_pct = float(lr_model.predict_proba(X_pred)[0][1] * 100)
    credit_score = int(max(300, min(850, 850 - pd_pct * 5.5)))

    if   credit_score >= 800: grade, gc = "AAA", GREEN
    elif credit_score >= 750: grade, gc = "AA",  "#27AE60"
    elif credit_score >= 700: grade, gc = "A",   "#82E0AA"
    elif credit_score >= 650: grade, gc = "BBB", AMBER
    elif credit_score >= 600: grade, gc = "BB",  "#E59866"
    elif credit_score >= 550: grade, gc = "B",   RED
    elif credit_score >= 500: grade, gc = "CCC", "#C0392B"
    else:                     grade, gc = "D",   "#922B21"

    cr_col1, cr_col2 = st.columns(2)

    with cr_col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=credit_score,
            delta={"reference": 700},
            gauge={
                "axis": {"range": [300, 850], "tickcolor": DARK},
                "bar":  {"color": gc},
                "bgcolor": "#FFF0E8",
                "steps": [
                    {"range": [300, 500], "color": "#FFE0D0"},
                    {"range": [500, 650], "color": "#FFD5B8"},
                    {"range": [650, 800], "color": "#FFE8D5"},
                    {"range": [800, 850], "color": "#FFF5EE"},
                ],
                "threshold": {"line": {"color": DARK, "width": 3},
                              "thickness": 0.75, "value": 700},
            },
            title={"text": "Credit Score (300–850)", "font": {"color": DARK}},
            number={"font": {"color": DARK, "size": 52}},
        ))
        fig_gauge.update_layout(paper_bgcolor=CREAM, font_color=DARK,
                                height=280, margin=dict(l=30, r=30, t=60, b=30))
        st.plotly_chart(fig_gauge, use_container_width=True)
        cr1, cr2 = st.columns(2)
        cr1.metric("Prob. of Default", f"{pd_pct:.2f}%")
        cr2.metric("Credit Score",     str(credit_score))
        st.markdown(f"""
        <div style='text-align:center;padding:10px;background:{gc};
                    border-radius:10px;color:white;font-weight:700;
                    font-size:22px;margin-top:8px;'>
            Risk Grade: {grade}
        </div>""", unsafe_allow_html=True)

    with cr_col2:
        cm_df = pd.DataFrame(cm,
            index=["Actual Non-Default", "Actual Default"],
            columns=["Pred Non-Default", "Pred Default"])
        fig_cm = px.imshow(cm_df, text_auto=True,
            color_continuous_scale=["#FFF0E8", PEACH],
            title="Confusion Matrix")
        fig_cm.update_layout(**PLOT, height=280, coloraxis_showscale=False)
        st.plotly_chart(fig_cm, use_container_width=True)
        st.dataframe(pd.DataFrame({
            "Metric": ["AUC-ROC", "Accuracy", "Train Size", "Test Size"],
            "Value":  [f"{auc:.4f}", f"{acc*100:.2f}%", "400", "100"],
        }), use_container_width=True, hide_index=True)

    st.markdown("#### 15-Month PD Trend")
    pd_trend = []
    for m_i in range(15):
        fac = 1 + 0.02 * np.sin(m_i / 2) + np.random.normal(0, 0.01)
        xi  = scaler_cr.transform([[de_val*fac, icr_val/fac, cr_val,
                                    roe_val*fac, npm_val*fac]])
        pd_trend.append(float(lr_model.predict_proba(xi)[0][1] * 100))

    fig_pd = go.Figure(go.Scatter(
        x=[f"M{i+1}" for i in range(15)], y=pd_trend,
        mode="lines+markers", line=dict(color=RED, width=2),
        marker=dict(color=PEACH, size=7)))
    fig_pd.update_layout(**PLOT, title="15-Month Probability of Default Trend",
                          xaxis_title="Month", yaxis_title="PD (%)", height=260)
    st.plotly_chart(fig_pd, use_container_width=True)
