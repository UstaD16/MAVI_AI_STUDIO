@echo off
setlocal EnableExtensions EnableDelayedExpansion

title MAVI AI STUDIO - Complete Setup

set "ROOT=%~dp0"
set "MAIN_VENV=%ROOT%.venv"
set "WORKER_VENV=%ROOT%.worker_venv"

set "MAIN_PYTHON=%MAIN_VENV%\Scripts\python.exe"
set "WORKER_PYTHON=%WORKER_VENV%\Scripts\python.exe"

echo ============================================================
echo MAVI AI STUDIO
echo COMPLETE SETUP
echo ============================================================
echo.

REM ============================================================
REM PYTHON LAUNCHER
REM ============================================================

echo [1/8] Python Launcher kontrol ediliyor...

where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python Launcher bulunamadi.
    echo.
    pause
    exit /b 1
)

echo [OK] Python Launcher bulundu.
echo.

REM ============================================================
REM PYTHON 3.14
REM ============================================================

echo [2/8] Python 3.14 kontrol ediliyor...

py -3.14 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.14 bulunamadi.
    echo Ana MAVI uygulamasi Python 3.14 ile calisacak.
    echo.
    pause
    exit /b 1
)

py -3.14 --version
echo.

REM ============================================================
REM PYTHON 3.13
REM ============================================================

echo [3/8] Python 3.13 kontrol ediliyor...

py -3.13 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.13 bulunamadi.
    echo Gercek audio worker Python 3.13 gerektiriyor.
    echo.
    pause
    exit /b 1
)

py -3.13 --version
echo.

REM ============================================================
REM MAIN VENV
REM ============================================================

echo [4/8] Ana MAVI environment hazirlaniyor...

if not exist "%MAIN_PYTHON%" (
    echo Ana virtual environment olusturuluyor...
    py -3.14 -m venv "%MAIN_VENV%"

    if errorlevel 1 (
        echo [ERROR] Ana virtual environment olusturulamadi.
        pause
        exit /b 1
    )
)

echo [OK] Ana environment hazir.
echo.

REM ============================================================
REM MAIN PACKAGES
REM ============================================================

echo [5/8] Ana MAVI paketleri kuruluyor...

"%MAIN_PYTHON%" -m pip install --upgrade pip

if errorlevel 1 (
    echo [ERROR] Ana pip guncellenemedi.
    pause
    exit /b 1
)

"%MAIN_PYTHON%" -m pip install -r "%ROOT%requirements.txt"

if errorlevel 1 (
    echo [ERROR] Ana paketler kurulurken hata olustu.
    pause
    exit /b 1
)

echo [OK] Ana paketler hazir.
echo.

REM ============================================================
REM WORKER VENV
REM ============================================================

echo [6/8] Real Audio Worker environment hazirlaniyor...

if not exist "%WORKER_PYTHON%" (
    echo Worker virtual environment olusturuluyor...

    py -3.13 -m venv "%WORKER_VENV%"

    if errorlevel 1 (
        echo [ERROR] Worker virtual environment olusturulamadi.
        pause
        exit /b 1
    )
)

echo [OK] Worker environment hazir.
echo.

REM ============================================================
REM WORKER PACKAGES
REM ============================================================

echo [7/8] Real Audio Worker paketleri kuruluyor...

"%WORKER_PYTHON%" -m pip install --upgrade pip

if errorlevel 1 (
    echo [ERROR] Worker pip guncellenemedi.
    pause
    exit /b 1
)

"%WORKER_PYTHON%" -m pip install -r "%ROOT%requirements-worker.txt"

if errorlevel 1 (
    echo [ERROR] Worker paketleri kurulurken hata olustu.
    pause
    exit /b 1
)

echo [OK] Worker paketleri hazir.
echo.

REM ============================================================
REM DIRECTORY CHECK
REM ============================================================

echo [8/8] MAVI klasorleri ve dosyalari kontrol ediliyor...

if not exist "%ROOT%core" mkdir "%ROOT%core"
if not exist "%ROOT%ai" mkdir "%ROOT%ai"
if not exist "%ROOT%assets" mkdir "%ROOT%assets"
if not exist "%ROOT%audio" mkdir "%ROOT%audio"
if not exist "%ROOT%audio\source" mkdir "%ROOT%audio\source"
if not exist "%ROOT%audio\stems" mkdir "%ROOT%audio\stems"
if not exist "%ROOT%audio\mix" mkdir "%ROOT%audio\mix"
if not exist "%ROOT%audio\master" mkdir "%ROOT%audio\master"
if not exist "%ROOT%output" mkdir "%ROOT%output"
if not exist "%ROOT%logs" mkdir "%ROOT%logs"
if not exist "%ROOT%build" mkdir "%ROOT%build"
if not exist "%ROOT%dist" mkdir "%ROOT%dist"

echo [OK] Klasor yapisi hazir.
echo.

REM ============================================================
REM FINAL STATUS
REM ============================================================

echo ============================================================
echo MAVI AI STUDIO SETUP TAMAMLANDI
echo ============================================================
echo.

echo ANA PYTHON
echo ------------------------------------------------------------
"%MAIN_PYTHON%" --version
echo.

echo WORKER PYTHON
echo ------------------------------------------------------------
"%WORKER_PYTHON%" --version
echo.

echo ANA ENVIRONMENT
echo %MAIN_VENV%
echo.

echo WORKER ENVIRONMENT
echo %WORKER_VENV%
echo.

echo ============================================================
echo DOSYA YAPISI
echo ============================================================
echo.

if exist "%ROOT%config.py" (
    echo [OK] config.py
) else (
    echo [FAIL] config.py
)

if exist "%ROOT%app.py" (
    echo [OK] app.py
) else (
    echo [FAIL] app.py
)

if exist "%ROOT%worker.py" (
    echo [OK] worker.py
) else (
    echo [FAIL] worker.py
)

if exist "%ROOT%worker_bridge.py" (
    echo [OK] worker_bridge.py
) else (
    echo [FAIL] worker_bridge.py
)

if exist "%ROOT%preflight.py" (
    echo [OK] preflight.py
) else (
    echo [FAIL] preflight.py
)

echo.
echo ============================================================
echo HAZIR
echo ============================================================
echo.
echo Ana uygulama:
echo start_mavi.bat
echo.
echo Worker:
echo run_worker.bat
echo.
echo Build:
echo python build_mavi_studio.py
echo.
echo Preflight:
echo python preflight.py
echo.
echo ============================================================
echo.

pause
exit /b 0