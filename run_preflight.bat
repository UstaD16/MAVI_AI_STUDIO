@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Preflight

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "PREFLIGHT=%ROOT%preflight.py"

echo ============================================================
echo MAVI AI STUDIO
echo PREFLIGHT CHECK
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%PREFLIGHT%" (
    echo [FAIL] preflight.py bulunamadi:
    echo %PREFLIGHT%
    echo.
    pause
    exit /b 1
)

cd /d "%ROOT%"

echo Python:
"%PYTHON%" --version
echo.

echo ============================================================
echo PREFLIGHT BASLIYOR
echo ============================================================
echo.

"%PYTHON%" "%PREFLIGHT%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo PREFLIGHT STATUS: READY
) else (
    echo PREFLIGHT STATUS: FAILED
    echo.
    echo Yukaridaki hata listesi kontrol edilmelidir.
)

echo EXIT CODE: %EXIT_CODE%
echo ============================================================
echo.

pause
exit /b %EXIT_CODE%