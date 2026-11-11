# Tainted Grail: The Fall of Avalon - Localization Toolkit

A complete standalone toolset to unpack, export, translate, and repack game text from `languages.arch` in **Tainted Grail: The Fall of Avalon** (Unity).

Supports **Microsoft Excel**, **Google Sheets**, **JSON**, and **automated batch translation** with zero setup.

---

## ⚡ 1-Click Quick Workflow

### 1. Extract Game Text:
1. Copy `languages.arch` from your game directory into this folder:
   ```
   <GameDir>\Fall of Avalon_Data\StreamingAssets\languages.arch
   ```
2. Double-click **`1_extract_to_json.bat`**.
3. It generates two formats:
   * **`translation_en.csv`** — Open directly in **Microsoft Excel** or **Google Sheets**!
   * **`strings_en.json`** — Standard JSON format for text editors or scripts.

---

### 2. Choose Your Translation Method:

#### Option A: Edit in Excel / Google Sheets (Recommended for humans & teams)
1. Open `translation_en.csv` in Excel or upload it to Google Sheets.
2. Fill in the **`Translation`** column with your text.
3. *Tip in Google Sheets:* You can use `=GOOGLETRANSLATE(C2, "en", "es")` to instantly translate lines!
4. Save the file.

#### Option B: Automated Full Translation (1-Click)
1. Double-click **`3_auto_translate.bat`**.
2. Enter your language code (e.g., `es` for Spanish, `de` for German, `fr` for French, `it` for Italian, `uk` for Ukrainian, etc.).
3. The tool automatically translates the entire game in batches using Google Translate and saves `strings_<lang>.json`!

#### Option C: Edit in JSON
Open `strings_en.json` in VS Code or Notepad++ and edit the `"text"` fields.

---

### 3. Repack Mod:
1. Double-click **`2_repack_mod.bat`**.
2. It compiles your translation (CSV or JSON) and repacks it into **`build\languages.arch`** with LZ4 compression.
3. Copy `build\languages.arch` to your game directory:
   ```
   <GameDir>\Fall of Avalon_Data\StreamingAssets\languages.arch
   ```
4. In game settings, select Polish (`pl`) or your chosen language slot, and enjoy!

---

## 🎛️ Interactive CLI Menu

You can also run the unified toolkit menu from terminal:
```bash
python toolkit.py
```
```
============================================================
   Tainted Grail: The Fall of Avalon - Localization Toolkit
============================================================
 [1] Extract game text to Excel CSV & JSON
 [2] Auto-Translate all text with Google Translate (Batch)
 [3] Compile CSV/JSON & Repack into languages.arch
 [4] Exit
============================================================
```

---

## 📁 Repository Structure

```
tainted-grail-localization-tools/
├── 1_extract_to_json.bat     # [1-Click] Double-click to extract text to CSV & JSON
├── 2_repack_mod.bat          # [1-Click] Double-click to compile & repack mod
├── 3_auto_translate.bat      # [1-Click] Automated batch translation into any language
├── toolkit.py                # All-in-one interactive CLI & automation runner
├── export_csv.py             # Exports blobs to UTF-8 BOM CSV for Excel / Google Sheets
├── import_csv.py             # Compiles translated CSV back into binary blobs
├── export_json.py            # Converts binary blobs into editable JSON
├── import_json.py            # Compiles edited JSON back into binary blobs
├── auto_translate.py         # Batch auto-translator with resume/checkpointing
├── repack_arch.ps1           # Injects compiled blobs into languages.arch with LZ4 compression
├── unpack_arch.ps1           # Unpacks languages.arch AssetBundle
├── lib/
│   └── AssetsTools.NET.dll   # Managed C# library for Unity AssetBundle manipulation
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚙️ Prerequisites

1. **Windows 10 / 11** with PowerShell 5.1+ (built-in).
2. **Python 3.8+** (installed and added to system PATH).

---

## 🔬 Binary Format Specification

For developers wishing to write their own parsers:

* **`positions.blob`**: Array of 8-byte binary records:
  - `char_offset` (`uint32`, little-endian): UTF-16 character offset (byte offset = `char_offset * 2`).
  - `char_length` (`uint32`, little-endian): Character count (byte length = `char_length * 2`).
* **`strings.blob`**: Continuous buffer of raw UTF-16LE characters.
* **`keys_positions.blob` & `keys_data.blob`**: Same binary format mapping IDs to internal game keys (dialogue nodes, quests, items).

---

## 📜 Credits & License

* Developed for the **Tainted Grail: The Fall of Avalon** modding and localization community.
* Uses [AssetsTools.NET](https://github.com/nesrak1/AssetsTools.NET) by **nesrak1** (MIT License).
* Licensed under the [MIT License](LICENSE).
