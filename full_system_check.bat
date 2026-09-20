@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Full System Check

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "CHECK=%ROOT%full_system_check.py"

echo ============================================================
echo MAVI AI STUDIO
echo FULL SYSTEM CHECK
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%CHECK%" (
    echo [FAIL] full_system_check.py bulunamadi:
    echo %CHECK%
    echo.
    pause
    exit /b 1
)

cd /d "%ROOT%"

echo Python:
"%PYTHON%" --version
echo.

echo ============================================================
echo FULL SYSTEM CHECK BASLIYOR
echo ============================================================
echo.

"%PYTHON%" "%CHECK%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo SYSTEM STATUS: READY
    echo.
    echo Ayrintili rapor:
    echo %ROOT%logs\full_system_check.json
) else (
    echo SYSTEM STATUS: NEEDS FIX
    echo.
    echo Ayrintili rapor:
    echo %ROOT%logs\full_system_check.json
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%