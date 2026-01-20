@echo off
echo ============================================
echo Drug Information Chatbot - Quick Setup
echo ============================================
echo.

echo [1/3] Setting up Python virtual environment...
cd backend
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo [2/3] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [3/3] Installing frontend dependencies...
cd ..\frontend
call npm install

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Start LM Studio (localhost:1234)
echo 2. Run: start_backend.bat
echo 3. Run: start_frontend.bat
echo 4. Open: http://localhost:3000
echo.
pause
