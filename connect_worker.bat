@echo off
setlocal EnableExtensions EnableDelayedExpansion

title MAVI AI STUDIO - Connect Real Worker

set "ROOT=%~dp0"
set "MAIN_PYTHON=%ROOT%.venv\Scripts\python.exe"
set "WORKER_PYTHON=%ROOT%.worker_venv\Scripts\python.exe"

set "BRIDGE=%ROOT%worker_bridge.py"
set "WORKER=%ROOT%worker.py"
set "RUNNER=%ROOT%stable_audio_runner.py"

echo ============================================================
echo MAVI AI STUDIO
echo REAL WORKER CONNECTION
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
REM WORKER PYTHON
REM ============================================================

if not exist "%WORKER_PYTHON%" (
    echo [FAIL] Worker Python bulunamadi:
    echo %WORKER_PYTHON%
    echo.
    pause
    exit /b 1
)

echo [OK] Worker Python
"%WORKER_PYTHON%" --version
echo.

REM ============================================================
REM FILES
REM ============================================================

if not exist "%BRIDGE%" (
    echo [FAIL] worker_bridge.py bulunamadi.
    pause
    exit /b 1
)

if not exist "%WORKER%" (
    echo [FAIL] worker.py bulunamadi.
    pause
    exit /b 1
)

if not exist "%RUNNER%" (
    echo [FAIL] stable_audio_runner.py bulunamadi.
    pause
    exit /b 1
)

echo [OK] Worker dosyalari
echo.

REM ============================================================
REM STABLE AUDIO CLI
REM ============================================================

if not defined MAVI_STABLE_AUDIO_CLI (
    echo [FAIL] MAVI_STABLE_AUDIO_CLI tanimli degil.
    echo.
    echo Once set_stable_audio_path.bat calistirin.
    echo.
    pause
    exit /b 1
)

if not exist "%MAVI_STABLE_AUDIO_CLI%" (
    echo [FAIL] Stable Audio CLI bulunamadi:
    echo %MAVI_STABLE_AUDIO_CLI%
    echo.
    pause
    exit /b 1
)

echo [OK] Stable Audio CLI
echo %MAVI_STABLE_AUDIO_CLI%
echo.

REM ============================================================
REM SESSION ENVIRONMENT
REM ============================================================

set "MAVI_WORKER_PYTHON=%WORKER_PYTHON%"
set "MAVI_WORKER_SCRIPT=%RUNNER%"
set "MAVI_GENERATION_REAL_ONLY=1"
set "MAVI_ALLOW_FAKE_AUDIO=0"
set "MAVI_ALLOW_PROCEDURAL_AUDIO=0"
set "MAVI_ALLOW_PROCEDURAL_PLACEHOLDER_AUDIO=0"

echo ============================================================
echo ACTIVE CONNECTION
echo ============================================================
echo.

echo MAIN PYTHON:
echo %MAIN_PYTHON%
echo.

echo WORKER PYTHON:
echo %MAVI_WORKER_PYTHON%
echo.

echo WORKER SCRIPT:
echo %MAVI_WORKER_SCRIPT%
echo.

echo STABLE AUDIO CLI:
echo %MAVI_STABLE_AUDIO_CLI%
echo.

echo REAL GENERATION : ENABLED
echo FAKE AUDIO      : DISABLED
echo PROCEDURAL      : DISABLED
echo.

REM ============================================================
REM RUNNER STATUS
REM ============================================================

echo ============================================================
echo RUNNER STATUS
echo ============================================================
echo.

"%WORKER_PYTHON%" "%RUNNER%" --status

if errorlevel 1 (
    echo.
    echo [FAIL] Stable Audio runner status basarisiz.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo WORKER BAGLANTISI HAZIR
echo ============================================================
echo.
echo Bu CMD oturumunda MAVI'nin real worker ayarlari aktif.
echo.
echo Yeni bir terminal acildiginda bu dosyanin tekrar
echo calistirilmasi gerekebilir.
echo.
echo ============================================================
echo.

pause
exit /b 0