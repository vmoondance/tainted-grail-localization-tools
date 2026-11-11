#!/usr/bin/env python3
"""
Tainted Grail: The Fall of Avalon - Unified Localization Toolkit

Provides a simple, all-in-one CLI and interactive menu to extract
and repack game text with a single command.
"""

import argparse
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_cmd(cmd):
    """Executes a command and raises an exception if it fails."""
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {res.returncode}")

def extract_flow(arch_path="languages.arch", lang="en", out_json=None):
    if not os.path.exists(arch_path):
        print(f"\n[ERROR] '{arch_path}' not found!")
        print("Please place the original 'languages.arch' in this folder.\n")
        return False
        
    out_dir = os.path.join(SCRIPT_DIR, "extracted")
    ps1_unpack = os.path.join(SCRIPT_DIR, "unpack_arch.ps1")
    py_export = os.path.join(SCRIPT_DIR, "export_json.py")
    
    if not out_json:
        out_json = f"strings_{lang}.json"
        
    print(f"\n[*] [1/2] Unpacking '{arch_path}' (Language: '{lang}')...")
    ps_cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -File "{ps1_unpack}" -ArchPath "{arch_path}" -OutputDir "{out_dir}" -Lang "{lang}"'
    run_cmd(ps_cmd)
    
    print(f"\n[*] [2/2] Exporting binary blobs to '{out_json}'...")
    py_cmd = f'"{sys.executable}" "{py_export}" --extracted-dir "{out_dir}" --lang "{lang}" --out "{out_json}"'
    run_cmd(py_cmd)
    
    print("\n" + "=" * 60)
    print(f" SUCCESS! Text exported to '{out_json}'.")
    print(" You can now edit and translate this JSON file!")
    print("=" * 60 + "\n")
    return True

def repack_flow(json_path="strings_en.json", target_lang="pl", original_arch="languages.arch", out_arch="build/languages.arch"):
    if not os.path.exists(original_arch):
        print(f"\n[ERROR] Original template '{original_arch}' not found!\n")
        return False
        
    if not os.path.exists(json_path):
        print(f"\n[ERROR] Translation file '{json_path}' not found!\n")
        return False
        
    build_dir = os.path.join(SCRIPT_DIR, "build")
    pos_blob = os.path.join(build_dir, "positions.blob")
    str_blob = os.path.join(build_dir, "strings.blob")
    py_import = os.path.join(SCRIPT_DIR, "import_json.py")
    ps1_repack = os.path.join(SCRIPT_DIR, "repack_arch.ps1")
    
    print(f"\n[*] [1/2] Compiling '{json_path}' to binary blobs...")
    py_cmd = f'"{sys.executable}" "{py_import}" --json "{json_path}" --out-dir "{build_dir}"'
    run_cmd(py_cmd)
    
    print(f"\n[*] [2/2] Repacking into '{out_arch}' (Target language slot: '{target_lang}')...")
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
        print(" [1] Extract & Export game text to JSON (e.g. English)")
        print(" [2] Compile JSON & Repack into languages.arch")
        print(" [3] Exit")
        print("=" * 60)
        
        choice = input("Select an option (1-3): ").strip()
        if choice == "1":
            lang = input("Enter language to extract (default 'en'): ").strip() or "en"
            out_file = f"strings_{lang}.json"
            extract_flow(lang=lang, out_json=out_file)
        elif choice == "2":
            def_json = "strings_translated.json" if os.path.exists("strings_translated.json") else "strings_en.json"
            json_file = input(f"Enter path to your JSON (default '{def_json}'): ").strip() or def_json
            slot = input("Enter target language slot to replace (default 'pl'): ").strip() or "pl"
            repack_flow(json_path=json_file, target_lang=slot)
        elif choice == "3" or choice.lower() == "q":
            print("Goodbye!")
            break
        else:
            print("[!] Invalid option. Please choose 1, 2, or 3.")

def main():
    parser = argparse.ArgumentParser(description="Tainted Grail All-In-One Localization Toolkit")
    subparsers = parser.add_subparsers(dest="command")
    
    # Extract
    ext_parser = subparsers.add_parser("extract", help="Extract and export text from languages.arch to JSON in 1 step")
    ext_parser.add_argument("--arch", default="languages.arch", help="Path to languages.arch")
    ext_parser.add_argument("--lang", default="en", help="Language to extract (en, pl, de, etc.)")
    ext_parser.add_argument("--out", default=None, help="Output JSON filename")
    
    # Repack
    rep_parser = subparsers.add_parser("repack", help="Compile JSON and repack into languages.arch in 1 step")
    rep_parser.add_argument("--json", default="strings_en.json", help="Path to translated JSON")
    rep_parser.add_argument("--arch", default="languages.arch", help="Original languages.arch")
    rep_parser.add_argument("--slot", default="pl", help="Target language slot to replace (default: pl)")
    rep_parser.add_argument("--out", default="build/languages.arch", help="Output languages.arch path")
    
    args = parser.parse_args()
    
    if args.command == "extract":
        extract_flow(arch_path=args.arch, lang=args.lang, out_json=args.out)
    elif args.command == "repack":
        repack_flow(json_path=args.json, target_lang=args.slot, original_arch=args.arch, out_arch=args.out)
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
