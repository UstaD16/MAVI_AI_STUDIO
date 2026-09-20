@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Pipeline Status

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "STATUS=%ROOT%mavi_pipeline_status.py"

echo ============================================================
echo MAVI AI STUDIO
echo PIPELINE STATUS
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%STATUS%" (
    echo [FAIL] mavi_pipeline_status.py bulunamadi:
    echo %STATUS%
    echo.
    pause
    exit /b 1
)

cd /d "%ROOT%"

echo Python:
"%PYTHON%" --version
echo.

echo ============================================================
echo PIPELINE STATUS
echo ============================================================
echo.

"%PYTHON%" "%STATUS%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================
echo STATUS FILE:
echo %ROOT%logs\mavi_pipeline_status.json
echo.

if "%EXIT_CODE%"=="0" (
    echo PIPELINE STATUS: READ COMPLETE
) else (
    echo PIPELINE STATUS: READ FAILED
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%