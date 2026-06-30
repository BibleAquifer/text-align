<#
.SYNOPSIS
    Sync alignment data from C:\git\Clear\alignments-??? into .\data\alignments\
    and update configs/*.yaml to point to the local copy.

.DESCRIPTION
    Run from the project root:
        pwsh scripts\sync_clear_data.ps1

    Copies per language repo:
      - data\targets\**\nt_*.tsv, ot_*.tsv  (translation token TSVs)
      - data\alignments\**\SBLGNT-*-manual.json, WLCM-*-manual.json

    Excludes: alignments-cookiecutter, alignments-from-Randall

    After copying, rewrites configs/*.yaml so that:
        alignments_root: C:/git/Clear
    becomes:
        alignments_root: ./data/alignments
#>

$ErrorActionPreference = 'Stop'

$clearRoot = 'C:\git\Clear'
$dataRoot  = '.\data\alignments'

$excluded = @('alignments-cookiecutter', 'alignments-from-Randall')

$repos = Get-ChildItem $clearRoot -Directory -Filter 'alignments-*' |
         Where-Object { $_.Name -notin $excluded }

foreach ($repo in $repos) {
    Write-Host "`n=== $($repo.Name) ===" -ForegroundColor Cyan

    $src = $repo.FullName
    $dst = Join-Path $dataRoot $repo.Name

    # Target TSVs
    $tSrc = Join-Path $src 'data\targets'
    $tDst = Join-Path $dst 'data\targets'
    if (Test-Path $tSrc) {
        Write-Host '  targets...'
        robocopy $tSrc $tDst nt_*.tsv ot_*.tsv /e /np /ndl /nfl
        if ($LASTEXITCODE -ge 8) { throw "robocopy error (exit $LASTEXITCODE): $tSrc" }
    }

    # Existing alignment JSONs
    $aSrc = Join-Path $src 'data\alignments'
    $aDst = Join-Path $dst 'data\alignments'
    if (Test-Path $aSrc) {
        Write-Host '  alignments...'
        robocopy $aSrc $aDst SBLGNT-*-manual.json WLCM-*-manual.json /e /np /ndl /nfl
        if ($LASTEXITCODE -ge 8) { throw "robocopy error (exit $LASTEXITCODE): $aSrc" }
    }
}

# Update configs/*.yaml
Write-Host "`n--- Updating configs ---" -ForegroundColor Cyan
$old = 'alignments_root: C:/git/Clear'
$new = 'alignments_root: ./data/alignments'
foreach ($f in (Get-ChildItem '.\configs' -Filter '*.yaml')) {
    $content = [System.IO.File]::ReadAllText($f.FullName)
    if ($content.Contains($old)) {
        [System.IO.File]::WriteAllText($f.FullName, $content.Replace($old, $new))
        Write-Host "  Updated: $($f.Name)"
    }
}

Write-Host "`nDone." -ForegroundColor Green
