@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Stable Audio 3 Worker

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.worker_venv\Scripts\python.exe"
set "RUNNER=%ROOT%stable_audio_runner.py"

echo ============================================================
echo MAVI AI STUDIO
echo STABLE AUDIO 3 REAL WORKER
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [ERROR] Worker Python bulunamadi.
    echo.
    echo Once setup_worker.bat calistirin.
    echo.
    pause
    exit /b 1
)

if not exist "%RUNNER%" (
    echo [ERROR] stable_audio_runner.py bulunamadi.
    echo.
    pause
    exit /b 1
)

echo Python:
"%PYTHON%" --version
echo.

echo Stable Audio 3 Runner:
echo %RUNNER%
echo.

echo ============================================================
echo CLI DURUMU
echo ============================================================
echo.

"%PYTHON%" "%RUNNER%" --status

echo.
echo ============================================================
echo.

pause
exit /b 0