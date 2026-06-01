"""
data_loader.py — All @st.cache_data functions that fetch / prepare data.

Import from here to keep app.py free of data-fetching logic.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from io import StringIO

from .config import RISK_FREE_RATE


def _read_json_series(json_str: str) -> pd.Series:
    """Safely read a JSON string into a pandas Series (pandas >= 2.x fix)."""
    return pd.read_json(StringIO(json_str), typ="series")


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten MultiIndex columns produced by yfinance for single tickers."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


# ── Single-stock price data ───────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_stock_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if df.empty:
        return df
    df = _flatten_columns(df)
    df.index = pd.to_datetime(df.index)
    df["Returns"]     = df["Close"].pct_change()
    df["Log_Returns"] = np.log(df["Close"] / df["Close"].shift(1))
    df["Rolling_Vol"] = df["Returns"].rolling(20).std() * np.sqrt(252) * 100
    return df.dropna(subset=["Returns"])


# ── Multi-stock price matrix ──────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_portfolio_data(tickers: list, start: str, end: str) -> pd.DataFrame:
    if not tickers:
        return pd.DataFrame()
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    if raw.empty:
        return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        # Single ticker — raw itself is the OHLCV frame
        prices = raw[["Close"]]
    prices = prices.copy()
    prices.columns = [str(c).replace(".NS", "") for c in prices.columns]
    return prices.dropna()


@st.cache_data(ttl=300, show_spinner=False)
def load_portfolio_with_bond(tickers: list, start: str, end: str,
                              add_bond: bool, add_gold: bool) -> pd.DataFrame:
    tks = list(tickers)
    if add_gold and "GOLDBEES.NS" not in tks:
        tks.append("GOLDBEES.NS")
    prices = load_portfolio_data(tks, start, end)
    if prices.empty:
        return prices
    if add_bond:
        bond_ret = RISK_FREE_RATE / 252
        prices["Bond"] = [100 * (1 + bond_ret) ** i for i in range(len(prices))]
    return prices


# ── Fundamental / metadata ────────────────────────────────────

@st.cache_data(ttl=600, show_spinner=False)
def get_ticker_info(ticker: str) -> dict:
    try:
        return yf.Ticker(ticker).info or {}
    except Exception:
        return {}


@st.cache_data(ttl=600, show_spinner=False)
def get_cashflow(ticker: str) -> pd.DataFrame:
    try:
        cf = yf.Ticker(ticker).cashflow
        return cf if cf is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


# ── Beta vs Nifty ─────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def compute_beta(ret_json: str, start: str, end: str) -> float:
    rets = _read_json_series(ret_json).dropna()
    try:
        nifty_raw = yf.download("^NSEI", start=start, end=end,
                                auto_adjust=True, progress=False)
        nifty_raw = _flatten_columns(nifty_raw)
        nifty = nifty_raw["Close"]
        if isinstance(nifty, pd.DataFrame):
            nifty = nifty.iloc[:, 0]
        nifty_ret = nifty.pct_change().dropna()
        aligned = pd.concat([rets, nifty_ret], axis=1, join="inner").dropna()
        aligned.columns = ["stock", "market"]
        beta, _ = np.polyfit(aligned["market"], aligned["stock"], 1)
        return float(beta)
    except Exception:
        return 1.0
