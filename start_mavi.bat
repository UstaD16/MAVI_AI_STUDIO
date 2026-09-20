@echo off
setlocal EnableExtensions

title MAVI AI STUDIO

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "APP=%ROOT%app.py"

echo ============================================================
echo MAVI AI STUDIO
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [ERROR] Ana virtual environment bulunamadi.
    echo.
    echo Beklenen:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%APP%" (
    echo [ERROR] app.py bulunamadi.
    echo.
    pause
    exit /b 1
)

echo MAVI AI STUDIO baslatiliyor...
echo.
echo Python:
"%PYTHON%" --version
echo.

cd /d "%ROOT%"

"%PYTHON%" "%APP%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================
echo MAVI AI STUDIO KAPANDI
echo EXIT CODE: %EXIT_CODE%
echo ============================================================
echo.

if not "%EXIT_CODE%"=="0" (
    echo Program hata koduyla kapandi.
    echo.
    pause
)

exit /b %EXIT_CODE%