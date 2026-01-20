# ==========================================================================================
# MBGRN Solver - Automated Setup Script (V2 - Requirements Support)
# ==========================================================================================

Write-Host "--- Starting MBGRN Environment Setup ---" -ForegroundColor Cyan

# 1. Cấp quyền thực thi
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# 2. Kiểm tra/Cài đặt Python 3.10
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Python not found. Installing via winget..." -ForegroundColor Yellow
    winget install -e --id Python.Python.3.10 --scope machine
}

# 3. Tạo môi trường ảo
if (!(Test-Path ".venv")) {
    Write-Host "[+] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
}

# 4. Cài đặt thư viện từ requirements.txt
Write-Host "[+] Installing dependencies..." -ForegroundColor Yellow
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip

if (Test-Path "requirements.txt") {
    Write-Host "[*] Found requirements.txt. Installing listed packages..." -ForegroundColor Green
    & ".\.venv\Scripts\pip.exe" install -r requirements.txt
} else {
    Write-Host "[!] requirements.txt not found. Installing default packages (numpy, scipy)..." -ForegroundColor Cyan
    & ".\.venv\Scripts\pip.exe" install numpy scipy
}

Write-Host "--- Setup Completed! ---" -ForegroundColor Green
Write-Host "Run: .\.venv\Scripts\activate" -ForegroundColor Cyan