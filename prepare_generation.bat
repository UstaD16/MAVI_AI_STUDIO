@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Prepare Generation

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "PREPARE=%ROOT%prepare_generation.py"

set "SOURCE=C:\Users\ORGOC\Desktop\MAVI'NİN MÜZİKLERİ\Kaynak\3 - shote-mori_u8taBMNc.mp3"
set "OUTPUT=%ROOT%output\prepared_generation.wav"
set "RESULT=%ROOT%output\prepared_generation.json"

echo ============================================================
echo MAVI AI STUDIO
echo GENERATION PREPARATION
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%PREPARE%" (
    echo [FAIL] prepare_generation.py bulunamadi:
    echo %PREPARE%
    echo.
    pause
    exit /b 1
)

if not exist "%SOURCE%" (
    echo [FAIL] Kaynak audio bulunamadi:
    echo %SOURCE%
    echo.
    pause
    exit /b 1
)

if not exist "%ROOT%output" (
    mkdir "%ROOT%output"
)

cd /d "%ROOT%"

echo Kaynak:
echo %SOURCE%
echo.

echo ============================================================
echo MAVI GENERATION PLAN
echo ============================================================
echo.

"%PYTHON%" "%PREPARE%" ^
    --prompt "Eski halk muzigi kaydini bozma; kaynak melodiyi, ritmi, tempoyu, tonal karakteri ve yoresel kimligi koru; davul, bas gitar, zurna ve sol klarneti dogal canli icra hissiyle kontrollu bicimde ekle; gercek akustik ensemble karakteri; organ, keyboard, synth, arcade ve yapay karakter kullanma." ^
    --source "%SOURCE%" ^
    --output "%OUTPUT%" ^
    --seconds 120 ^
    --seed 314159 ^
    --steps 8 ^
    --threads 4 ^
    --cfg 1.0 ^
    --dit sm-music ^
    --decoder same-s ^
    --init-noise-level 0.20 ^
    --result "%RESULT%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo GENERATION PREPARATION: READY
    echo.
    echo Request:
    echo %RESULT%
) else (
    echo GENERATION PREPARATION: FAILED
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%