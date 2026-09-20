@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Production Report

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "REPORT=%ROOT%production_report.py"

echo ============================================================
echo MAVI AI STUDIO
echo PRODUCTION REPORT
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%REPORT%" (
    echo [FAIL] production_report.py bulunamadi:
    echo %REPORT%
    echo.
    pause
    exit /b 1
)

if not exist "%ROOT%output" (
    mkdir "%ROOT%output"
)

cd /d "%ROOT%"

echo Python:
"%PYTHON%" --version
echo.

echo ============================================================
echo RAPOR OLUSTURULUYOR
echo ============================================================
echo.

"%PYTHON%" "%REPORT%" ^
    --json "%ROOT%output\MAVI_production_report.json" ^
    --text "%ROOT%output\MAVI_production_report.txt"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo PRODUCTION REPORT: READY
    echo.
    echo JSON:
    echo %ROOT%output\MAVI_production_report.json
    echo.
    echo TEXT:
    echo %ROOT%output\MAVI_production_report.txt
) else (
    echo PRODUCTION REPORT: FAILED
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%