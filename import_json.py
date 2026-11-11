#!/usr/bin/env python3
"""
Tainted Grail Localization Tools - Compile JSON to Blobs

Converts an edited JSON localization file back into binary
positions.blob and strings.blob formats ready for repacking.
"""

import argparse
import json
import os
import struct
import sys

def compile_json_to_blobs(json_path, out_dir):
    if not os.path.exists(json_path):
        print(f"Error: JSON file '{json_path}' not found!", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loading '{json_path}'...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Support both list of objects and key-value mapping dict
    items_by_id = {}
    if isinstance(data, list):
        for entry in data:
            if "id" in entry and "text" in entry:
                items_by_id[int(entry["id"])] = str(entry["text"])
    elif isinstance(data, dict):
        for k, v in data.items():
            if str(k).isdigit():
                items_by_id[int(k)] = str(v)
            elif isinstance(v, dict) and "text" in v and "id" in v:
                items_by_id[int(v["id"])] = str(v["text"])
    else:
        print("Error: Unsupported JSON format. Expected list of entries or key-value dict.", file=sys.stderr)
        sys.exit(1)
        
    if not items_by_id:
        print("Error: No valid entries found in JSON file!", file=sys.stderr)
        sys.exit(1)
        
    total_entries = max(items_by_id.keys()) + 1
    print(f"Found {len(items_by_id)} strings (total index span: 0 to {total_entries - 1}).")
    
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
    print(f"Files saved to: {out_dir}")

def main():
    parser = argparse.ArgumentParser(description="Compile JSON translation into Tainted Grail binary blobs.")
    parser.add_argument("--json", required=True, help="Path to edited JSON file")
    parser.add_argument("--out-dir", default="build", help="Output directory for blobs (default: 'build')")
    
    args = parser.parse_args()
    compile_json_to_blobs(args.json, args.out_dir)

if __name__ == "__main__":
    main()
