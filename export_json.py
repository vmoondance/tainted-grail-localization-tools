#!/usr/bin/env python3
"""
Tainted Grail Localization Tools - Export Blobs to JSON

Converts binary localization blobs (positions.blob and strings.blob)
extracted from languages.arch into a structured JSON file.
"""

import argparse
import json
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
        # UTF-16LE characters (2 bytes per character)
        raw = str_bytes[off * 2 : (off + length) * 2]
        text = raw.decode('utf-16le', errors='replace')
        strings.append(text)
    return strings

def main():
    parser = argparse.ArgumentParser(description="Export Tainted Grail localization blobs to JSON.")
    parser.add_argument("--extracted-dir", default="extracted", help="Path to extracted blobs directory (default: 'extracted')")
    parser.add_argument("--lang", default="en", help="Language code to export (e.g. en, pl, de, fr, es, ru) (default: 'en')")
    parser.add_argument("--ref-lang", default=None, help="Optional reference language to include side-by-side (e.g. en)")
    parser.add_argument("--out", default=None, help="Output JSON path (default: 'strings_<lang>.json')")
    
    args = parser.parse_args()
    
    base_dir = os.path.abspath(args.extracted_dir)
    lang_pos = os.path.join(base_dir, args.lang, "positions.blob")
    lang_str = os.path.join(base_dir, args.lang, "strings.blob")
    
    if not os.path.exists(lang_pos) or not os.path.exists(lang_str):
        print(f"Error: Missing language blobs for '{args.lang}' in '{base_dir}'!", file=sys.stderr)
        print(f"Expected: {lang_pos} and {lang_str}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loading '{args.lang}' text strings...")
    lang_texts = parse_blob_table(lang_pos, lang_str)
    print(f"Loaded {len(lang_texts)} strings for '{args.lang}'.")
    
    # Load keys if available
    keys_pos = os.path.join(base_dir, "keys_positions.blob")
    keys_str = os.path.join(base_dir, "keys_data.blob")
    keys = parse_blob_table(keys_pos, keys_str)
    if keys:
        print(f"Loaded {len(keys)} string identification keys.")
    else:
        print("Notice: 'keys_positions.blob' / 'keys_data.blob' not found. IDs will be numeric only.")
        
    # Load reference language if requested
    ref_texts = None
    if args.ref_lang:
        ref_pos = os.path.join(base_dir, args.ref_lang, "positions.blob")
        ref_str = os.path.join(base_dir, args.ref_lang, "strings.blob")
        ref_texts = parse_blob_table(ref_pos, ref_str)
        if ref_texts:
            print(f"Loaded {len(ref_texts)} reference strings for '{args.ref_lang}'.")
            
    out_file = args.out or f"strings_{args.lang}.json"
    
    data = []
    for i, text in enumerate(lang_texts):
        entry = {
            "id": i
        }
        if keys and i < len(keys):
            entry["key"] = keys[i]
        entry["text"] = text
        if ref_texts and i < len(ref_texts):
            entry["ref_text"] = ref_texts[i]
        data.append(entry)
        
    print(f"Writing {len(data)} entries to '{out_file}'...")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Done! Successfully created '{out_file}'.")

if __name__ == "__main__":
    main()
