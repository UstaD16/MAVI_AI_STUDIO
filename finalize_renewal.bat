@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Finalize Renewal

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "FINALIZER=%ROOT%finalize_renewal.py"

set "SOURCE=C:\Users\ORGOC\Desktop\MAVI'NİN MÜZİKLERİ\Kaynak\3 - shote-mori_u8taBMNc.mp3"
set "GENERATED=%ROOT%output\prepared_generation.wav"

set "RESULT=%ROOT%output\finalize_renewal_result.json"

echo ============================================================
echo MAVI AI STUDIO
echo FINAL RENEWAL
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%FINALIZER%" (
    echo [FAIL] finalize_renewal.py bulunamadi:
    echo %FINALIZER%
    echo.
    pause
    exit /b 1
)

if not exist "%SOURCE%" (
    echo [FAIL] Kaynak bulunamadi:
    echo %SOURCE%
    echo.
    pause
    exit /b 1
)

if not exist "%GENERATED%" (
    echo [FAIL] Generation output bulunamadi:
    echo %GENERATED%
    echo.
    echo Once execute_generation.bat calistirilmalidir.
    echo.
    pause
    exit /b 1
)

if not exist "%ROOT%output\final" (
    mkdir "%ROOT%output\final"
)

cd /d "%ROOT%"

echo SOURCE:
echo %SOURCE%
echo.

echo GENERATED:
echo %GENERATED%
echo.

echo ============================================================
echo FINAL QUALITY GATE
echo ============================================================
echo.

"%PYTHON%" "%FINALIZER%" ^
    --source "%SOURCE%" ^
    --generated "%GENERATED%" ^
    --target-seconds 120 ^
    --result "%RESULT%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo FINAL RENEWAL: SUCCESS
    echo.
    echo Final klasoru:
    echo %ROOT%output\final
) else (
    echo FINAL RENEWAL: FAILED
    echo.
    if exist "%RESULT%" (
        echo RESULT:
        type "%RESULT%"
    )
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%