@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
)

call ".venv\Scripts\activate.bat"

if not exist "frontend\dist\index.html" (
    echo First run, installing deps... (3-5 min)
    cd backend
    pip install -r requirements.txt
    cd ..\frontend
    call npm install
    call npm run build
    cd ..
)

cd backend
echo Starting server at http://localhost:8000
start "" http://localhost:8000
python main.py
pause
