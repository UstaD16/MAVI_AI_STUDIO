@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Pipeline Controller

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "CONTROLLER=%ROOT%pipeline_controller.py"

set "SOURCE=C:\Users\ORGOC\Desktop\MAVI'NİN MÜZİKLERİ\Kaynak\3 - shote-mori_u8taBMNc.mp3"
set "COMMAND=eski kaydi bozma; melodiyi, ritmi, tempoyu ve tonal kimligi koru; davul bas gitar zurna ve sol klarnet ile dogal canli ensemble olarak yenile"

set "RESULT=%ROOT%output\pipeline_result.json"

echo ============================================================
echo MAVI AI STUDIO
echo CENTRAL PIPELINE CONTROLLER
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%CONTROLLER%" (
    echo [FAIL] pipeline_controller.py bulunamadi:
    echo %CONTROLLER%
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

echo Python:
"%PYTHON%" --version
echo.

echo SOURCE:
echo %SOURCE%
echo.

echo COMMAND:
echo %COMMAND%
echo.

echo ============================================================
echo PIPELINE
echo ============================================================
echo.

"%PYTHON%" "%CONTROLLER%" ^
    --source "%SOURCE%" ^
    --command "%COMMAND%" ^
    --seconds 120 ^
    --seed 314159 ^
    --steps 8 ^
    --threads 4 ^
    --cfg 1.0 ^
    --init-noise-level 0.20 ^
    --result "%RESULT%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo PIPELINE STATUS: SUCCESS
    echo.
    echo RESULT:
    echo %RESULT%
) else (
    echo PIPELINE STATUS: FAILED
    echo.
    echo RESULT:
    echo %RESULT%

    if exist "%RESULT%" (
        echo.
        type "%RESULT%"
    )
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%