"""
tab_dcf.py — Module 4: DCF Valuation tab.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from .config import GREEN, RED, AMBER, BLUE, PURPLE, CREAM, PLOT
from .data_loader import get_cashflow


def render(selected_ticker: str, current_price: float):
    st.markdown("###  DCF Valuation Model")

    sl_col, chart_col = st.columns([1, 2])
    with sl_col:
        forecast_years  = st.slider("Forecast Period (Years)", 1, 10, 5, key="dcf_fy")
        wacc_pct        = st.slider("WACC (%)", 5, 25, 10, key="dcf_wacc")
        term_growth_pct = st.slider("Terminal Growth Rate (%)", 1, 5, 3, key="dcf_tg")
        growth_rate_pct = st.slider("FCF Growth Rate (%)", 1, 20, 10, key="dcf_gr")

    wacc = wacc_pct / 100
    g    = term_growth_pct / 100
    gr   = growth_rate_pct / 100

    cashflow = get_cashflow(selected_ticker)
    base_fcf = 0
    if not cashflow.empty:
        try:
            fcf_rows = [r for r in ["Free Cash Flow", "Operating Cash Flow"]
                        if r in cashflow.index]
            if fcf_rows:
                base_fcf = abs(float(cashflow.loc[fcf_rows[0]].iloc[0]))
        except Exception:
            base_fcf = 0

    if base_fcf <= 0:
        st.warning("Cash flow data unavailable — using synthetic FCF = ₹50,000 Cr.")
        base_fcf = 5_000_000_000_00

    proj    = [base_fcf * (1 + gr) ** y for y in range(1, forecast_years + 1)]
    disc    = [fcf / (1 + wacc) ** y for y, fcf in enumerate(proj, 1)]
    tv      = proj[-1] * (1 + g) / (wacc - g)
    disc_tv = tv / (1 + wacc) ** forecast_years
    ev      = sum(disc) + disc_tv
    mos     = (ev - current_price) / ev * 100 if ev > 0 else 0.0

    val_status = ("UNDERVALUED" if mos > 15 else
                  "FAIRLY VALUED" if mos >= 0 else "OVERVALUED")
    val_color  = GREEN if mos > 15 else AMBER if mos >= 0 else RED

    with chart_col:
        x_labs = [f"Year {i}" for i in range(1, forecast_years + 1)] + \
                 ["Terminal Value", "Total Value"]
        y_vals = disc + [disc_tv, ev]
        bar_colors = [GREEN] * forecast_years + [BLUE, PURPLE]

        fig_dcf = go.Figure(go.Bar(
            x=x_labs, y=y_vals, marker_color=bar_colors,
            text=[f"₹{v/1e7:.0f}Cr" for v in y_vals],
            textposition="outside"))
        fig_dcf.update_layout(**PLOT,
            title="DCF Waterfall — Discounted Cash Flow Projection",
            xaxis_title="Period", yaxis_title="Value (₹)", height=380)
        st.plotly_chart(fig_dcf, use_container_width=True)

    rows = (
        [("Base FCF (₹ Cr)", f"₹{base_fcf/1e7:,.0f} Cr")]
        + [(f"PV Year {i}", f"₹{v/1e7:,.0f} Cr") for i, v in enumerate(disc, 1)]
        + [
            ("Terminal Value",        f"₹{tv/1e7:,.0f} Cr"),
            ("PV of Terminal Value",  f"₹{disc_tv/1e7:,.0f} Cr"),
            ("Enterprise Value",      f"₹{ev:,.0f}"),
            ("Market Price",          f"₹{current_price:,.2f}"),
            ("Margin of Safety",      f"{mos:.2f}%"),
            ("Valuation Status",      val_status),
        ]
    )
    st.dataframe(pd.DataFrame(rows, columns=["Particulars", "Value (INR)"]),
                 use_container_width=True, hide_index=True)

    d1, d2, d3 = st.columns(3)
    d1.metric("Enterprise Value", f"₹{ev:,.0f}")
    d2.metric("Margin of Safety", f"{mos:.2f}%")
    with d3:
        st.markdown(f"""
        <div style='padding:16px;background:{val_color};border-radius:12px;
                    text-align:center;color:white;font-weight:700;font-size:18px;'>
            {val_status}
        </div>""", unsafe_allow_html=True)
