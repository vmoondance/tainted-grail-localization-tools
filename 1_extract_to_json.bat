@echo off
setlocal enabledelayedexpansion
title Tainted Grail - Extract to JSON
cd /d "%~dp0"

echo ============================================================
echo   Tainted Grail Localization Tools - 1-Click Extractor
echo ============================================================
echo.

if not exist "languages.arch" (
    echo [ERROR] 'languages.arch' not found in this folder!
    echo Please copy 'languages.arch' from:
    echo   ^<GameDir^>\Fall of Avalon_Data\StreamingAssets\languages.arch
    echo into this directory and run this script again.
    echo.
    pause
    exit /b 1
)

set LANG_CHOICE=en
echo Default language to extract is English [en].
set /p USER_LANG="Enter language code to extract (press Enter for 'en', or type pl, de, fr, es, ru): "
if not "!USER_LANG!"=="" set LANG_CHOICE=!USER_LANG!

echo.
echo [*] Step 1/2: Unpacking languages.arch (extracting !LANG_CHOICE! blobs)...
powershell -NoProfile -ExecutionPolicy Bypass -File ".\unpack_arch.ps1" -ArchPath "languages.arch" -OutputDir "extracted" -Lang "!LANG_CHOICE!"
if errorlevel 1 (
    echo [ERROR] Unpacking failed!
    pause
    exit /b 1
)

echo.
echo [*] Step 2/2: Converting binary blobs to JSON...
set OUT_JSON=strings_!LANG_CHOICE!.json
python export_json.py --extracted-dir extracted --lang !LANG_CHOICE! --out "!OUT_JSON!"
if errorlevel 1 (
    echo [ERROR] JSON export failed! Please ensure Python 3 is installed and added to PATH.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  SUCCESS!
echo  Created: !OUT_JSON!
echo  You can now open this JSON file and translate the text!
echo ============================================================
echo.
pause
