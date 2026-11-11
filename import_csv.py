#!/usr/bin/env python3
"""
Tainted Grail Localization Tools - Compile CSV to Blobs

Reads an edited CSV file (from Excel or Google Sheets), applies translations,
and compiles binary positions.blob and strings.blob for repacking.
"""

import argparse
import csv
import os
import struct
import sys

def compile_csv_to_blobs(csv_path, out_dir):
    if not os.path.exists(csv_path):
        print(f"Error: CSV file '{csv_path}' not found!", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loading '{csv_path}'...")
    items_by_id = {}
    translated_count = 0
    fallback_count = 0
    
    # Try utf-8-sig first (Excel default), then utf-8
    encoding = 'utf-8-sig'
    try:
        with open(csv_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
    except Exception:
        encoding = 'utf-8'
        with open(csv_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
    # Identify translation column and original column
    trans_col = None
    orig_col = None
    for h in headers:
        hl = h.lower()
        if "translat" in hl or hl in ["target", "text_translated", "custom"]:
            trans_col = h
        elif "origin" in hl or "source" in hl or "english" in hl or hl.startswith("original_"):
            orig_col = h
            
    if not trans_col:
        # Default to the 4th column or last column
        trans_col = headers[-1]
    if not orig_col:
        orig_col = headers[2] if len(headers) > 2 else headers[1]
        
    print(f"Using translation column: '{trans_col}', source column: '{orig_col}'")
    
    with open(csv_path, 'r', encoding=encoding, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_id_raw = row.get("ID") or row.get("id")
            if row_id_raw is None or not str(row_id_raw).strip().isdigit():
                continue
            row_id = int(str(row_id_raw).strip())
            
            trans_text = row.get(trans_col, "").strip()
            orig_text = row.get(orig_col, "")
            
            if trans_text:
                items_by_id[row_id] = trans_text
                translated_count += 1
            else:
                items_by_id[row_id] = orig_text
                fallback_count += 1
                
    if not items_by_id:
        print("Error: No valid data rows found in CSV!", file=sys.stderr)
        sys.exit(1)
        
    total_entries = max(items_by_id.keys()) + 1
    print(f"Parsed {len(items_by_id)} total lines:")
    print(f" - Translated lines: {translated_count}")
    print(f" - Fallback to original: {fallback_count}")
    
    positions_data = bytearray()
    strings_data = bytearray()
    current_char_offset = 0
    
    for i in range(total_entries):
        text = items_by_id.get(i, "")
        encoded_text = text.encode('utf-16le')
        char_len = len(text)
        
        positions_data.extend(struct.pack('<II', current_char_offset, char_len))
        strings_data.extend(encoded_text)
        
        current_char_offset += char_len
        
    os.makedirs(out_dir, exist_ok=True)
    out_pos = os.path.join(out_dir, "positions.blob")
    out_str = os.path.join(out_dir, "strings.blob")
    
    with open(out_pos, 'wb') as f:
        f.write(positions_data)
    with open(out_str, 'wb') as f:
        f.write(strings_data)
        
    print(f"==> Compilation successful!")
    print(f" - positions.blob: {len(positions_data)} bytes ({total_entries} index records)")
    print(f" - strings.blob:   {len(strings_data)} bytes ({current_char_offset} characters in UTF-16LE)")
    print(f"Saved to: {out_dir}")

def main():
    parser = argparse.ArgumentParser(description="Compile CSV translation into Tainted Grail binary blobs.")
    parser.add_argument("--csv", required=True, help="Path to edited CSV file")
    parser.add_argument("--out-dir", default="build", help="Output directory for blobs (default: 'build')")
    
    args = parser.parse_args()
    compile_csv_to_blobs(args.csv, args.out_dir)

if __name__ == "__main__":
    main()
