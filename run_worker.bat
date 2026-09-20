@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Real Audio Worker

set "ROOT=%~dp0"
set "WORKER_VENV=%ROOT%.worker_venv"
set "PYTHON=%WORKER_VENV%\Scripts\python.exe"
set "WORKER=%ROOT%worker.py"

echo ============================================================
echo MAVI AI STUDIO
echo REAL AUDIO WORKER
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [ERROR] Worker Python bulunamadi.
    echo Once setup_worker.bat calistirin.
    echo.
    pause
    exit /b 1
)

if not exist "%WORKER%" (
    echo [ERROR] worker.py bulunamadi.
    echo.
    pause
    exit /b 1
)

echo Python:
"%PYTHON%" --version
echo.

echo Worker:
echo %WORKER%
echo.

echo Worker status:
echo ------------------------------------------------------------
"%PYTHON%" "%WORKER%" --status
echo ------------------------------------------------------------
echo.

echo MAVI_STABLE_AUDIO_COMMAND:
if defined MAVI_STABLE_AUDIO_COMMAND (
    echo CONFIGURED
) else (
    echo NOT CONFIGURED
)

echo.
echo ============================================================
echo Worker hazir.
echo ============================================================
echo.

pause
exit /b 0