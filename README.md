# Tainted Grail: The Fall of Avalon - Localization Toolkit

A complete standalone toolset to unpack, export, edit, compile, and repack game text from `languages.arch` in **Tainted Grail: The Fall of Avalon** (Unity).

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
2. **Python 3.8+** (for JSON conversion scripts).

---

## 🚀 Quick Start Guide

### Step 1: Unpack `languages.arch`

Copy `languages.arch` from your game folder (`<GameDir>\Fall of Avalon_Data\StreamingAssets\languages.arch`) into this directory.

To extract all languages and keys:
```powershell
.\unpack_arch.ps1 -ArchPath "languages.arch" -OutputDir "extracted" -Lang "all"
```
Or to extract only English (`en`):
```powershell
.\unpack_arch.ps1 -ArchPath "languages.arch" -OutputDir "extracted" -Lang "en"
```

---

### Step 2: Export to JSON

Run `export_json.py` to convert the binary blobs into a structured JSON file:

```bash
python export_json.py --extracted-dir extracted --lang en --out strings_en.json
```

**Tip:** If you are translating into a new language and want the English text side-by-side as a reference:
```bash
python export_json.py --extracted-dir extracted --lang pl --ref-lang en --out strings_pl.json
```

Each entry in the JSON looks like:
```json
{
  "id": 0,
  "key": "AKS_Emissary_Clement_Controller/choice_text_-2001076184502774882_6770907423a42594aa868f9940af6946",
  "text": "What’s your plan for dealing with Sagremor?",
  "ref_text": "What’s your plan for dealing with Sagremor?"
}
```

---

### Step 3: Translate / Edit Text

Edit the `"text"` fields in the generated `.json` file using your favorite text editor (VS Code, Notepad++, etc.) or automated translation scripts. Keep the `"id"` order intact.

---

### Step 4: Compile JSON Back to Binary Blobs

Compile your translated `.json` file back into binary `positions.blob` and `strings.blob`:

```bash
python import_json.py --json strings_translated.json --out-dir build
```

This generates:
* `build/positions.blob`
* `build/strings.blob`

---

### Step 5: Repack into `languages.arch`

Use `repack_arch.ps1` to inject your modified blobs into any target language slot (e.g. `pl`, `de`, `fr`, `es`, or `en`) and recompress with LZ4:

```powershell
.\repack_arch.ps1 -OriginalArch "languages.arch" -PositionsBlob "build/positions.blob" -StringsBlob "build/strings.blob" -TargetLang "pl" -OutputArch "build/languages.arch"
```

> **Target Language Note:**
> The game allows choosing languages in its settings menu. Overwriting a language slot like `pl` (Polish) or `de` (German) lets players switch to your translation in the game settings by selecting that language.

---

### Step 6: Install into the Game

Copy the newly created `build/languages.arch` into your game directory:
```
<GameDir>\Fall of Avalon_Data\StreamingAssets\languages.arch
```
Launch the game and select your chosen target language in the settings!

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
