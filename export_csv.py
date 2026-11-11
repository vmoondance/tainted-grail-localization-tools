#!/usr/bin/env python3
"""
Tainted Grail Localization Tools - Export Blobs to CSV (Excel / Google Sheets)

Converts binary localization blobs into a clean CSV file that can be opened
directly in Excel, Google Sheets, or LibreOffice Calc.
"""

import argparse
import csv
import os
import struct
import sys

def parse_blob_table(pos_path, str_path):
    if not os.path.exists(pos_path) or not os.path.exists(str_path):
        return None
    
    with open(pos_path, 'rb') as f:
        pos_bytes = f.read()
    with open(str_path, 'rb') as f:
        str_bytes = f.read()
        
    count = len(pos_bytes) // 8
    strings = []
    for i in range(count):
        off, length = struct.unpack_from('<II', pos_bytes, i * 8)
        raw = str_bytes[off * 2 : (off + length) * 2]
        text = raw.decode('utf-16le', errors='replace')
        strings.append(text)
    return strings

def main():
    parser = argparse.ArgumentParser(description="Export Tainted Grail blobs to CSV (Excel / Google Sheets compatible).")
    parser.add_argument("--extracted-dir", default="extracted", help="Path to extracted blobs directory (default: 'extracted')")
    parser.add_argument("--lang", default="en", help="Source language to export (default: 'en')")
    parser.add_argument("--out", default=None, help="Output CSV path (default: 'translation_<lang>.csv')")
    
    args = parser.parse_args()
    
    base_dir = os.path.abspath(args.extracted_dir)
    lang_pos = os.path.join(base_dir, args.lang, "positions.blob")
    lang_str = os.path.join(base_dir, args.lang, "strings.blob")
    
    if not os.path.exists(lang_pos) or not os.path.exists(lang_str):
        print(f"Error: Missing language blobs for '{args.lang}' in '{base_dir}'!", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loading '{args.lang}' text strings...")
    lang_texts = parse_blob_table(lang_pos, lang_str)
    print(f"Loaded {len(lang_texts)} strings.")
    
    # Load keys
    keys_pos = os.path.join(base_dir, "keys_positions.blob")
    keys_str = os.path.join(base_dir, "keys_data.blob")
    keys = parse_blob_table(keys_pos, keys_str)
    
    out_file = args.out or f"translation_{args.lang}.csv"
    
    print(f"Writing CSV with UTF-8 BOM to '{out_file}'...")
    # 'utf-8-sig' ensures Windows Excel opens special characters correctly
    with open(out_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["ID", "Key", f"Original_{args.lang.upper()}", "Translation"])
        
        for i, text in enumerate(lang_texts):
            key = keys[i] if keys and i < len(keys) else f"String_{i}"
            # By default Translation column can be left empty for translator to fill,
            # or pre-filled if desired. We leave it empty so translators easily see what's done.
            writer.writerow([i, key, text, ""])
            
    print(f"Done! Successfully created '{out_file}' ({len(lang_texts)} rows).")
    print(f"-> You can now open this file directly in Microsoft Excel, Google Sheets, or LibreOffice Calc!")

if __name__ == "__main__":
    main()
