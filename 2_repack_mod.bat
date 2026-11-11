@echo off
setlocal enabledelayedexpansion
title Tainted Grail - Repack languages.arch
cd /d "%~dp0"

echo ============================================================
echo   Tainted Grail Localization Tools - 1-Click Repacker
echo ============================================================
echo.

if not exist "languages.arch" (
    echo [ERROR] Original 'languages.arch' not found in this folder!
    echo Please keep the original 'languages.arch' here as a base template.
    echo.
    pause
    exit /b 1
)

set INPUT_JSON=
if exist "strings_translated.json" (
    set INPUT_JSON=strings_translated.json
) else if exist "strings_en.json" (
    set INPUT_JSON=strings_en.json
) else (
    echo [!] Enter the path to your translated JSON file:
    set /p INPUT_JSON="JSON file path: "
)

if not exist "!INPUT_JSON!" (
    echo [ERROR] JSON file '!INPUT_JSON!' not found!
    pause
    exit /b 1
)

set TARGET_SLOT=pl
echo.
echo Target game language slot to replace (default is 'pl' [Polish]):
echo Common choices: pl, de, fr, es, it, cs, ru
set /p USER_SLOT="Enter target language slot (press Enter for 'pl'): "
if not "!USER_SLOT!"=="" set TARGET_SLOT=!USER_SLOT!

echo.
echo [*] Step 1/2: Compiling '!INPUT_JSON!' to binary blobs...
python import_json.py --json "!INPUT_JSON!" --out-dir "build"
if errorlevel 1 (
    echo [ERROR] Blob compilation failed!
    pause
    exit /b 1
)

echo.
echo [*] Step 2/2: Injecting blobs into languages.arch and compressing (LZ4)...
powershell -NoProfile -ExecutionPolicy Bypass -File ".\repack_arch.ps1" -OriginalArch "languages.arch" -PositionsBlob "build/positions.blob" -StringsBlob "build/strings.blob" -TargetLang "!TARGET_SLOT!" -OutputArch "build/languages.arch"
if errorlevel 1 (
    echo [ERROR] Repacking failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  SUCCESS!
echo  Modded bundle built: build\languages.arch
echo.
echo  Installation:
echo  1. Copy 'build\languages.arch' to:
echo     ^<GameDir^>\Fall of Avalon_Data\StreamingAssets\languages.arch
echo  2. In game settings, select language: !TARGET_SLOT!
echo ============================================================
echo.
pause
