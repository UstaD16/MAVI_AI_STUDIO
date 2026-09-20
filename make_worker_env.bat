@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Persistent Worker Environment

set "ROOT=%~dp0"
set "WORKER_VENV=%ROOT%.worker_venv"
set "WORKER_PYTHON=%WORKER_VENV%\Scripts\python.exe"
set "WORKER_SCRIPT=%ROOT%stable_audio_runner.py"

echo ============================================================
echo MAVI AI STUDIO
echo PERSISTENT WORKER ENVIRONMENT
echo ============================================================
echo.

if not exist "%WORKER_PYTHON%" (
    echo [FAIL] Worker Python bulunamadi:
    echo %WORKER_PYTHON%
    echo.
    echo Once setup_worker.bat calistirin.
    echo.
    pause
    exit /b 1
)

if not exist "%WORKER_SCRIPT%" (
    echo [FAIL] stable_audio_runner.py bulunamadi.
    echo.
    pause
    exit /b 1
)

echo Worker Python:
echo %WORKER_PYTHON%
echo.

echo Worker Script:
echo %WORKER_SCRIPT%
echo.

REM ============================================================
REM STABLE AUDIO VARIABLES
REM ============================================================

setx MAVI_WORKER_PYTHON "%WORKER_PYTHON%" >nul
setx MAVI_WORKER_SCRIPT "%WORKER_SCRIPT%" >nul

REM ============================================================
REM REAL AUDIO POLICY
REM ============================================================

setx MAVI_GENERATION_REAL_ONLY "1" >nul
setx MAVI_ALLOW_FAKE_AUDIO "0" >nul
setx MAVI_ALLOW_PROCEDURAL_AUDIO "0" >nul
setx MAVI_ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO "0" >nul

REM ============================================================
REM STABLE AUDIO DEVICE
REM ============================================================

setx MAVI_STABLE_AUDIO_DEVICE "cpu" >nul

if errorlevel 1 (
    echo.
    echo [FAIL] Environment degiskenleri kaydedilemedi.
    echo.
    pause
    exit /b 1
)

echo ============================================================
echo ENVIRONMENT KAYDEDILDI
echo ============================================================
echo.
echo MAVI_WORKER_PYTHON
echo %WORKER_PYTHON%
echo.
echo MAVI_WORKER_SCRIPT
echo %WORKER_SCRIPT%
echo.
echo MAVI_GENERATION_REAL_ONLY=1
echo MAVI_ALLOW_FAKE_AUDIO=0
echo MAVI_ALLOW_PROCEDURAL_AUDIO=0
echo MAVI_ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO=0
echo MAVI_STABLE_AUDIO_DEVICE=cpu
echo.
echo ============================================================
echo ONEMLI
echo ============================================================
echo Yeni terminal oturumunda bu degiskenler aktif olacaktir.
echo Mevcut terminali kapatip yeni terminal acin.
echo ============================================================
echo.

pause
exit /b 0