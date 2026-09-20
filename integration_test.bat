@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Full Integration Test

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "TEST=%ROOT%integration_test.py"

echo ============================================================
echo MAVI AI STUDIO
echo FULL INTEGRATION TEST
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
    echo [FAIL] integration_test.py bulunamadi:
    echo %TEST%
    echo.
    pause
    exit /b 1
)

cd /d "%ROOT%"

echo Python:
"%PYTHON%" --version
echo.

echo ============================================================
echo FULL INTEGRATION TEST BASLIYOR
echo ============================================================
echo.

"%PYTHON%" "%TEST%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo INTEGRATION STATUS: READY
    echo.
    echo MAVI mimari baglantilari temel seviyede hazir.
) else (
    echo INTEGRATION STATUS: NEEDS FIX
    echo.
    echo Detayli rapor:
    echo %ROOT%logs\integration_test.json
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%