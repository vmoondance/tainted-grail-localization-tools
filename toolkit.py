#!/usr/bin/env python3
"""
Tainted Grail: The Fall of Avalon - Unified Localization Toolkit

Provides an all-in-one CLI and interactive menu to extract, translate,
and repack game text with full support for JSON, CSV (Excel/Sheets),
and batch automated translation.
"""

import argparse
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {res.returncode}")

def extract_flow(arch_path="languages.arch", lang="en"):
    if not os.path.exists(arch_path):
        print(f"\n[ERROR] '{arch_path}' not found! Place original languages.arch in this folder.\n")
        return False
        
    out_dir = os.path.join(SCRIPT_DIR, "extracted")
    ps1_unpack = os.path.join(SCRIPT_DIR, "unpack_arch.ps1")
    py_export_json = os.path.join(SCRIPT_DIR, "export_json.py")
    py_export_csv = os.path.join(SCRIPT_DIR, "export_csv.py")
    
    out_json = f"strings_{lang}.json"
    out_csv = f"translation_{lang}.csv"
    
    print(f"\n[*] [1/3] Unpacking '{arch_path}' (Language: '{lang}')...")
    ps_cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -File "{ps1_unpack}" -ArchPath "{arch_path}" -OutputDir "{out_dir}" -Lang "{lang}"'
    run_cmd(ps_cmd)
    
    print(f"\n[*] [2/3] Exporting binary blobs to '{out_json}'...")
    run_cmd(f'"{sys.executable}" "{py_export_json}" --extracted-dir "{out_dir}" --lang "{lang}" --out "{out_json}"')
    
    print(f"\n[*] [3/3] Exporting to Excel/Google Sheets CSV '{out_csv}'...")
    run_cmd(f'"{sys.executable}" "{py_export_csv}" --extracted-dir "{out_dir}" --lang "{lang}" --out "{out_csv}"')
    
    print("\n" + "=" * 60)
    print(" SUCCESS! Files generated:")
    print(f" 1. {out_csv}  (Open in Microsoft Excel or Google Sheets)")
    print(f" 2. {out_json} (JSON format)")
    print("=" * 60 + "\n")
    return True

def auto_translate_flow(lang):
    in_json = "strings_en.json"
    if not os.path.exists(in_json):
        print(f"\n[ERROR] '{in_json}' not found! Please run Extract first.\n")
        return False
    out_json = f"strings_{lang}.json"
    py_auto = os.path.join(SCRIPT_DIR, "auto_translate.py")
    print(f"\n[*] Starting batch auto-translation into '{lang}'...")
    run_cmd(f'"{sys.executable}" "{py_auto}" --input "{in_json}" --lang "{lang}" --out "{out_json}"')
    return True

def repack_flow(input_file, target_lang="pl", original_arch="languages.arch", out_arch="build/languages.arch"):
    if not os.path.exists(original_arch):
        print(f"\n[ERROR] Original template '{original_arch}' not found!\n")
        return False
        
    if not os.path.exists(input_file):
        print(f"\n[ERROR] Translation file '{input_file}' not found!\n")
        return False
        
    build_dir = os.path.join(SCRIPT_DIR, "build")
    pos_blob = os.path.join(build_dir, "positions.blob")
    str_blob = os.path.join(build_dir, "strings.blob")
    ps1_repack = os.path.join(SCRIPT_DIR, "repack_arch.ps1")
    
    print(f"\n[*] [1/2] Compiling '{input_file}' to binary blobs...")
    if input_file.lower().endswith(".csv"):
        py_import = os.path.join(SCRIPT_DIR, "import_csv.py")
        run_cmd(f'"{sys.executable}" "{py_import}" --csv "{input_file}" --out-dir "{build_dir}"')
    else:
        py_import = os.path.join(SCRIPT_DIR, "import_json.py")
        run_cmd(f'"{sys.executable}" "{py_import}" --json "{input_file}" --out-dir "{build_dir}"')
        
    print(f"\n[*] [2/2] Repacking into '{out_arch}' (Slot: '{target_lang}')...")
    ps_cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -File "{ps1_repack}" -OriginalArch "{original_arch}" -PositionsBlob "{pos_blob}" -StringsBlob "{str_blob}" -TargetLang "{target_lang}" -OutputArch "{out_arch}"'
    run_cmd(ps_cmd)
    
    print("\n" + "=" * 60)
    print(f" SUCCESS! Modded bundle created at '{out_arch}'.")
    print(f" Copy '{out_arch}' to your game's StreamingAssets folder,")
    print(f" then choose language '{target_lang}' in the game settings.")
    print("=" * 60 + "\n")
    return True

def interactive_menu():
    while True:
        print("=" * 60)
        print("   Tainted Grail: The Fall of Avalon - Localization Toolkit")
        print("=" * 60)
        print(" [1] Extract game text to Excel CSV & JSON")
        print(" [2] Auto-Translate all text with Google Translate (Batch)")
        print(" [3] Compile CSV/JSON & Repack into languages.arch")
        print(" [4] Exit")
        print("=" * 60)
        
        choice = input("Select an option (1-4): ").strip()
        if choice == "1":
            lang = input("Enter source language to extract (default 'en'): ").strip() or "en"
            extract_flow(lang=lang)
        elif choice == "2":
            lang = input("Enter target language code (e.g. es, de, fr, it, uk, pl, ja): ").strip()
            if lang:
                auto_translate_flow(lang=lang)
        elif choice == "3":
            # Autodetect
            candidates = [f for f in os.listdir(SCRIPT_DIR) if f.startswith("translation_") and f.endswith(".csv")]
            candidates += [f for f in os.listdir(SCRIPT_DIR) if f.startswith("strings_") and f.endswith(".json") and f != "strings_en.json"]
            def_file = candidates[0] if candidates else "strings_en.json"
            inp = input(f"Enter path to your CSV or JSON (default '{def_file}'): ").strip() or def_file
            slot = input("Enter target language slot to replace (default 'pl'): ").strip() or "pl"
            repack_flow(input_file=inp, target_lang=slot)
        elif choice == "4" or choice.lower() == "q":
            print("Goodbye!")
            break

def main():
    parser = argparse.ArgumentParser(description="Tainted Grail Localization Toolkit")
    subparsers = parser.add_subparsers(dest="command")
    
    # Extract
    ext_parser = subparsers.add_parser("extract", help="Extract text to JSON and Excel CSV")
    ext_parser.add_argument("--arch", default="languages.arch")
    ext_parser.add_argument("--lang", default="en")
    
    # Auto-translate
    auto_parser = subparsers.add_parser("auto-translate", help="Batch auto-translate to another language")
    auto_parser.add_argument("--lang", required=True)
    
    # Repack
    rep_parser = subparsers.add_parser("repack", help="Compile and repack into languages.arch")
    rep_parser.add_argument("--file", required=True, help="Input CSV or JSON path")
    rep_parser.add_argument("--arch", default="languages.arch")
    rep_parser.add_argument("--slot", default="pl")
    rep_parser.add_argument("--out", default="build/languages.arch")
    
    args = parser.parse_args()
    
    if args.command == "extract":
        extract_flow(arch_path=args.arch, lang=args.lang)
    elif args.command == "auto-translate":
        auto_translate_flow(lang=args.lang)
    elif args.command == "repack":
        repack_flow(input_file=args.file, target_lang=args.slot, original_arch=args.arch, out_arch=args.out)
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
