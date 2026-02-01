# Inventix AI - UTF-8 Environment File Validator
# ================================================
# This script ensures .env file is in UTF-8 encoding

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " UTF-8 Encoding Validator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path .env) {
    Write-Host "[INFO] Checking .env file encoding..." -ForegroundColor Yellow
    
    # Read and re-save as UTF-8 without BOM
    $content = Get-Content .env -Raw
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText(".env", $content, $utf8NoBom)
    
    Write-Host "[OK] .env file is now UTF-8 encoded (without BOM)" -ForegroundColor Green
} else {
    Write-Host "[WARNING] .env file not found" -ForegroundColor Yellow
    
    if (Test-Path .env.example) {
        Write-Host "[INFO] Creating .env from .env.example..." -ForegroundColor Yellow
        $content = Get-Content .env.example -Raw
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText(".env", $content, $utf8NoBom)
        Write-Host "[CREATED] .env file created (UTF-8 without BOM)" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] .env.example not found!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Ready for Docker deployment!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
