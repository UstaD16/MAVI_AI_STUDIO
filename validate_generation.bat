@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Generation Validation

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "VALIDATOR=%ROOT%validate_generation.py"

set "OUTPUT=%ROOT%output\prepared_generation.wav"
set "RESULT=%ROOT%output\generation_validation.json"

echo ============================================================
echo MAVI AI STUDIO
echo GENERATION OUTPUT VALIDATION
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
    echo [FAIL] validate_generation.py bulunamadi:
    echo %VALIDATOR%
    echo.
    pause
    exit /b 1
)

if not exist "%OUTPUT%" (
    echo [FAIL] Generation output bulunamadi:
    echo %OUTPUT%
    echo.
    echo Once execute_generation.bat calistirilmalidir.
    echo.
    pause
    exit /b 1
)

if not exist "%ROOT%output" (
    mkdir "%ROOT%output"
)

cd /d "%ROOT%"

echo Output:
echo %OUTPUT%
echo.

echo ============================================================
echo VALIDATION BASLIYOR
echo ============================================================
echo.

"%PYTHON%" "%VALIDATOR%" ^
    --output "%OUTPUT%" ^
    --target-seconds 120 ^
    --target-sample-rate 48000 ^
    --duration-tolerance 2 ^
    --result "%RESULT%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo GENERATION VALIDATION: PASS
) else (
    echo GENERATION VALIDATION: REJECT
)

echo.
echo Result:
echo %RESULT%
echo ============================================================
echo.

pause
exit /b %EXIT_CODE%