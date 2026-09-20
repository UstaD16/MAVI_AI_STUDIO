@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Inspection

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "INSPECTOR=%ROOT%inspect_pipeline.py"

echo ============================================================
echo MAVI AI STUDIO
echo PIPELINE INSPECTION
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%INSPECTOR%" (
    echo [FAIL] inspect_pipeline.py bulunamadi:
    echo %INSPECTOR%
    echo.
    pause
    exit /b 1
)

cd /d "%ROOT%"

echo Python:
"%PYTHON%" --version
echo.

echo ============================================================
echo INSPECTION
echo ============================================================
echo.

"%PYTHON%" "%INSPECTOR%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo INSPECTION STATUS: READY
) else (
    echo INSPECTION STATUS: NEEDS FIX
    echo.
    echo Detay:
    echo %ROOT%logs\pipeline_inspection.json
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%