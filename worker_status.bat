@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Worker Status

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "STATUS=%ROOT%worker_status.py"

echo ============================================================
echo MAVI AI STUDIO
echo REAL WORKER STATUS
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%STATUS%" (
    echo [FAIL] worker_status.py bulunamadi:
    echo %STATUS%
    echo.
    pause
    exit /b 1
)

cd /d "%ROOT%"

echo Python:
"%PYTHON%" --version
echo.

echo ============================================================
echo WORKER STATUS
echo ============================================================
echo.

"%PYTHON%" "%STATUS%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo REAL WORKER: READY
) else (
    echo REAL WORKER: NOT READY
    echo.
    echo Detayli rapor:
    echo %ROOT%logs\worker_status.json
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%