@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Stable Audio Path

set "ROOT=%~dp0"

echo ============================================================
echo MAVI AI STUDIO
echo STABLE AUDIO 3 PATH CONFIGURATION
echo ============================================================
echo.

echo Stable Audio 3 TFLite klasor yolunu gir.
echo.
echo Ornek:
echo C:\Users\ORGOC\Desktop\stable-audio-3
echo.
set /p "STABLE_DIR=Stable Audio 3 klasoru: "

if "%STABLE_DIR%"=="" (
    echo.
    echo [ERROR] Klasor yolu bos birakilamaz.
    echo.
    pause
    exit /b 1
)

if not exist "%STABLE_DIR%" (
    echo.
    echo [ERROR] Klasor bulunamadi:
    echo %STABLE_DIR%
    echo.
    pause
    exit /b 1
)

set "SA3=%STABLE_DIR%\optimized\tflite\sa3.bat"

if not exist "%SA3%" (
    echo.
    echo [ERROR] sa3.bat bulunamadi:
    echo %SA3%
    echo.
    echo Beklenen yapi:
    echo optimized\tflite\sa3.bat
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Stable Audio 3 bulundu:
echo %SA3%
echo.

set "MAVI_STABLE_AUDIO_3_DIR=%STABLE_DIR%"
set "MAVI_STABLE_AUDIO_CLI=%SA3%"

setx MAVI_STABLE_AUDIO_3_DIR "%STABLE_DIR%" >nul
setx MAVI_STABLE_AUDIO_CLI "%SA3%" >nul

if errorlevel 1 (
    echo.
    echo [ERROR] Environment variable kaydedilemedi.
    echo.
    pause
    exit /b 1
)

echo ============================================================
echo AYARLAR KAYDEDILDI
echo ============================================================
echo.
echo MAVI_STABLE_AUDIO_3_DIR
echo %STABLE_DIR%
echo.
echo MAVI_STABLE_AUDIO_CLI
echo %SA3%
echo.
echo Yeni CMD/PowerShell oturumunda aktif olacaktir.
echo.
echo ============================================================
echo.

pause
exit /b 0