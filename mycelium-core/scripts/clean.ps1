# ============================================================
# MYCELIUM CORE - Project deep clean (PowerShell)
# ============================================================
# Удаляет: chain-data, logs, exports, runtime, build, dist,
#          __pycache__, .pytest_cache, *.spec, ABI артефакты
# Не трогает: .env, app.cfg, исходный код, тесты, bin/geth.exe
# ============================================================

param(
    [switch]$Force,
    [switch]$Quiet
)

$ErrorActionPreference = "Continue"

# Переход в корневой каталог проекта
Set-Location -Path (Join-Path $PSScriptRoot "..")

function Write-Step {
    param([string]$Text, [string]$Status = "OK")
    $color = switch ($Status) {
        "OK"   { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
        default { "White" }
    }
    Write-Host "  [$Status] " -ForegroundColor $color -NoNewline
    Write-Host $Text
}

function Remove-IfExists {
    param([string]$Path, [string]$Label)
    if (Test-Path $Path) {
        try {
            Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
            Write-Step -Text $Label -Status "OK"
            return $true
        } catch {
            Write-Step -Text "$Label (locked: $($_.Exception.Message))" -Status "FAIL"
            return $false
        }
    }
    return $true
}

# Header
if (-not $Quiet) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  MYCELIUM CORE - Project Clean" -ForegroundColor Cyan
    Write-Host "  Working dir: $(Get-Location)" -ForegroundColor DarkGray
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  WARNING: this will delete:" -ForegroundColor Yellow
    Write-Host "    - data\chain-data\ (blockchain state)"
    Write-Host "    - data\logs\       (all session logs)"
    Write-Host "    - data\exports\    (exported JSON/CSV)"
    Write-Host "    - data\runtime\    (cache)"
    Write-Host "    - build\           (PyInstaller temp)"
    Write-Host "    - dist\            (built EXE)"
    Write-Host "    - contracts\abi\   (compiled artifacts)"
    Write-Host "    - All __pycache__\ folders"
    Write-Host "    - All .pytest_cache, .mypy_cache folders"
    Write-Host "    - *.spec files"
    Write-Host ""
    Write-Host "  WILL NOT TOUCH:" -ForegroundColor Green
    Write-Host "    - .env, app.cfg (your config)"
    Write-Host "    - src\, contracts\VotingCore.sol (source code)"
    Write-Host "    - tests\ (tests)"
    Write-Host "    - bin\geth.exe (binary)"
    Write-Host ""
}

# Confirmation
if (-not $Force) {
    $confirm = Read-Host "Continue? [y/N]"
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-Host "Cancelled." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "Cleaning..." -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray

# Static folders
$targets = @(
    @{Path="data\chain-data\active";    Label="data\chain-data\active"}
    @{Path="data\chain-data\archives";  Label="data\chain-data\archives"}
    @{Path="data\logs\active";          Label="data\logs\active"}
    @{Path="data\logs\archive";         Label="data\logs\archive"}
    @{Path="data\exports";              Label="data\exports"}
    @{Path="data\runtime";              Label="data\runtime"}
    @{Path="build";                     Label="build\"}
    @{Path="dist";                      Label="dist\"}
    @{Path="contracts\abi";             Label="contracts\abi\"}
    @{Path=".pytest_cache";             Label=".pytest_cache"}
)

foreach ($t in $targets) {
    Remove-IfExists -Path $t.Path -Label $t.Label | Out-Null
}

# Recursive __pycache__ removal
$pycacheCount = 0
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop
        $pycacheCount++
    } catch {}
}
Write-Step -Text "Removed $pycacheCount __pycache__ folders" -Status "OK"

# Recursive .mypy_cache removal
$mypyCount = 0
Get-ChildItem -Path . -Recurse -Directory -Filter ".mypy_cache" -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop
        $mypyCount++
    } catch {}
}
if ($mypyCount -gt 0) {
    Write-Step -Text "Removed $mypyCount .mypy_cache folders" -Status "OK"
}

# *.spec files in root
$specFiles = Get-ChildItem -Path . -Filter "*.spec" -File -ErrorAction SilentlyContinue
foreach ($f in $specFiles) {
    try {
        Remove-Item $f.FullName -Force
        Write-Step -Text $f.Name -Status "OK"
    } catch {
        Write-Step -Text "$($f.Name) (locked)" -Status "FAIL"
    }
}

# *.pyc files recursively
$pycCount = 0
Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        Remove-Item $_.FullName -Force -ErrorAction Stop
        $pycCount++
    } catch {}
}
if ($pycCount -gt 0) {
    Write-Step -Text "Removed $pycCount .pyc files" -Status "OK"
}

Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

if (-not $Quiet) {
    Write-Host "To start fresh:" -ForegroundColor Cyan
    Write-Host "  1. python main.py"
    Write-Host "  2. Deploy contract again"
    Write-Host ""
}