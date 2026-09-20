@echo off
setlocal EnableExtensions EnableDelayedExpansion

title MAVI AI STUDIO - Worker Setup

echo ============================================================
echo MAVI AI STUDIO
echo REAL AUDIO WORKER SETUP
echo ============================================================
echo.

set "ROOT=%~dp0"
set "WORKER_VENV=%ROOT%.worker_venv"

echo [1/6] Python kontrol ediliyor...

where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python Launcher bulunamadi.
    echo Python 3.13 gerekli.
    echo.
    pause
    exit /b 1
)

echo [2/6] Python 3.13 kontrol ediliyor...

py -3.13 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.13 bulunamadi.
    echo Stable Audio worker icin Python 3.13 gerekli.
    echo.
    pause
    exit /b 1
)

py -3.13 --version
echo.

echo [3/6] Worker virtual environment hazirlaniyor...

if not exist "%WORKER_VENV%\Scripts\python.exe" (
    py -3.13 -m venv "%WORKER_VENV%"
    if errorlevel 1 (
        echo [ERROR] Virtual environment olusturulamadi.
        pause
        exit /b 1
    )
)

echo.

echo [4/6] pip guncelleniyor...

"%WORKER_VENV%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] pip guncellenemedi.
    pause
    exit /b 1
)

echo.

echo [5/6] Worker paketleri kuruluyor...

"%WORKER_VENV%\Scripts\python.exe" -m pip install -r "%ROOT%requirements-worker.txt"
if errorlevel 1 (
    echo [ERROR] Worker paketleri kurulurken hata olustu.
    echo.
    pause
    exit /b 1
)

echo.

echo [6/6] Worker dosyalari kontrol ediliyor...

if not exist "%ROOT%worker.py" (
    echo [ERROR] worker.py bulunamadi.
    pause
    exit /b 1
)

if not exist "%ROOT%worker_bridge.py" (
    echo [ERROR] worker_bridge.py bulunamadi.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo WORKER SETUP TAMAMLANDI
echo ============================================================
echo.
echo Python:
"%WORKER_VENV%\Scripts\python.exe" --version
echo.
echo VENV:
echo %WORKER_VENV%
echo.
echo Worker:
echo %ROOT%worker.py
echo.
echo Bridge:
echo %ROOT%worker_bridge.py
echo.
echo ============================================================
echo.

pause
exit /b 0