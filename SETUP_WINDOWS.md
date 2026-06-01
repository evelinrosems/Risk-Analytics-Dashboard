# Setup Instructions (Windows)

## Step 1 — Install Python 3.11
Download from https://www.python.org/downloads/release/python-3119/
- Choose "Windows installer (64-bit)"
- During install: tick "Add Python to PATH"

## Step 2 — Create a virtual environment
Open Command Prompt in the project folder and run:
```
py -3.11 -m venv venv
venv\Scripts\activate
```

## Step 3 — Install dependencies
```
pip install -r requirements.txt
```

## Step 4 — Run the app
```
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---
## Why Python 3.11?
Libraries like numpy, arch, and pmdarima do not yet have pre-built
wheels for Python 3.13. Python 3.11 has full support for all packages.
