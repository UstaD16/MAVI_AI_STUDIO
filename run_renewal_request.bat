@echo off
setlocal EnableExtensions EnableDelayedExpansion

title MAVI AI STUDIO - REAL RENEWAL REQUEST

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.worker_venv\Scripts\python.exe"
set "RUNNER=%ROOT%stable_audio_runner.py"

set "REQUEST=%ROOT%output\shote_mori_renewal.json"
set "OUTPUT=%ROOT%output\shote_mori_renewal.wav"

echo ============================================================
echo MAVI AI STUDIO
echo REAL AUDIO-TO-AUDIO RENEWAL
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

if not exist "%REQUEST%" (
    echo [FAIL] Renewal request bulunamadi:
    echo %REQUEST%
    echo.
    echo Once create_worker_request.bat calistirin.
    echo.
    pause
    exit /b 1
)

if not defined MAVI_STABLE_AUDIO_CLI (
    echo [FAIL] MAVI_STABLE_AUDIO_CLI tanimli degil.
    echo.
    echo Once set_stable_audio_path.bat calistirin.
    echo.
    pause
    exit /b 1
)

if not exist "%MAVI_STABLE_AUDIO_CLI%" (
    echo [FAIL] Stable Audio 3 CLI bulunamadi:
    echo %MAVI_STABLE_AUDIO_CLI%
    echo.
    pause
    exit /b 1
)

echo Request:
echo %REQUEST%
echo.

echo ============================================================
echo REQUEST ICERIGI
echo ============================================================
echo.

type "%REQUEST%"

echo.
echo ============================================================
echo REAL GENERATION
echo ============================================================
echo.

"%PYTHON%" -c ^
"import json,sys; from pathlib import Path; p=Path(r'%REQUEST%'); d=json.loads(p.read_text(encoding='utf-8')); print(json.dumps(d,ensure_ascii=False,indent=2));"

if errorlevel 1 (
    echo.
    echo [FAIL] Request JSON okunamadi.
    echo.
    pause
    exit /b 1
)

echo.
echo Stable Audio 3 calistiriliyor...
echo.

"%PYTHON%" "%RUNNER%" ^
    --request "%REQUEST%" ^
    --result "%ROOT%output\shote_mori_renewal_result.json"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo RENEWAL GENERATION: SUCCESS
    echo.
    if exist "%OUTPUT%" (
        echo OUTPUT:
        echo %OUTPUT%
        echo.
        for %%A in ("%OUTPUT%") do (
            echo SIZE: %%~zA bytes
        )
    ) else (
        echo [FAIL] Result basarili ancak beklenen WAV bulunamadi.
        set "EXIT_CODE=1"
    )
) else (
    echo RENEWAL GENERATION: FAILED
    echo.
    if exist "%ROOT%output\shote_mori_renewal_result.json" (
        echo RESULT:
        type "%ROOT%output\shote_mori_renewal_result.json"
    )
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%