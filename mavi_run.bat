@echo off
setlocal EnableExtensions EnableDelayedExpansion

title MAVI AI STUDIO - REAL MUSIC AI

set "ROOT=%~dp0"

set "MAIN_PYTHON=%ROOT%.venv\Scripts\python.exe"
set "WORKER_PYTHON=%ROOT%.worker_venv\Scripts\python.exe"

set "APP=%ROOT%app.py"
set "PREFLIGHT=%ROOT%preflight.py"
set "RUNNER=%ROOT%stable_audio_runner.py"

echo ============================================================
echo MAVI AI STUDIO
echo REAL MUSIC AI
echo ============================================================
echo.

REM ============================================================
REM MAIN PYTHON
REM ============================================================

if not exist "%MAIN_PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %MAIN_PYTHON%
    echo.
    pause
    exit /b 1
)

echo [OK] Ana Python
"%MAIN_PYTHON%" --version
echo.

REM ============================================================
REM APP
REM ============================================================

if not exist "%APP%" (
    echo [FAIL] app.py bulunamadi.
    echo.
    pause
    exit /b 1
)

echo [OK] app.py
echo.

REM ============================================================
REM WORKER
REM ============================================================

if not exist "%WORKER_PYTHON%" (
    echo [FAIL] Worker Python bulunamadi:
    echo %WORKER_PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%RUNNER%" (
    echo [FAIL] Stable Audio runner bulunamadi:
    echo %RUNNER%
    echo.
    pause
    exit /b 1
)

echo [OK] Worker Python
"%WORKER_PYTHON%" --version
echo.

REM ============================================================
REM REAL AUDIO POLICY
REM ============================================================

set "MAVI_GENERATION_REAL_ONLY=1"
set "MAVI_ALLOW_FAKE_AUDIO=0"
set "MAVI_ALLOW_PROCEDURAL_AUDIO=0"
set "MAVI_ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO=0"

REM ============================================================
REM WORKER CONNECTION
REM ============================================================

set "MAVI_WORKER_PYTHON=%WORKER_PYTHON%"
set "MAVI_WORKER_SCRIPT=%RUNNER%"

if defined MAVI_STABLE_AUDIO_CLI (
    echo [OK] Stable Audio CLI environment mevcut.
) else (
    echo [WARN] MAVI_STABLE_AUDIO_CLI bu oturumda tanimli degil.
)

echo.

REM ============================================================
REM PREFLIGHT
REM ============================================================

if exist "%PREFLIGHT%" (

    echo ============================================================
    echo PREFLIGHT
    echo ============================================================
    echo.

    "%MAIN_PYTHON%" "%PREFLIGHT%"

    if errorlevel 1 (
        echo.
        echo [FAIL] Preflight basarisiz.
        echo MAVI baslatilmiyor.
        echo.
        pause
        exit /b 1
    )

    echo.
    echo [OK] Preflight
    echo.
)

REM ============================================================
REM START
REM ============================================================

cd /d "%ROOT%"

echo ============================================================
echo MAVI BASLATILIYOR
echo ============================================================
echo.

"%MAIN_PYTHON%" "%APP%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================
echo MAVI AI STUDIO KAPANDI
echo EXIT CODE: %EXIT_CODE%
echo ============================================================
echo.

if not "%EXIT_CODE%"=="0" (
    pause
)

exit /b %EXIT_CODE%