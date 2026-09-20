@echo off
setlocal EnableExtensions EnableDelayedExpansion

title MAVI AI STUDIO - Configure Real Audio Worker

set "ROOT=%~dp0"
set "WORKER_VENV=%ROOT%.worker_venv"
set "PYTHON=%WORKER_VENV%\Scripts\python.exe"

echo ============================================================
echo MAVI AI STUDIO
echo REAL AUDIO WORKER CONFIGURATION
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [ERROR] Worker virtual environment bulunamadi.
    echo.
    echo Once setup_worker.bat calistirin.
    echo.
    pause
    exit /b 1
)

echo Worker Python:
echo %PYTHON%
echo.

echo Bu script mevcut worker yapilandirmasini kontrol eder.
echo Gercek Stable Audio komutu elle girilmeden herhangi bir
echo sahte veya procedural audio fallback etkinlestirilmez.
echo.

echo ============================================================
echo MEVCUT AYARLAR
echo ============================================================
echo.

if defined MAVI_STABLE_AUDIO_COMMAND (
    echo MAVI_STABLE_AUDIO_COMMAND = CONFIGURED
    echo.
    echo Mevcut komut:
    echo %MAVI_STABLE_AUDIO_COMMAND%
) else (
    echo MAVI_STABLE_AUDIO_COMMAND = NOT CONFIGURED
)

echo.

if defined MAVI_GENERATOR_COMMAND (
    echo MAVI_GENERATOR_COMMAND = CONFIGURED
    echo.
    echo Mevcut generator:
    echo %MAVI_GENERATOR_COMMAND%
) else (
    echo MAVI_GENERATOR_COMMAND = NOT CONFIGURED
)

echo.

if defined MAVI_WORKER_PYTHON (
    echo MAVI_WORKER_PYTHON = %MAVI_WORKER_PYTHON%
) else (
    echo MAVI_WORKER_PYTHON = NOT SET
)

if defined MAVI_WORKER_SCRIPT (
    echo MAVI_WORKER_SCRIPT = %MAVI_WORKER_SCRIPT%
) else (
    echo MAVI_WORKER_SCRIPT = NOT SET
)

echo.
echo ============================================================
echo TEST
echo ============================================================
echo.

"%PYTHON%" "%ROOT%worker.py" --status

echo.
echo ============================================================
echo NOT
echo ============================================================
echo.
echo Bu dosya otomatik olarak bilinmeyen bir Stable Audio
echo komutu uretmez.
echo.
echo Gercek generator entegrasyonu kesin komut belirlendiginde
echo environment variable ile yapilacaktir.
echo.
echo ============================================================
echo.

pause
exit /b 0