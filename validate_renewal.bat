@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Renewal Validation

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "VALIDATOR=%ROOT%validate_renewal.py"

set "SOURCE=C:\Users\ORGOC\Desktop\MAVI'NİN MÜZİKLERİ\Kaynak\3 - shote-mori_u8taBMNc.mp3"
set "RENEWED=%ROOT%output\shote_mori_renewal.wav"
set "RESULT=%ROOT%output\shote_mori_validation.json"

echo ============================================================
echo MAVI AI STUDIO
echo RENEWAL OUTPUT VALIDATION
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%VALIDATOR%" (
    echo [FAIL] validate_renewal.py bulunamadi.
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

if not exist "%RENEWED%" (
    echo [FAIL] Renewal WAV bulunamadi:
    echo %RENEWED%
    echo.
    echo Once run_renewal_request.bat calistirilmalidir.
    echo.
    pause
    exit /b 1
)

if not exist "%ROOT%output" (
    mkdir "%ROOT%output"
)

cd /d "%ROOT%"

echo SOURCE:
echo %SOURCE%
echo.

echo RENEWED:
echo %RENEWED%
echo.

echo ============================================================
echo VALIDATION BASLIYOR
echo ============================================================
echo.

"%PYTHON%" "%VALIDATOR%" ^
    --source "%SOURCE%" ^
    --renewed "%RENEWED%" ^
    --result "%RESULT%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo RENEWAL VALIDATION: PASS
) else (
    echo RENEWAL VALIDATION: REJECT
)

echo RESULT:
echo %RESULT%
echo ============================================================
echo.

pause
exit /b %EXIT_CODE%