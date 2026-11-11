#!/usr/bin/env python3
"""
Tainted Grail Localization Tools - Batch Auto-Translator

Automatically translates extracted strings from English into any target language
using Google Translate (zero external dependencies, standard library only).
Includes batch chunking, progress bar, rate-limit backoff, and automatic checkpoint/resume.
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def translate_batch(texts, target_lang, source_lang="en", max_retries=5):
    """Translates a batch of texts separated by a custom separator."""
    if not texts:
        return []
    
    # Filter out empty or whitespace-only lines to save queries
    filtered_indices = []
    to_translate = []
    for idx, t in enumerate(texts):
        if t and t.strip():
            filtered_indices.append(idx)
            # Replace inner newlines so our batch delimiter is safe
            to_translate.append(t.replace("\r\n", " \\n ").replace("\n", " \\n "))
            
    if not to_translate:
        return texts
        
    delimiter = "\n----TG_DELIM----\n"
    combined_query = delimiter.join(to_translate)
    
    url = (
        f"https://translate.googleapis.com/translate_a/single?client=gtx"
        f"&sl={source_lang}&tl={target_lang}&dt=t"
        f"&q={urllib.parse.quote(combined_query)}"
    )
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw_data = resp.read().decode('utf-8')
                parsed = json.loads(raw_data)
                
            translated_combined = "".join(segment[0] for segment in parsed[0] if segment and segment[0])
            parts = translated_combined.split("----TG_DELIM----")
            
            # Map back
            results = list(texts)
            for i, part in enumerate(parts):
                if i < len(filtered_indices):
                    orig_idx = filtered_indices[i]
                    # Restore newlines
                    cleaned = part.strip()
                    cleaned = cleaned.replace("\\n", "\n").replace("\\ n", "\n")
                    results[orig_idx] = cleaned
            return results
            
        except Exception as e:
            wait_time = 2 * (attempt + 1)
            print(f" [!] Request error ({e}). Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
            time.sleep(wait_time)
            
    print(f" [!] Batch failed after {max_retries} attempts. Keeping original text for this batch.")
    return texts

def run_auto_translate(input_json, target_lang, output_json, batch_size=20):
    if not os.path.exists(input_json):
        print(f"Error: Input JSON '{input_json}' not found!", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loading '{input_json}'...")
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    total_count = len(data)
    print(f"Loaded {total_count} strings. Target language: '{target_lang}'.")
    
    # Check for existing checkpoint
    checkpoint_file = f"{output_json}.checkpoint"
    translated_map = {}
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                translated_map = json.load(f)
            print(f"Found checkpoint! Resuming with {len(translated_map)} already translated lines.")
        except Exception:
            translated_map = {}
            
    start_time = time.time()
    
    # Process in batches
    for i in range(0, total_count, batch_size):
        chunk = data[i : i + batch_size]
        
        # Check if already fully in checkpoint
        needed_indices = []
        needed_texts = []
        for idx_in_chunk, item in enumerate(chunk):
            str_id = str(item["id"])
            if str_id not in translated_map:
                needed_indices.append(idx_in_chunk)
                needed_texts.append(item.get("text", ""))
                
        if needed_texts:
            translated_texts = translate_batch(needed_texts, target_lang=target_lang)
            for k, trans in enumerate(translated_texts):
                orig_item = chunk[needed_indices[k]]
                translated_map[str(orig_item["id"])] = trans
                
            # Periodic checkpoint save every 100 items
            if len(translated_map) % 100 < batch_size:
                with open(checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump(translated_map, f, ensure_ascii=False)
                    
            # Polite pause to prevent IP rate-limiting
            time.sleep(0.3)
            
        progress = min(i + batch_size, total_count)
        pct = (progress / total_count) * 100
        elapsed = time.time() - start_time
        print(f"\r Progress: {progress}/{total_count} ({pct:.1f}%) | Translated: {len(translated_map)}", end="", flush=True)
        
    print("\n\nFinalizing output file...")
    # Build output
    result_data = []
    for item in data:
        str_id = str(item["id"])
        trans_text = translated_map.get(str_id, item.get("text", ""))
        new_item = dict(item)
        new_item["ref_text"] = item.get("text", "")
        new_item["text"] = trans_text
        result_data.append(new_item)
        
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
        
    # Remove checkpoint
    if os.path.exists(checkpoint_file):
        try:
            os.remove(checkpoint_file)
        except Exception:
            pass
            
    print(f"==> Auto-translation complete!")
    print(f"Saved: '{output_json}' ({len(result_data)} lines)")

def main():
    parser = argparse.ArgumentParser(description="Auto-translate Tainted Grail strings to any language.")
    parser.add_argument("--input", default="strings_en.json", help="Input JSON file (default: 'strings_en.json')")
    parser.add_argument("--lang", required=True, help="Target language code (e.g. es, de, fr, it, pl, pt, uk, ja)")
    parser.add_argument("--out", default=None, help="Output JSON path (default: 'strings_<lang>.json')")
    parser.add_argument("--batch-size", type=int, default=20, help="Batch size per translation request (default: 20)")
    
    args = parser.parse_args()
    out_file = args.out or f"strings_{args.lang}.json"
    run_auto_translate(args.input, args.lang, out_file, args.batch_size)

if __name__ == "__main__":
    main()
