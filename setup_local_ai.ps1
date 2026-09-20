$ErrorActionPreference = "Stop"

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$THIRD_PARTY = Join-Path $ROOT "third_party"
$SA3_ROOT = Join-Path $THIRD_PARTY "stable-audio-3"
$TFLITE_ROOT = Join-Path $SA3_ROOT "optimized\tflite"

Write-Host ""
Write-Host "============================================================"
Write-Host " MAVI AI STUDIO - LOCAL STABLE AUDIO 3"
Write-Host "============================================================"
Write-Host ""

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[HATA] Git bulunamadi."
    exit 1
}

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "[HATA] Python Launcher (py) bulunamadi."
    exit 1
}

New-Item -ItemType Directory -Force -Path $THIRD_PARTY | Out-Null

# ------------------------------------------------------------
# STABLE AUDIO 3
# ------------------------------------------------------------

if (-not (Test-Path $SA3_ROOT)) {

    Write-Host "[1/4] Stable Audio 3 indiriliyor..."

    git clone `
        https://github.com/Stability-AI/stable-audio-3.git `
        $SA3_ROOT

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[HATA] Stable Audio 3 indirilemedi."
        exit 1
    }

} else {

    Write-Host "[1/4] Stable Audio 3 zaten mevcut."
}

# ------------------------------------------------------------
# TFLITE BACKEND
# ------------------------------------------------------------

if (-not (Test-Path $TFLITE_ROOT)) {

    Write-Host "[HATA] optimized\tflite klasoru bulunamadi."
    exit 1
}

# ------------------------------------------------------------
# PYTHON 3.13
# ------------------------------------------------------------

Write-Host ""
Write-Host "[2/4] Python 3.13 kontrol ediliyor..."

$python313 = $null

try {

    $python313 = (
        py -3.13 -c "import sys; print(sys.executable)"
    ).Trim()

} catch {

    $python313 = $null
}

if (-not $python313) {

    Write-Host ""
    Write-Host "[UYARI] Python 3.13 bulunamadi."
    Write-Host ""
    Write-Host "Stable Audio 3 TFLite backend icin"
    Write-Host "Python 3.13 gerekiyor."
    Write-Host ""
    Write-Host "Script burada durduruldu."
    Write-Host ""

    exit 2
}

Write-Host "Python 3.13 : $python313"

# ------------------------------------------------------------
# VENV + REQUIREMENTS
# ------------------------------------------------------------

Write-Host ""
Write-Host "[3/4] TFLite Windows backend kuruluyor..."

Push-Location $TFLITE_ROOT

try {

    if (Test-Path ".venv") {

        Write-Host "Mevcut .venv kullaniliyor."

    } else {

        & $python313 -m venv .venv

        if ($LASTEXITCODE -ne 0) {
            throw "Python 3.13 venv olusturulamadi."
        }
    }

    $venvPython = Join-Path `
        $TFLITE_ROOT `
        ".venv\Scripts\python.exe"

    Write-Host ""
    Write-Host "pip guncelleniyor..."

    & $venvPython -m pip install --upgrade pip

    if ($LASTEXITCODE -ne 0) {
        throw "pip guncellenemedi."
    }

    if (Test-Path "requirements.txt") {

        Write-Host ""
        Write-Host "TFLite requirements kuruluyor..."

        & $venvPython -m pip install -r requirements.txt

        if ($LASTEXITCODE -ne 0) {
            throw "TFLite requirements kurulumu basarisiz."
        }
    }

} finally {

    Pop-Location
}

# ------------------------------------------------------------
# BACKEND CHECK
# ------------------------------------------------------------

Write-Host ""
Write-Host "[4/4] Backend kontrol ediliyor..."

$launcher = Join-Path `
    $TFLITE_ROOT `
    "sa3.bat"

$backendPython = Join-Path `
    $TFLITE_ROOT `
    ".venv\Scripts\python.exe"

$backendScript = Join-Path `
    $TFLITE_ROOT `
    "scripts\sa3_tflite.py"

if (
    (Test-Path $launcher) -and
    (Test-Path $backendPython) -and
    (Test-Path $backendScript)
) {

    Write-Host ""
    Write-Host "============================================================"
    Write-Host " LOCAL BACKEND HAZIR"
    Write-Host "============================================================"
    Write-Host ""
    Write-Host "Backend:"
    Write-Host $TFLITE_ROOT
    Write-Host ""
    Write-Host "Model:"
    Write-Host "sm-music"
    Write-Host ""
    Write-Host "CPU:"
    Write-Host "TFLite / XNNPACK"
    Write-Host ""

} else {

    Write-Host ""
    Write-Host "[HATA] Backend dosyalari eksik."
    exit 1
}