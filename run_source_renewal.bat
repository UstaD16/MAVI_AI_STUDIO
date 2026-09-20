@echo off
setlocal EnableExtensions EnableDelayedExpansion

title MAVI AI STUDIO - SOURCE RENEWAL

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "APP=%ROOT%app.py"

set "SOURCE_DIR=C:\Users\ORGOC\Desktop\MAVI'NİN MÜZİKLERİ\Kaynak"
set "OUTPUT_DIR=C:\Users\ORGOC\Desktop\MAVI'NİN MÜZİKLERİ\Üretilen"

echo ============================================================
echo MAVI AI STUDIO
echo REAL SOURCE RENEWAL
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%APP%" (
    echo [FAIL] app.py bulunamadi.
    echo.
    pause
    exit /b 1
)

if not exist "%SOURCE_DIR%" (
    echo [FAIL] Kaynak klasoru bulunamadi:
    echo %SOURCE_DIR%
    echo.
    pause
    exit /b 1
)

if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
)

echo ============================================================
echo KAYNAK DOSYALARI
echo ============================================================
echo.

set /a COUNT=0

for %%F in (
    "%SOURCE_DIR%\*.wav"
    "%SOURCE_DIR%\*.mp3"
    "%SOURCE_DIR%\*.flac"
    "%SOURCE_DIR%\*.ogg"
    "%SOURCE_DIR%\*.m4a"
) do (
    if exist "%%~F" (
        set /a COUNT+=1
        echo [!COUNT!] %%~nxF
    )
)

if "%COUNT%"=="0" (
    echo [FAIL] Kaynak klasorunde desteklenen audio bulunamadi.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo RENEWAL KOMUTU
echo ============================================================
echo.

echo Bu akis kaynak muzigi korumaya odaklanir.
echo.
echo Ornek:
echo   eski kaydi toparla, davul ve bas gitar ekle
echo.
echo veya:
echo   zurna daha sert, sol klarnet ekle
echo.
echo veya:
echo   bu parcayi bozma, sadece davul ve bas gitar ekle
echo.

set "SELECTED_SOURCE="

for %%F in (
    "%SOURCE_DIR%\*.wav"
    "%SOURCE_DIR%\*.mp3"
    "%SOURCE_DIR%\*.flac"
    "%SOURCE_DIR%\*.ogg"
    "%SOURCE_DIR%\*.m4a"
) do (
    if exist "%%~F" if not defined SELECTED_SOURCE (
        set "SELECTED_SOURCE=%%~F"
    )
)

echo.
echo Secilen kaynak:
echo %SELECTED_SOURCE%
echo.

set "RENEWAL_COMMAND=eski kaydi toparla, davul ve bas gitar ekle; melodiyi, tempoyu, tonu, ritmi ve yore karakterini koru; dogal canli icra hissi"

echo Renewal:
echo %RENEWAL_COMMAND%
echo.

echo ============================================================
echo MAVI ENGINE
echo ============================================================
echo.

cd /d "%ROOT%"

"%PYTHON%" -c ^
"from pathlib import Path; from ai.engine import engine; import json; import sys; src=Path(r'%SELECTED_SOURCE%'); result=engine.run_production(source_path=str(src), command=r'%RENEWAL_COMMAND%'); print(json.dumps(result, ensure_ascii=False, indent=2, default=str))"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo SOURCE RENEWAL: SUCCESS
) else (
    echo SOURCE RENEWAL: FAILED
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%