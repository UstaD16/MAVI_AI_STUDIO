@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Create Worker Request

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "BUILDER=%ROOT%create_worker_request.py"

set "SOURCE=C:\Users\ORGOC\Desktop\MAVI'NİN MÜZİKLERİ\Kaynak\3 - shote-mori_u8taBMNc.mp3"
set "OUTPUT=%ROOT%output\shote_mori_renewal_request.wav"
set "REQUEST=%ROOT%output\shote_mori_renewal.json"

echo ============================================================
echo MAVI AI STUDIO
echo CREATE REAL RENEWAL REQUEST
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%BUILDER%" (
    echo [FAIL] create_worker_request.py bulunamadi.
    echo.
    pause
    exit /b 1
)

if not exist "%SOURCE%" (
    echo [FAIL] Kaynak dosyasi bulunamadi:
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

echo Renewal:
echo Kaydi bozma; dogal ve gercek akustik icra karakterini koru; mevcut melodiyi, ritmi, tempoyu ve tonal kimligi koru; davul ve bas gitar ile kontrollu bicimde yenile; gereksiz elektronik, synth, organ, keyboard ve arcade karakterinden kacın.
echo.

echo Request olusturuluyor...
echo.

"%PYTHON%" "%BUILDER%" ^
    --mode renewal ^
    --prompt "Kaydi bozma; dogal ve gercek akustik icra karakterini koru; mevcut melodiyi, ritmi, tempoyu ve tonal kimligi koru; davul ve bas gitar ile kontrollu bicimde yenile; gereksiz elektronik, synth, organ, keyboard ve arcade karakterinden kacın." ^
    --source "%SOURCE%" ^
    --output "%OUTPUT%" ^
    --seconds 120 ^
    --seed 314159 ^
    --init-noise-level 0.20 ^
    --steps 8 ^
    --threads 4 ^
    --cfg 1.0 ^
    --request "%REQUEST%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo REQUEST: READY
    echo.
    echo JSON:
    echo %REQUEST%
) else (
    echo REQUEST: FAILED
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%