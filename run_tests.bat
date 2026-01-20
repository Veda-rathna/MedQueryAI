@echo off
echo ============================================
echo Running Backend Tests
echo ============================================
echo.

cd backend
call venv\Scripts\activate.bat

echo Installing test dependencies...
pip install -r tests\requirements-test.txt

echo.
echo Running unit tests...
python tests\test_backend.py

echo.
echo ============================================
echo Tests Complete
echo ============================================
pause
