"""
config.py — App-wide constants, Plotly theme, and ticker registry.
"""

# ── Risk-free rate ────────────────────────────────────────────
RISK_FREE_RATE = 0.065

# ── Tracked stocks ───────────────────────────────────────────
TICKERS = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS":      "Tata Consultancy Services",
    "INFY.NS":     "Infosys",
    "HDFCBANK.NS": "HDFC Bank",
    "WIPRO.NS":    "Wipro",
}

# ── Colour palette ───────────────────────────────────────────
PEACH   = "#FF6B3D"
PEACH_L = "#FFB899"
GREEN   = "#2ECC71"
RED     = "#E74C3C"
AMBER   = "#E67E22"
BLUE    = "#2980B9"
PURPLE  = "#8E44AD"
CREAM   = "#FFF8F5"
DARK    = "#3D1F0A"

# ── Default Plotly layout dict (spread with **PLOT) ───────────
PLOT = dict(
    template="plotly_white",
    paper_bgcolor="#FFF8F5",
    plot_bgcolor="#FFF8F5",
    font=dict(color="#3D1F0A", family="DM Sans"),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(bgcolor="rgba(255,240,232,0.8)", bordercolor="#FFD0BB",
                borderwidth=1),
    xaxis=dict(gridcolor="#FFE8DC", zerolinecolor="#FFD0BB"),
    yaxis=dict(gridcolor="#FFE8DC", zerolinecolor="#FFD0BB"),
    title_font=dict(size=15, color="#3D1F0A"),
)
