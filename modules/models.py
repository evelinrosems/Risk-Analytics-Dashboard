"""
models.py — All quantitative / ML model functions.

Each function is pure (no Streamlit calls) and @st.cache_data decorated
so results are cached across reruns.
"""

import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
from pmdarima import auto_arima
from arch import arch_model

from .data_loader import get_ticker_info, get_cashflow


def _read_json_series(json_str: str) -> pd.Series:
    """Safely read a JSON string into a pandas Series (pandas >= 2.x fix)."""
    return pd.read_json(StringIO(json_str), typ="series")


# ── Quick helpers used by Executive Summary ───────────────────

@st.cache_data(ttl=300, show_spinner=False)
def quick_arima_forecast(close_json: str, steps: int = 5) -> float:
    close = _read_json_series(close_json).sort_index()
    try:
        m = auto_arima(close, seasonal=False, stepwise=True,
                       suppress_warnings=True, error_action="ignore",
                       max_p=3, max_q=3, max_d=2)
        return float(list(m.predict(n_periods=steps))[-1])
    except Exception:
        return float(close.iloc[-1])


@st.cache_data(ttl=600, show_spinner=False)
def quick_dcf(ticker: str, wacc: float = 0.10, g: float = 0.03) -> float:
    cf = get_cashflow(ticker)
    if cf.empty:
        return 0.0
    try:
        rows = [r for r in ["Free Cash Flow", "Operating Cash Flow"] if r in cf.index]
        if not rows:
            return 0.0
        fcf = abs(float(cf.loc[rows[0]].iloc[0]))
        if fcf <= 0:
            return 0.0
        pv = sum(fcf * (1.07 ** y) / (1 + wacc) ** y for y in range(1, 6))
        tv = (fcf * (1.07 ** 5) * (1 + g)) / (wacc - g)
        return pv + tv / (1 + wacc) ** 5
    except Exception:
        return 0.0


@st.cache_data(ttl=600, show_spinner=False)
def compute_pd_model(ticker: str) -> float:
    """Quick probability-of-default estimate for the Executive Summary KPI."""
    np.random.seed(42)
    n = 500
    X_syn = pd.DataFrame({
        "D_E": np.random.uniform(0.1, 5,   n),
        "ICR": np.random.uniform(0.5, 15,  n),
        "CR":  np.random.uniform(0.5, 4,   n),
        "ROE": np.random.uniform(-10, 30,  n),
        "NPM": np.random.uniform(-20, 40,  n),
    })
    y_syn = (
        ((X_syn["D_E"] > 3) & (X_syn["ROE"] < 5)) |
        ((X_syn["ICR"] < 1.5) & (X_syn["CR"] < 1))
    ).astype(int)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X_syn)
    lr = LogisticRegression(max_iter=500, random_state=42)
    lr.fit(Xs, y_syn)
    info = get_ticker_info(ticker)
    de  = float(info.get("debtToEquity",  1.5) or 1.5)   # realistic default
    de  = min(de / 100.0 if de > 20 else de, 10.0)        # yfinance returns % form
    icr = float(max((info.get("ebitdaMargins", 0.15) or 0.15) * 10, 0.5))
    cr  = float(info.get("currentRatio",  1.5) or 1.5)
    roe = float((info.get("returnOnEquity", 0.12) or 0.12) * 100)
    npm = float((info.get("profitMargins", 0.10) or 0.10) * 100)
    xi  = scaler.transform([[de, icr, cr, roe, npm]])
    return float(lr.predict_proba(xi)[0][1] * 100)


# ── ARIMA full forecast ───────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def run_arima(close_json: str, horizon: int = 90) -> dict:
    close = _read_json_series(close_json).sort_index()
    split = int(len(close) * 0.8)
    train, test = close.iloc[:split], close.iloc[split:]

    model = auto_arima(train, seasonal=False, stepwise=True,
                       suppress_warnings=True, error_action="ignore",
                       information_criterion="aic", max_p=5, max_q=5)
    order = model.order
    aic, bic = model.aic(), model.bic()

    # Walk-forward validation
    history, wf_preds = list(train), []
    for obs in test:
        try:
            m2 = auto_arima(history, seasonal=False, stepwise=True,
                            suppress_warnings=True, error_action="ignore",
                            start_p=order[0], start_q=order[2],
                            max_p=order[0]+1, max_q=order[2]+1, d=order[1])
            wf_preds.append(float(m2.predict(1)[0]))
        except Exception:
            wf_preds.append(history[-1])
        history.append(obs)

    wf_arr   = np.array(wf_preds)
    test_arr = np.array(test)
    rmse_out = np.sqrt(np.mean((test_arr - wf_arr) ** 2))
    mae_out  = np.mean(np.abs(test_arr - wf_arr))
    mape_out = np.mean(np.abs((test_arr - wf_arr) / (test_arr + 1e-8))) * 100
    in_pred  = model.predict_in_sample()
    rmse_in  = np.sqrt(np.mean((np.array(train) - in_pred) ** 2))

    full = auto_arima(close, seasonal=False, stepwise=True,
                      suppress_warnings=True, error_action="ignore",
                      max_p=5, max_q=5)
    fc, ci = full.predict(n_periods=horizon, return_conf_int=True)
    return dict(order=order, aic=aic, bic=bic, train=train, test=test,
                wf_preds=pd.Series(wf_arr, index=test.index),
                rmse_in=rmse_in, rmse_out=rmse_out,
                mae_out=mae_out, mape_out=mape_out,
                forecast=list(fc), ci=ci)


# ── GARCH volatility ──────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def run_garch(log_ret_json: str):
    lr = _read_json_series(log_ret_json).sort_index().dropna() * 100
    res = arch_model(lr, vol="Garch", p=1, q=1, dist="normal").fit(disp="off")
    cond_vol = res.conditional_volatility * np.sqrt(252)
    roll_vol = lr.rolling(20).std() * np.sqrt(252)
    return cond_vol, roll_vol, res.params


# ── Monte Carlo GBM ───────────────────────────────────────────

@st.cache_data(show_spinner=False)
def run_monte_carlo(mu_val: float, sigma_val: float, s0: float,
                    n_sims: int, n_days: int) -> np.ndarray:
    sims = np.zeros((n_days + 1, n_sims))
    sims[0] = s0
    Z = np.random.standard_normal((n_days, n_sims))
    for t in range(1, n_days + 1):
        sims[t] = sims[t-1] * np.exp(
            (mu_val - 0.5 * sigma_val ** 2) + sigma_val * Z[t-1]
        )
    return sims


# ── Value at Risk (3 methods + CVaR) ─────────────────────────

@st.cache_data(show_spinner=False)
def compute_var_all(ret_json: str, n_paths: int = 10000):
    rets = _read_json_series(ret_json).dropna()
    mu, sigma = rets.mean(), rets.std()
    h95 = float(np.percentile(rets, 5) * 100)
    h99 = float(np.percentile(rets, 1) * 100)
    p95 = float(norm.ppf(0.05, mu, sigma) * 100)
    p99 = float(norm.ppf(0.01, mu, sigma) * 100)
    mc_rets = np.random.normal(mu, sigma, n_paths)
    m95 = float(np.percentile(mc_rets, 5) * 100)
    m99 = float(np.percentile(mc_rets, 1) * 100)
    threshold = np.percentile(rets, 5)
    cvar = float(rets[rets <= threshold].mean() * 100)
    return h95, h99, p95, p99, m95, m99, cvar, mc_rets * 100


# ── Credit risk (logistic regression + confusion matrix) ──────

@st.cache_data(show_spinner=False)
def build_credit_model():
    np.random.seed(42)
    n = 500
    X = pd.DataFrame({
        "D_E": np.random.uniform(0.1, 5,   n),
        "ICR": np.random.uniform(0.5, 15,  n),
        "CR":  np.random.uniform(0.5, 4,   n),
        "ROE": np.random.uniform(-10, 30,  n),
        "NPM": np.random.uniform(-20, 40,  n),
    })
    y = (
        ((X["D_E"] > 3) & (X["ROE"] < 5)) |
        ((X["ICR"] < 1.5) & (X["CR"] < 1))
    ).astype(int)
    sc = StandardScaler()
    Xs = sc.fit_transform(X)
    Xtr, Xte, ytr, yte = train_test_split(Xs, y, test_size=0.2, random_state=42)
    lr = LogisticRegression(max_iter=500, random_state=42)
    lr.fit(Xtr, ytr)
    ypred = lr.predict(Xte)
    yprob = lr.predict_proba(Xte)[:, 1]
    acc   = accuracy_score(yte, ypred)
    auc   = roc_auc_score(yte, yprob)
    cm    = confusion_matrix(yte, ypred)
    return lr, sc, acc, auc, cm
