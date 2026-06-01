"""
ui_helpers.py — Reusable Streamlit / Plotly UI components.

Nothing here fetches data or runs models; it only renders.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime

from .config import (
    TICKERS, PEACH, PEACH_L, GREEN, RED, AMBER, BLUE, PURPLE,
    CREAM, DARK, PLOT,
)


# ── Sidebar ───────────────────────────────────────────────────

def render_sidebar():
    """Render sidebar controls and return selected values."""
    with st.sidebar:
        st.markdown("""
        <div style='padding:16px 0 8px;'>
            <div style='color:#FF6B3D;font-size:11px;font-weight:700;
                        letter-spacing:0.12em;text-transform:uppercase;'>
                MCA · Capstone Project
            </div>
            <div style='color:#3D1F0A;font-size:20px;font-weight:700;
                        line-height:1.2;margin-top:4px;'>
                Risk Analytics<br>Dashboard
            </div>
            <div style='color:#A0614A;font-size:11px;margin-top:4px;'>
                yFinance · Plotly · Streamlit
            </div>
        </div>
        <hr style='border-color:#FFD0BB;margin:10px 0;'>
        """, unsafe_allow_html=True)

        selected_ticker = st.selectbox(
            "Select Stock",
            list(TICKERS.keys()),
            format_func=lambda x: f"{x} — {TICKERS[x]}",
        )

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("From",
                datetime.date.today() - datetime.timedelta(days=730))
        with col_d2:
            end_date = st.date_input("To", datetime.date.today())

        st.markdown("<hr style='border-color:#FFD0BB;margin:10px 0;'>",
                    unsafe_allow_html=True)

        portfolio_stocks = st.multiselect(
            "Portfolio Assets",
            list(TICKERS.keys()),
            default=list(TICKERS.keys()),
        )
        if len(portfolio_stocks) < 2:
            st.warning("Select ≥ 2 assets for portfolio modules.")

        add_bond = st.checkbox("Include Bond (proxy)", value=True)
        add_gold = st.checkbox("Include Gold (GOLDBEES.NS)", value=True)

        st.markdown("<hr style='border-color:#FFD0BB;margin:10px 0;'>",
                    unsafe_allow_html=True)
        st.caption("All data: Yahoo Finance / NSE")

    return selected_ticker, start_date, end_date, portfolio_stocks, add_bond, add_gold


# ── Page header ───────────────────────────────────────────────

def render_header(selected_ticker, current_price, price_chg,
                  start_date, end_date, n_days):
    chg_color = GREEN if price_chg >= 0 else RED
    chg_arrow = "▲" if price_chg >= 0 else "▼"
    st.markdown(f"""
<div style='background:linear-gradient(135deg,#FFF0E8 0%,#FFE4D4 100%);
            border:2px solid #FFD0BB;border-radius:16px;
            padding:20px 28px;margin-bottom:20px;
            display:flex;align-items:center;justify-content:space-between;
            box-shadow:0 4px 20px rgba(255,107,61,0.1);'>
    <div>
        <div style='color:#FF6B3D;font-size:11px;font-weight:700;
                    letter-spacing:0.12em;text-transform:uppercase;'>
            Risk Analytics Dashboard · MCA Capstone
        </div>
        <div style='color:#3D1F0A;font-size:26px;font-weight:700;
                    margin:4px 0 2px;line-height:1.2;'>
            {selected_ticker} &nbsp;·&nbsp; {TICKERS.get(selected_ticker,'')}
        </div>
        <div style='color:#A0614A;font-size:13px;'>
            {start_date.strftime('%d %b %Y')} → {end_date.strftime('%d %b %Y')}
            &nbsp;·&nbsp; {n_days} trading days
        </div>
    </div>
    <div style='text-align:right;'>
        <div style='color:#A0614A;font-size:11px;text-transform:uppercase;
                    letter-spacing:0.08em;'>Last Close</div>
        <div style='color:#3D1F0A;font-size:34px;font-weight:700;
                    font-family:Space Mono,monospace;'>
            ₹{current_price:,.2f}
        </div>
        <div style='color:{chg_color};font-size:14px;font-weight:700;'>
            {chg_arrow} {abs(price_chg):.2f}% (1D)
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Sparkline ─────────────────────────────────────────────────

def sparkline(series: pd.Series, color: str) -> go.Figure:
    # Convert hex color to rgba for Plotly 6.x compatibility
    def hex_to_rgba(hex_color, alpha=0.13):
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    fig = go.Figure(go.Scatter(
        x=list(range(len(series))), y=series.values,
        mode="lines", line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=hex_to_rgba(color),
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        height=55, showlegend=False,
    )
    return fig


# ── KPI card ──────────────────────────────────────────────────

def kpi_card(col, title, value, sub, sub_color, spark_series, spark_color, key):
    with col:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#FFF8F5,#FFF0E8);
                    border:1.5px solid #FFD0BB;border-radius:14px;
                    padding:16px;min-height:110px;
                    box-shadow:0 2px 12px rgba(255,107,61,0.08);'>
            <div style='color:#A0614A;font-size:10px;font-weight:700;
                        text-transform:uppercase;letter-spacing:0.08em;'>
                {title}
            </div>
            <div style='color:#3D1F0A;font-size:24px;font-weight:700;
                        font-family:Space Mono,monospace;margin:6px 0 2px;'>
                {value}
            </div>
            <div style='color:{sub_color};font-size:12px;font-weight:600;'>
                {sub}
            </div>
        </div>""", unsafe_allow_html=True)
        st.plotly_chart(sparkline(spark_series, spark_color),
                        use_container_width=True, key=key)


# ── Footer ────────────────────────────────────────────────────

def render_footer():
    st.markdown("---")
    st.markdown(f"""
<div style='text-align:center;padding:16px 0;color:#A0614A;font-size:12px;'>
    <strong style='color:{PEACH};'>Risk Analytics Dashboard</strong> ·
    MCA Financial Analytics Capstone Project ·
    Built with Python, Streamlit, Plotly, yFinance ·
    NSE / Yahoo Finance data
</div>
""", unsafe_allow_html=True)
