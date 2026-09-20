@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Paths

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "PATHS=%ROOT%mavi_paths.py"

echo ============================================================
echo MAVI AI STUDIO
echo CENTRAL PATH STATUS
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%PATHS%" (
    echo [FAIL] mavi_paths.py bulunamadi:
    echo %PATHS%
    echo.
    pause
    exit /b 1
)

cd /d "%ROOT%"

echo Python:
"%PYTHON%" --version
echo.

echo ============================================================
echo PATH KONTROLU
echo ============================================================
echo.

"%PYTHON%" "%PATHS%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo PATH STATUS: READY
) else (
    echo PATH STATUS: FAILED
)

echo EXIT CODE: %EXIT_CODE%
echo ============================================================
echo.

pause
exit /b %EXIT_CODE%