# Tainted Grail: The Fall of Avalon - Localization Toolkit

A complete standalone toolset to unpack, export, edit, compile, and repack game text from `languages.arch` in **Tainted Grail: The Fall of Avalon** (Unity).

---

## ⚡ 1-Click Quick Workflow (No Complex Commands!)

### 1. Extract Game Text:
1. Copy `languages.arch` from your game directory into this folder:
   ```
   <GameDir>\Fall of Avalon_Data\StreamingAssets\languages.arch
   ```
2. Double-click **`1_extract_to_json.bat`** (or run `python toolkit.py extract`).
3. You now have **`strings_en.json`** ready for translation!

### 2. Translate:
Open `strings_en.json` and translate the `"text"` fields.

### 3. Repack Mod:
1. Double-click **`2_repack_mod.bat`** (or run `python toolkit.py repack`).
2. Your modded **`build\languages.arch`** is ready!
3. Copy it back to `<GameDir>\Fall of Avalon_Data\StreamingAssets\languages.arch` and select Polish (`pl`) in the game settings to play in your new language!

---

## 🎛️ Interactive CLI Menu

You can also run the unified toolkit menu:
```bash
python toolkit.py
```
```
============================================================
   Tainted Grail: The Fall of Avalon - Localization Toolkit
============================================================
 [1] Extract & Export game text to JSON (e.g. English)
 [2] Compile JSON & Repack into languages.arch
 [3] Exit
============================================================
```

---

## 🔍 Why Can't UABEA Edit Text Directly?

`languages.arch` is an LZ4-compressed Unity AssetBundle. However, the game developers do not use standard Unity `TextAsset` or `MonoBehaviour` objects to store localizations. Instead, the bundle stores raw custom binary blobs for each language:

* **`<lang>/positions.blob`**: Binary index table of 64-bit entries (`uint32 char_offset`, `uint32 char_length`).
* **`<lang>/strings.blob`**: Continuous raw UTF-16LE stream containing all localized text.
* **`keys_positions.blob` & `keys_data.blob`**: Internal string identifier keys mapping every line to its quest, dialogue node, bark, or UI element.

Because these are raw binary files inside the AssetBundle, standard UABEA GUI inspectors cannot parse or edit the text. This toolkit automates the entire workflow.

---

## 📁 Repository Structure

```
tainted-grail-localization-tools/
├── 1_extract_to_json.bat     # [1-Click] Double-click to extract text to JSON
├── 2_repack_mod.bat          # [1-Click] Double-click to compile & repack mod
├── toolkit.py                # All-in-one interactive CLI & automation runner
├── lib/
│   └── AssetsTools.NET.dll   # Managed C# library for Unity AssetBundle manipulation
├── unpack_arch.ps1           # Unpacks languages.arch and extracts language blobs
├── export_json.py            # Converts binary blobs into editable JSON (with keys & ref text)
├── import_json.py            # Compiles edited JSON back into binary positions.blob & strings.blob
├── repack_arch.ps1           # Injects compiled blobs into languages.arch with LZ4 compression
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

### `positions.blob`
* Array of `Record` structures, 8 bytes each.
* `char_offset`: 32-bit unsigned little-endian integer (`uint32`). Specifies the UTF-16 character offset (byte offset = `char_offset * 2`).
* `char_length`: 32-bit unsigned little-endian integer (`uint32`). Specifies character count (byte length = `char_length * 2`).

### `strings.blob`
* Contiguous buffer of UTF-16LE encoded characters.

---

## 📜 Credits & License

* Developed for the **Tainted Grail: The Fall of Avalon** modding and localization community.
* Uses [AssetsTools.NET](https://github.com/nesrak1/AssetsTools.NET) by **nesrak1** (MIT License).
* Licensed under the [MIT License](LICENSE).
