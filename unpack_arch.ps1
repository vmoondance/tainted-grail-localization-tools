<#
.SYNOPSIS
    Unpacks Tainted Grail: The Fall of Avalon "languages.arch" Unity AssetBundle.
.DESCRIPTION
    Extracts binary blobs (positions.blob, strings.blob, keys, smart_tags) from languages.arch.
.PARAMETER ArchPath
    Path to the original languages.arch file (default: "languages.arch").
.PARAMETER OutputDir
    Directory where unpacked blobs will be saved (default: "extracted").
.PARAMETER Lang
    Specific language to extract (e.g. "en", "pl", "de", "ru") or "all" to extract all languages (default: "all").
.EXAMPLE
    .\unpack_arch.ps1 -ArchPath "languages.arch" -OutputDir "extracted" -Lang "en"
#>

param(
    [string]$ArchPath = "languages.arch",
    [string]$OutputDir = "extracted",
    [string]$Lang = "all"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$dllPath = Join-Path $scriptDir "lib\AssetsTools.NET.dll"

if (-not (Test-Path $dllPath)) {
    Write-Error "AssetsTools.NET.dll not found in '$dllPath'!"
    exit 1
}

if (-not (Test-Path $ArchPath)) {
    Write-Error "AssetBundle '$ArchPath' not found!"
    exit 1
}

Add-Type -Path $dllPath

Write-Host "==> Reading AssetBundle: $ArchPath..."
$origFs = [System.IO.File]::OpenRead((Resolve-Path $ArchPath).Path)
$origReader = New-Object AssetsTools.NET.AssetsFileReader($origFs)
$origBundle = New-Object AssetsTools.NET.AssetBundleFile
$origBundle.Read($origReader)

$tempUnpackedPath = Join-Path $scriptDir "temp_unpacked.bundle"
if (Test-Path $tempUnpackedPath) { Remove-Item $tempUnpackedPath -Force }

Write-Host "==> Decompressing LZ4 AssetBundle into memory..."
$tempFs = [System.IO.File]::Create($tempUnpackedPath)
$origBundle.Unpack((New-Object AssetsTools.NET.AssetsFileWriter($tempFs)))
$tempFs.Close()
$origFs.Close()

Write-Host "==> Parsing unpacked bundle structure..."
$unpFs = [System.IO.File]::OpenRead($tempUnpackedPath)
$unpReader = New-Object AssetsTools.NET.AssetsFileReader($unpFs)
$unpBundle = New-Object AssetsTools.NET.AssetBundleFile
$unpBundle.Read($unpReader)

$allFiles = $unpBundle.GetAllFileNames()
Write-Host "==> Total files inside bundle: $($allFiles.Count)"

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$extractedCount = 0

for ($i = 0; $i -lt $allFiles.Count; $i++) {
    $fileName = $allFiles[$i]
    
    # Filter by language if specified
    if ($Lang -ne "all") {
        # Check if it's a global file (keys, gestures) or matches the selected language
        $isGlobal = ($fileName -notmatch "/")
        $isTargetLang = ($fileName -like "$Lang/*")
        if (-not $isGlobal -and -not $isTargetLang) {
            continue
        }
    }
    
    [long]$offset = 0
    [long]$length = 0
    $unpBundle.GetFileRange($i, [ref]$offset, [ref]$length)
    
    $destPath = Join-Path $OutputDir ($fileName -replace '/', '\')
    $destDir = Split-Path -Parent $destPath
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    $unpBundle.DataReader.Position = $offset
    $fileBytes = $unpBundle.DataReader.ReadBytes([int]$length)
    [System.IO.File]::WriteAllBytes($destPath, $fileBytes)
    
    Write-Host " [EXTRACTED] $fileName ($($fileBytes.Length) bytes)"
    $extractedCount++
}

$unpFs.Close()
Remove-Item $tempUnpackedPath -Force

Write-Host "==> Done! Extracted $extractedCount files to '$OutputDir'."
