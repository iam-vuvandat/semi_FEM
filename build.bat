@echo off
:: ============================================================
:: Project: semiFEM_Solver
:: Author: Vu Van Dat (HUST)
:: Description: Packaging Python script to EXE with PyInstaller
:: ============================================================

title Build semiFEM Solver - PyInstaller
color 0A
set EXE_NAME=semiFEM_Solver

echo [+] KHOI DONG QUA TRINH DONG GOI...
echo ------------------------------------------------------------

echo [-] Dang xoa thu muc build/dist cu...
if exist build rd /s /q build
if exist dist rd /s /q dist


echo [+] Dang thuc thi PyInstaller...
pyinstaller --noconfirm --console --clean ^
 --name "%EXE_NAME%" ^
 --icon "src/ui/assets/logo.ico" ^
 --add-data "src;src" ^
 --paths "src" ^
 --collect-submodules scipy ^
 --collect-all pyvista ^
 --collect-all vtk ^
 --collect-all pyvistaqt ^
 --hidden-import scipy.sparse.csgraph._validation ^
 --hidden-import scipy.special._cdflib ^
 --hidden-import PyQt5.sip ^
 --exclude-module PySide2 ^
 --exclude-module PySide6 ^
 main.py


echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] File EXE da duoc tao tai: \dist\%EXE_NAME%.exe
) else (
    echo [ERROR] Qua trinh build gap loi! Vui long kiem tra log.
)

echo ------------------------------------------------------------
echo Bam phim bat ky de ket thuc.
pause >nul