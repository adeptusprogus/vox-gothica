# Vox Gothica installer — Windows (PowerShell 5+).
#
# Default: download pre-built binary from GitHub Releases (no Python).
#
#   irm https://raw.githubusercontent.com/adeptusprogus/vox-gothica/main/vox-gothica/install.ps1 | iex
#
# Options:
#   -Version v0.2.0    specific release (default: latest)
#   -FromSource        build via pip/pipx (needs Python 3.10+)
param(
    [string]$Version = "",
    [switch]$FromSource
)

$ErrorActionPreference = "Stop"
$Repo = "adeptusprogus/vox-gothica"
$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\gothica"
$ExePath = Join-Path $InstallDir "gothica.exe"

function Say($m) { Write-Host "[gothica] $m" }
function Die($m) { Write-Host "[gothica] HERESIS: $m" -ForegroundColor Red; exit 1 }

function Get-ReleaseTag {
    if ($Version) { return $Version }
    $r = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest"
    return $r.tag_name
}

function Install-Binary {
    $tag = Get-ReleaseTag
    $asset = "gothica-windows-amd64.exe"
    $url = "https://github.com/$Repo/releases/download/$tag/$asset"
    Say "Fetching $tag -> $asset ..."
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    Invoke-WebRequest -Uri $url -OutFile $ExePath
    Say "Installed: $ExePath"
}

function Install-FromSource {
    $py = $null
    foreach ($cand in @("py -3", "python3", "python")) {
        try {
            $v = Invoke-Expression "$cand -c `"import sys;print('%d.%d'%sys.version_info[:2])`"" 2>$null
            if ($v -and ([version]$v -ge [version]"3.10")) { $py = $cand; break }
        } catch { }
    }
    if (-not $py) { Die "Python >= 3.10 not found. Install from https://python.org or 'winget install Python.Python.3.12'." }
    Say "Python found ($py)"
    if (Get-Command pipx -ErrorAction SilentlyContinue) {
        Say "Consecrating via pipx ..."
        pipx install --force $Dir
    } else {
        Say "Consecrating via pip --user ..."
        Invoke-Expression "$py -m pip install --user --quiet --upgrade `"$Dir`""
        $scripts = Invoke-Expression "$py -c `"import sysconfig;print(sysconfig.get_path('scripts', scheme='nt_user'))`""
        if ($env:PATH -notlike "*$scripts*") {
            Say "NOTE: add to PATH: $scripts"
        }
    }
}

function Ensure-Path {
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($userPath -notlike "*$InstallDir*") {
        [Environment]::SetEnvironmentVariable("PATH", "$userPath;$InstallDir", "User")
        $env:PATH = "$env:PATH;$InstallDir"
        Say "Added $InstallDir to user PATH (open a new terminal if gothica is not found)."
    }
}

if ($FromSource) {
    Install-FromSource
} else {
    Install-Binary
    Ensure-Path
}

try {
    if (Test-Path $ExePath) {
        & $ExePath versio
    } else {
        gothica versio
    }
} catch {
    Say "Done. Open a new terminal and run: gothica versio"
}

Say "For fabricae you also need terraform (winget install Hashicorp.Terraform) or the Docker image."
Say "The Machine Spirit is appeased."
