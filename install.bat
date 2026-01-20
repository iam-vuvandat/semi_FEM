@echo off
setlocal EnableDelayedExpansion
title MBGRN Auto-Setup
echo [+] Checking system requirements...

:: 1. Kiem tra Python (Khong dung khoi lenh phuc tap de tranh loi syntax)
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Installing Python 3.10...
    winget install -e --id Python.Python.3.10 --scope machine --silent
    echo Vui long mo lai VS Code sau khi cai dat xong.
    pause
    exit /b
)

:: 2. Tao moi truong ao
if not exist .venv (
    echo [+] Creating virtual environment...
    python -m venv .venv
)

:: 3. Cai dat thu vien (Dung lenh don gian de khong bi loi unexpected)
echo [+] Upgrading pip...
.venv\Scripts\python.exe -m pip install --upgrade pip --quiet

if exist requirements.txt (
    echo [+] Installing packages...
    .venv\Scripts\pip.exe install -r requirements.txt --no-warn-script-location --quiet
)

:: 4. FIX LOI IMPORT & KHOA INTERPRETER
:: Tao file .env de sua loi 'No module named system'
echo PYTHONPATH=src > .env

echo [+] Configuring VS Code...
powershell -NoProfile -Command "$d='.vscode'; if(!(Test-Path $d)){New-Item $d -ItemType Directory -Force | Out-Null}; $f='.vscode/settings.json'; $s=if(Test-Path $f){$j=(Get-Content $f -Raw) -replace '//.*','' -replace ',\s*([}\]])','$1'; $j | ConvertFrom-Json}else{New-Object PSObject}; $s | Add-Member -NotePropertyName 'python.defaultInterpreterPath' -NotePropertyValue '${workspaceFolder}/.venv/Scripts/python.exe' -Force; $s | Add-Member -NotePropertyName 'python.terminal.activateEnvironment' -NotePropertyValue $true -Force; $s | Add-Member -NotePropertyName 'python.envFile' -NotePropertyValue '${workspaceFolder}/.env' -Force; $s | Add-Member -NotePropertyName 'python.analysis.extraPaths' -NotePropertyValue @('./src') -Force; $s | ConvertTo-Json | Set-Content $f"

echo [+] SETUP SUCCESSFUL!
exit /b 0