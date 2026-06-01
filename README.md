# Risk Analytics Dashboard

### MCA Financial Analytics Capstone Project

A professional Risk Analytics Dashboard built using Python, Streamlit, Plotly, and Yahoo Finance. The dashboard provides forecasting, volatility modeling, valuation, portfolio optimization, credit risk analysis, and risk management tools for NSE-listed stocks.

---

## Features

### Executive Summary

* Current Price KPI
* Expected Return
* Portfolio Return
* Portfolio Risk
* Value at Risk (95% & 99%)
* Probability of Default
* Sharpe Ratio
* Investment Signal (BUY / HOLD / SELL)

### ARIMA Forecasting

* Auto ARIMA Model Selection
* 90-Day Price Forecast
* Confidence Intervals
* RMSE, MAE, and MAPE Metrics

### GARCH Volatility Modeling

* GARCH(1,1) Model
* Conditional Volatility Analysis
* Volatility Regime Detection
* Volatility Spike Identification

### DCF Valuation

* Discounted Cash Flow Analysis
* Terminal Value Calculation
* Margin of Safety
* Intrinsic Value Estimation

### Monte Carlo Simulation

* Geometric Brownian Motion
* Price Path Simulation
* Best Case and Worst Case Scenarios
* Probability Analysis

### Value at Risk (VaR)

* Historical VaR
* Parametric VaR
* Monte Carlo VaR
* Expected Shortfall (CVaR)
* Kupiec Backtesting

### Credit Risk Modeling

* Logistic Regression Model
* Probability of Default Estimation
* Credit Score Calculation
* Risk Grade Classification

### Portfolio Optimization

* Efficient Frontier
* Maximum Sharpe Portfolio
* Asset Allocation Analysis
* Portfolio Performance Metrics

### Correlation Heatmap

* Asset Correlation Analysis
* Diversification Insights
* Correlation Visualization

---

## Technology Stack

* Python
* Streamlit
* Plotly
* Pandas
* NumPy
* yFinance
* Statsmodels
* pmdarima
* ARCH
* Scikit-Learn
* SciPy
* PyPortfolioOpt

---

## Project Structure

```text
risk_dashboard_split/
│
├── app.py
├── requirements.txt
├── README.md
├── assets/
│   └── style.css
│
├── modules/
│   ├── config.py
│   ├── data_loader.py
│   ├── models.py
│   ├── tab_arima.py
│   ├── tab_credit.py
│   ├── tab_dcf.py
│   ├── tab_executive.py
│   ├── tab_garch.py
│   ├── tab_monte_carlo.py
│   ├── tab_portfolio.py
│   ├── tab_stress.py
│   ├── tab_var.py
│   ├── tab_correlation.py
│   └── ui_helpers.py
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/evelinrosems/Risk-Analytics-Dashboard.git
cd Risk-Analytics-Dashboard
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

---

## Data Source

Market data is obtained from Yahoo Finance using the yFinance library.

Supported NSE Stocks:

* RELIANCE.NS
* TCS.NS
* INFY.NS
* HDFCBANK.NS
* WIPRO.NS

---

## Academic Project

This project was developed as part of the MCA Financial Analytics Capstone Project and demonstrates practical applications of:

* Time Series Forecasting
* Volatility Modeling
* Risk Analytics
* Credit Risk Assessment
* Portfolio Optimization
* Financial Valuation

---

## Author

**Evelin Rose**

MCA Financial Analytics Capstone Project

Built using Python, Streamlit, Plotly, and Financial Analytics Techniques.
