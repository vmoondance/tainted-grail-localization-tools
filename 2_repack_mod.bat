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

set INPUT_FILE=
set IS_CSV=0

:: Check for common translation files
for %%F in (translation_*.csv) do (
    set INPUT_FILE=%%F
    set IS_CSV=1
)
for %%F in (strings_*_translated.json strings_translated.json) do (
    if exist "%%F" (
        set INPUT_FILE=%%F
        set IS_CSV=0
    )
)
if "!INPUT_FILE!"=="" (
    for %%F in (strings_*.json) do (
        set INPUT_FILE=%%F
        set IS_CSV=0
    )
)

echo Found translation file: !INPUT_FILE!
echo (Press Enter to use this file, or type custom filename)
set /p USER_FILE="File path: "
if not "!USER_FILE!"=="" (
    set INPUT_FILE=!USER_FILE!
    if "!INPUT_FILE:~-4!"==".csv" (
        set IS_CSV=1
    ) else (
        set IS_CSV=0
    )
)

if not exist "!INPUT_FILE!" (
    echo [ERROR] Translation file '!INPUT_FILE!' not found!
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
echo [*] Step 1/2: Compiling '!INPUT_FILE!' to binary blobs...
if "!IS_CSV!"=="1" (
    python import_csv.py --csv "!INPUT_FILE!" --out-dir "build"
) else (
    python import_json.py --json "!INPUT_FILE!" --out-dir "build"
)
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
