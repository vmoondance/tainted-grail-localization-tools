@echo off
setlocal enabledelayedexpansion
title Tainted Grail - Auto-Translator
cd /d "%~dp0"

echo ============================================================
echo   Tainted Grail Localization Tools - Batch Auto-Translator
echo ============================================================
echo.

if not exist "strings_en.json" (
    echo [ERROR] 'strings_en.json' not found!
    echo Please run '1_extract_to_json.bat' first to extract game text.
    echo.
    pause
    exit /b 1
)

echo Enter target language code for translation:
echo Examples:
echo   es  - Spanish
echo   de  - German
echo   fr  - French
echo   it  - Italian
echo   pt  - Portuguese
echo   uk  - Ukrainian
echo   pl  - Polish
echo   ja  - Japanese
echo.
set /p TARGET_LANG="Language code: "

if "!TARGET_LANG!"=="" (
    echo [ERROR] No language code provided!
    pause
    exit /b 1
)

set OUT_JSON=strings_!TARGET_LANG!.json

echo.
echo [*] Starting automated translation from English to !TARGET_LANG!...
echo Progress is saved periodically. If interrupted, run this script again to resume.
echo.
python auto_translate.py --input strings_en.json --lang !TARGET_LANG! --out "!OUT_JSON!"
if errorlevel 1 (
    echo [ERROR] Translation encountered an error.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  SUCCESS!
echo  Auto-translated file created: !OUT_JSON!
echo.
echo  Next steps:
echo  1. You can review and edit '!OUT_JSON!' in any editor.
echo  2. Run '2_repack_mod.bat' to build your languages.arch!
echo ============================================================
echo.
pause
