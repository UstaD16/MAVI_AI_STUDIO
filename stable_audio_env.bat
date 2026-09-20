@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Stable Audio Environment

set "ROOT=%~dp0"
set "WORKER_VENV=%ROOT%.worker_venv"
set "WORKER_PYTHON=%WORKER_VENV%\Scripts\python.exe"

echo ============================================================
echo MAVI AI STUDIO
echo STABLE AUDIO ENVIRONMENT
echo ============================================================
echo.

if not exist "%WORKER_PYTHON%" (
    echo [ERROR] Worker Python bulunamadi.
    echo Once setup_worker.bat calistirin.
    echo.
    pause
    exit /b 1
)

REM ============================================================
REM WORKER PYTHON
REM ============================================================

set "MAVI_WORKER_PYTHON=%WORKER_PYTHON%"
set "MAVI_WORKER_SCRIPT=%ROOT%stable_audio_worker.py"

REM ============================================================
REM GENERATOR ADAPTER
REM ============================================================

set "MAVI_STABLE_AUDIO_MODULE="
set "MAVI_STABLE_AUDIO_CLASS="
set "MAVI_STABLE_AUDIO_FUNCTION="
set "MAVI_STABLE_AUDIO_MODEL="
set "MAVI_STABLE_AUDIO_DEVICE=cpu"

REM ============================================================
REM MAIN BRIDGE
REM ============================================================

set "MAVI_STABLE_AUDIO_COMMAND="
set "MAVI_GENERATOR_COMMAND="

REM ============================================================
REM POLICY
REM ============================================================

set "MAVI_GENERATION_REAL_ONLY=1"
set "MAVI_ALLOW_FAKE_AUDIO=0"
set "MAVI_ALLOW_PROCEDURAL_AUDIO=0"

REM ============================================================
REM DISPLAY
REM ============================================================

echo Worker Python:
echo %MAVI_WORKER_PYTHON%
echo.

echo Worker Script:
echo %MAVI_WORKER_SCRIPT%
echo.

echo Device:
echo %MAVI_STABLE_AUDIO_DEVICE%
echo.

echo Real generation:
echo ENABLED
echo.

echo Fake audio:
echo DISABLED
echo.

echo Procedural placeholder audio:
echo DISABLED
echo.

echo ============================================================
echo ORTAM BU TERMINAL OTURUMU ICIN HAZIR
echo ============================================================
echo.
echo NOT:
echo Gercek Stable Audio backend komutu bu dosyada uydurulmaz.
echo Backend adapteri kesinlestiginde ilgili environment
echo degiskenleri burada etkinlestirilecektir.
echo.
echo Bu pencere acik kaldigi surece ayarlar gecerlidir.
echo.
echo ============================================================
echo.

pause
exit /b 0