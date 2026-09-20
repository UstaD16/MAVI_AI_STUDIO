@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Execute Real Generation

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "EXECUTOR=%ROOT%execute_generation.py"

set "PREPARED=%ROOT%output\prepared_generation.json"
set "RESULT=%ROOT%output\generation_result.json"

echo ============================================================
echo MAVI AI STUDIO
echo EXECUTE REAL GENERATION
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%EXECUTOR%" (
    echo [FAIL] execute_generation.py bulunamadi:
    echo %EXECUTOR%
    echo.
    pause
    exit /b 1
)

if not exist "%PREPARED%" (
    echo [FAIL] Prepared generation request bulunamadi:
    echo %PREPARED%
    echo.
    echo Once prepare_generation.bat calistirilmalidir.
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

echo Prepared request:
echo %PREPARED%
echo.

echo Result:
echo %RESULT%
echo.

echo ============================================================
echo GERCEK GENERATION BASLIYOR
echo ============================================================
echo.
echo Bu islem gercek Stable Audio backendini calistirir.
echo Fake / procedural / placeholder audio kullanilmaz.
echo.

"%PYTHON%" "%EXECUTOR%" ^
    --prepared "%PREPARED%" ^
    --result "%RESULT%" ^
    --timeout 1800

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo REAL GENERATION: SUCCESS

    if exist "%RESULT%" (
        echo.
        echo Result JSON:
        echo %RESULT%
    )

    echo.
    echo Cikti dosyasi:
    echo %ROOT%output
) else (
    echo REAL GENERATION: FAILED

    if exist "%RESULT%" (
        echo.
        echo Hata raporu:
        type "%RESULT%"
    )
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%