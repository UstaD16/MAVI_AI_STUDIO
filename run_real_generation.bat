@echo off
setlocal EnableExtensions EnableDelayedExpansion

title MAVI AI STUDIO - REAL GENERATION

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.worker_venv\Scripts\python.exe"
set "RUNNER=%ROOT%stable_audio_runner.py"

echo ============================================================
echo MAVI AI STUDIO
echo REAL STABLE AUDIO 3 GENERATION
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

echo Stable Audio CLI:
echo %MAVI_STABLE_AUDIO_CLI%
echo.

echo ============================================================
echo GENERATION AYARLARI
echo ============================================================
echo.

set "PROMPT=Natural Turkish folk dance music, authentic acoustic performance, organic live ensemble, davul and zurna, traditional Turkish folk character, human timing, realistic acoustic instruments, preserve musical identity, no electronic synths, no organ, no keyboard timbre, no arcade sound, no toy instruments, no excessive quantization, no artificial EDM production"

set "OUTPUT=%ROOT%output\real_generation.wav"
set "SECONDS=30"
set "SEED=314159"

echo Prompt:
echo %PROMPT%
echo.
echo Output:
echo %OUTPUT%
echo.
echo Duration:
echo %SECONDS% seconds
echo.
echo Seed:
echo %SEED%
echo.

echo ============================================================
echo GERCEK GENERATION BASLIYOR
echo ============================================================
echo.

"%PYTHON%" "%RUNNER%" ^
    --prompt "%PROMPT%" ^
    --output "%OUTPUT%" ^
    --seconds %SECONDS% ^
    --seed %SEED% ^
    --dit sm-music ^
    --decoder same-s ^
    --steps 8 ^
    --threads 4

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo REAL GENERATION: SUCCESS

    if exist "%OUTPUT%" (
        echo.
        echo OUTPUT:
        echo %OUTPUT%
        echo.
        for %%A in ("%OUTPUT%") do (
            echo SIZE: %%~zA bytes
        )
    ) else (
        echo [FAIL] Generator basarili dondu fakat WAV bulunamadi.
        set "EXIT_CODE=1"
    )
) else (
    echo REAL GENERATION: FAILED
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%