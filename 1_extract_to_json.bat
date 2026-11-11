@echo off
setlocal enabledelayedexpansion
title Tainted Grail - Extract to JSON & CSV
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
echo [*] Step 1/3: Unpacking languages.arch (extracting !LANG_CHOICE! blobs)...
powershell -NoProfile -ExecutionPolicy Bypass -File ".\unpack_arch.ps1" -ArchPath "languages.arch" -OutputDir "extracted" -Lang "!LANG_CHOICE!"
if errorlevel 1 (
    echo [ERROR] Unpacking failed!
    pause
    exit /b 1
)

echo.
echo [*] Step 2/3: Converting binary blobs to JSON...
set OUT_JSON=strings_!LANG_CHOICE!.json
python export_json.py --extracted-dir extracted --lang !LANG_CHOICE! --out "!OUT_JSON!"
if errorlevel 1 (
    echo [ERROR] JSON export failed! Please ensure Python 3 is installed and added to PATH.
    pause
    exit /b 1
)

echo.
echo [*] Step 3/3: Exporting to Excel/Google Sheets CSV...
set OUT_CSV=translation_!LANG_CHOICE!.csv
python export_csv.py --extracted-dir extracted --lang !LANG_CHOICE! --out "!OUT_CSV!"

echo.
echo ============================================================
echo  SUCCESS! Extraction complete.
echo.
echo  Available translation files:
echo  1. !OUT_CSV!  (Open directly in Excel or Google Sheets)
echo  2. !OUT_JSON! (JSON format for text editors or code)
echo.
echo  Tip: You can also run '3_auto_translate.bat' to
echo  automatically translate everything with Google Translate!
echo ============================================================
echo.
pause
