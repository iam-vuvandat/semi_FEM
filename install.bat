@echo off
setlocal EnableDelayedExpansion
title Virtual Environment Setup
echo Checking system requirements...

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not found. Installing Python 3.10...
    winget install -e --id Python.Python.3.10 --scope machine
    echo PLEASE RESTART this script after installation.
    pause
    exit /b
)

:: 2. Create .venv
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

:: 3. Upgrade pip
echo Upgrading pip...
.venv\Scripts\python.exe -m pip install --upgrade pip --quiet

:: 4. Install Requirements (Robust Loop)
if exist requirements.txt (
    echo Installing packages from requirements.txt...
    for /f "usebackq delims=" %%i in ("requirements.txt") do (
        set "line=%%i"
        if "!line:~0,1!" neq "#" if "!line!" neq "" (
            echo Processing: %%i
            .venv\Scripts\pip.exe install "%%i" --no-warn-script-location
        )
    )
)

:: 5. Ultimate VS Code Configuration (Handles comments, trailing commas, and existing dirs)
echo Configuring VS Code workspace...
powershell -NoProfile -Command "$d='.vscode'; if(!(Test-Path $d)){New-Item $d -ItemType Directory -Force | Out-Null}; $f='.vscode/settings.json'; $s=if(Test-Path $f){$j=(Get-Content $f -Raw) -replace '//.*','' -replace ',\s*([}\]])','$1'; $j | ConvertFrom-Json}else{New-Object PSObject}; $s | Add-Member -NotePropertyName 'python.defaultInterpreterPath' -NotePropertyValue './.venv/Scripts/python.exe' -Force; $s | Add-Member -NotePropertyName 'python.terminal.activateEnvironment' -NotePropertyValue $true -Force; $s | Add-Member -NotePropertyName 'python.analysis.extraPaths' -NotePropertyValue @('./src') -Force; $s | ConvertTo-Json | Set-Content $f"

echo.
echo [+] Setup finished successfully!
pause