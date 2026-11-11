<#
.SYNOPSIS
    Repacks modified localization blobs back into Tainted Grail's languages.arch AssetBundle.
.DESCRIPTION
    Injects custom positions.blob and strings.blob for a chosen target language slot (e.g. 'pl', 'de', 'fr', 'en')
    and compresses the final AssetBundle using LZ4.
.PARAMETER OriginalArch
    Path to original (vanilla) languages.arch file.
.PARAMETER PositionsBlob
    Path to modified positions.blob.
.PARAMETER StringsBlob
    Path to modified strings.blob.
.PARAMETER TargetLang
    Language slot inside the bundle to overwrite (default: "pl").
.PARAMETER OutputArch
    Destination path for the newly built languages.arch (default: "build/languages.arch").
.EXAMPLE
    .\repack_arch.ps1 -OriginalArch "languages.arch" -PositionsBlob "build/positions.blob" -StringsBlob "build/strings.blob" -TargetLang "pl" -OutputArch "build/languages.arch"
#>

param(
    [string]$OriginalArch = "languages.arch",
    [string]$PositionsBlob = "build/positions.blob",
    [string]$StringsBlob = "build/strings.blob",
    [string]$TargetLang = "pl",
    [string]$OutputArch = "build/languages.arch"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$dllPath = Join-Path $scriptDir "lib\AssetsTools.NET.dll"

if (-not (Test-Path $dllPath)) {
    Write-Error "AssetsTools.NET.dll not found in '$dllPath'!"
    exit 1
}

if (-not (Test-Path $OriginalArch)) {
    Write-Error "Original AssetBundle '$OriginalArch' not found!"
    exit 1
}

if (-not (Test-Path $PositionsBlob) -or -not (Test-Path $StringsBlob)) {
    Write-Error "Missing blob files! Ensure both '$PositionsBlob' and '$StringsBlob' exist."
    exit 1
}

Add-Type -Path $dllPath

Write-Host "==> Reading original AssetBundle: $OriginalArch..."
$origFs = [System.IO.File]::OpenRead((Resolve-Path $OriginalArch).Path)
$origReader = New-Object AssetsTools.NET.AssetsFileReader($origFs)
$origBundle = New-Object AssetsTools.NET.AssetBundleFile
$origBundle.Read($origReader)

$tempUnpackedPath = Join-Path $scriptDir "temp_unpacked.bundle"
$tempEditedPath = Join-Path $scriptDir "temp_edited.bundle"
if (Test-Path $tempUnpackedPath) { Remove-Item $tempUnpackedPath -Force }
if (Test-Path $tempEditedPath) { Remove-Item $tempEditedPath -Force }

$outDir = Split-Path -Parent $OutputArch
if ($outDir -and -not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}
if (Test-Path $OutputArch) { Remove-Item $OutputArch -Force }

Write-Host "==> Decompressing bundle for editing..."
$tempFs = [System.IO.File]::Create($tempUnpackedPath)
$origBundle.Unpack((New-Object AssetsTools.NET.AssetsFileWriter($tempFs)))
$tempFs.Close()
$origFs.Close()

Write-Host "==> Loading unpacked bundle structure..."
$unpFs = [System.IO.File]::OpenRead($tempUnpackedPath)
$unpReader = New-Object AssetsTools.NET.AssetsFileReader($unpFs)
$unpBundle = New-Object AssetsTools.NET.AssetBundleFile
$unpBundle.Read($unpReader)

Write-Host "==> Preparing replacements for target language slot: '$TargetLang'..."
$posBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $PositionsBlob).Path)
$strBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $StringsBlob).Path)

$targetPosName = "$TargetLang/positions.blob"
$targetStrName = "$TargetLang/strings.blob"

$replacers = New-Object 'System.Collections.Generic.List[AssetsTools.NET.BundleReplacer]'
$repPos = New-Object AssetsTools.NET.BundleReplacerFromMemory($targetPosName, $targetPosName, $false, $posBytes, $posBytes.Length, -1)
$repStr = New-Object AssetsTools.NET.BundleReplacerFromMemory($targetStrName, $targetStrName, $false, $strBytes, $strBytes.Length, -1)

$replacers.Add($repPos)
$replacers.Add($repStr)

Write-Host "==> Writing modified bundle entries..."
$editedFs = [System.IO.File]::Create($tempEditedPath)
$editedWriter = New-Object AssetsTools.NET.AssetsFileWriter($editedFs)
$unpBundle.Write($editedWriter, $replacers, $null)
$editedFs.Close()
$unpFs.Close()

Write-Host "==> Compressing final AssetBundle with LZ4 into '$OutputArch'..."
$editedFs2 = [System.IO.File]::OpenRead($tempEditedPath)
$editedReader2 = New-Object AssetsTools.NET.AssetsFileReader($editedFs2)
$bundleToCompress = New-Object AssetsTools.NET.AssetBundleFile
$bundleToCompress.Read($editedReader2)

$finalFs = [System.IO.File]::Create($OutputArch)
$finalWriter = New-Object AssetsTools.NET.AssetsFileWriter($finalFs)
$bundleToCompress.Pack($editedReader2, $finalWriter, [AssetsTools.NET.AssetBundleCompressionType]::LZ4, $false, $null)

$finalFs.Close()
$editedFs2.Close()

# Clean up temporary bundles
if (Test-Path $tempUnpackedPath) { Remove-Item $tempUnpackedPath -Force }
if (Test-Path $tempEditedPath) { Remove-Item $tempEditedPath -Force }

$resSize = (Get-Item $OutputArch).Length
Write-Host "==> REPACK COMPLETE! Output file: '$OutputArch' ($resSize bytes)"
