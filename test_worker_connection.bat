@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Worker Connection Test

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "TEST=%ROOT%test_worker_connection.py"

echo ============================================================
echo MAVI AI STUDIO
echo WORKER CONNECTION TEST
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%TEST%" (
    echo [FAIL] test_worker_connection.py bulunamadi.
    echo.
    pause
    exit /b 1
)

cd /d "%ROOT%"

echo Python:
"%PYTHON%" --version
echo.

echo ============================================================
echo TEST BASLIYOR
echo ============================================================
echo.

"%PYTHON%" "%TEST%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================
if "%EXIT_CODE%"=="0" (
    echo WORKER CONNECTION: READY
) else (
    echo WORKER CONNECTION: NOT READY
)
echo EXIT CODE: %EXIT_CODE%
echo ============================================================
echo.

pause
exit /b %EXIT_CODE%