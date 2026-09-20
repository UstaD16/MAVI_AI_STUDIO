@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Stable Audio Check

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.worker_venv\Scripts\python.exe"
set "RUNNER=%ROOT%stable_audio_runner.py"

echo ============================================================
echo MAVI AI STUDIO
echo STABLE AUDIO 3 ENVIRONMENT CHECK
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Worker Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%RUNNER%" (
    echo [FAIL] stable_audio_runner.py bulunamadi.
    echo.
    pause
    exit /b 1
)

echo [OK] Worker Python
"%PYTHON%" --version
echo.

echo ------------------------------------------------------------
echo Stable Audio 3 environment
echo ------------------------------------------------------------

if defined MAVI_STABLE_AUDIO_3_DIR (
    echo [OK] MAVI_STABLE_AUDIO_3_DIR
    echo %MAVI_STABLE_AUDIO_3_DIR%
) else (
    echo [FAIL] MAVI_STABLE_AUDIO_3_DIR tanimli degil.
)

echo.

if defined MAVI_STABLE_AUDIO_CLI (
    echo [OK] MAVI_STABLE_AUDIO_CLI
    echo %MAVI_STABLE_AUDIO_CLI%
) else (
    echo [FAIL] MAVI_STABLE_AUDIO_CLI tanimli degil.
)

echo.

if defined MAVI_STABLE_AUDIO_CLI (
    if exist "%MAVI_STABLE_AUDIO_CLI%" (
        echo [OK] sa3.bat bulundu.
    ) else (
        echo [FAIL] sa3.bat yolu mevcut degil.
    )
)

echo.
echo ------------------------------------------------------------
echo Runner status
echo ------------------------------------------------------------

"%PYTHON%" "%RUNNER%" --status

set "STATUS=%ERRORLEVEL%"

echo.
echo ============================================================

if "%STATUS%"=="0" (
    echo STABLE AUDIO CHECK: OK
) else (
    echo STABLE AUDIO CHECK: FAILED
)

echo ============================================================
echo.

pause
exit /b %STATUS%