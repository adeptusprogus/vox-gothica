# Vox Gothica installer — Windows (PowerShell 5+).
# Usage:  powershell -ExecutionPolicy Bypass -File install.ps1
$ErrorActionPreference = "Stop"
$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Say($m) { Write-Host "[gothica] $m" }
function Die($m) { Write-Host "[gothica] HERESIS: $m" -ForegroundColor Red; exit 1 }

# find python >= 3.10
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
        Say "  [Environment]::SetEnvironmentVariable('PATH', `$env:PATH + ';$scripts', 'User')"
    }
}

try { gothica versio } catch { Say "Done. Open a new terminal and run: gothica versio" }
Say "For fabricae you also need terraform (winget install Hashicorp.Terraform) or the Docker image."
Say "The Machine Spirit is appeased."
