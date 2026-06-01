@echo off
echo ============================================
echo  Risk Analytics Dashboard - Auto Setup
echo ============================================

:: Check if venv already exists
IF EXIST venv\Scripts\activate.bat (
    echo Virtual environment found. Activating...
) ELSE (
    echo Creating virtual environment with Python 3.11...
    py -3.11 -m venv venv
    IF ERRORLEVEL 1 (
        echo.
        echo ERROR: Python 3.11 not found!
        echo Please install it from:
        echo https://www.python.org/downloads/release/python-3119/
        echo During install, tick "Add Python to PATH"
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo Starting app...
echo Open http://localhost:8501 in your browser
echo.
streamlit run app.py

pause
