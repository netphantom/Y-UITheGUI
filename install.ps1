# Y-UI one-click installer / updater for Windows (Docker Desktop).
#
#   irm https://raw.githubusercontent.com/netphantom/Y-UITheGUI/main/install.ps1 | iex
#
# Downloads the compose files into $env:YUI_DIR (default ~\y-ui), creates .env on first run
# (NVIDIA GPU auto-detected; an existing .env is never overwritten), then pulls and starts Y-UI.
# Run it again at any time to update to the latest images.
# Compatible with Windows PowerShell 5.1 and PowerShell 7+.

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'  # Invoke-WebRequest is very slow with the progress bar

$RepoRaw = if ($env:YUI_REPO_RAW) { $env:YUI_REPO_RAW } else { 'https://raw.githubusercontent.com/netphantom/Y-UITheGUI/main' }
$Dir = if ($env:YUI_DIR) { $env:YUI_DIR } else { Join-Path $HOME 'y-ui' }
$Files = 'docker-compose.yml', 'docker-compose.gpu.yml', '.env.example'

function Say([string] $Message) { Write-Host "> $Message" -ForegroundColor Magenta }

# Set KEY=VALUE in .env, replacing an existing (possibly commented-out) line.
# Written with LF endings and no BOM, which is what Docker Compose expects.
function Set-EnvValue([string] $Key, [string] $Value) {
    $path = Join-Path (Get-Location) '.env'
    $lines = [System.Collections.Generic.List[string]] [IO.File]::ReadAllLines($path)
    $index = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "^#?\s*$([regex]::Escape($Key))=") { $index = $i; break }
    }
    if ($index -ge 0) { $lines[$index] = "$Key=$Value" } else { $lines.Add("$Key=$Value") }
    [IO.File]::WriteAllText($path, ($lines -join "`n") + "`n")
}

function Get-EnvValue([string] $Key) {
    $line = Get-Content .env | Where-Object { $_ -match "^$([regex]::Escape($Key))=" } | Select-Object -First 1
    if ($line) { return $line.Split('=', 2)[1] }
}

function Test-Command([string] $Name) { [bool] (Get-Command $Name -ErrorAction SilentlyContinue) }

function Install-YUI {
    if (-not (Test-Command docker)) {
        throw 'Docker Desktop is required: https://docs.docker.com/desktop/setup/install/windows-install/'
    }
    docker compose version *> $null
    if ($LASTEXITCODE -ne 0) { throw 'Docker Compose v2 is required (included in Docker Desktop).' }
    docker info *> $null
    if ($LASTEXITCODE -ne 0) { throw 'Docker is not running: start Docker Desktop and try again.' }

    Say "Installing into $Dir"
    New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    Push-Location $Dir
    try { Install-InCurrentDir } finally { Pop-Location }
}

function Install-InCurrentDir {
    foreach ($file in $Files) {
        Invoke-WebRequest -UseBasicParsing -Uri "$RepoRaw/$file" -OutFile $file
    }

    if (Test-Path .env) {
        Say 'Keeping your existing .env'
    } else {
        Copy-Item .env.example .env
        # A Docker named volume: SQLite on a bind-mounted C:\ folder is slow and its locks are unreliable.
        Set-EnvValue 'YUI_DATA_PATH' 'yui-data'
        $hasGpu = (Test-Command nvidia-smi) -and $(& nvidia-smi *> $null; $LASTEXITCODE -eq 0)
        if ($hasGpu) {
            Say 'NVIDIA GPU found: using the YuE2 engine (Docker Desktop must use the WSL 2 backend)'
        } else {
            Say 'No NVIDIA GPU found: using the mock engine (UI demo, no real music)'
            Set-EnvValue 'COMPOSE_FILE' 'docker-compose.yml'
            Set-EnvValue 'YUI_ENGINE' 'mock'
        }
    }

    Say 'Pulling images'
    docker compose pull
    if ($LASTEXITCODE -ne 0) { throw 'docker compose pull failed' }
    Say 'Starting Y-UI'
    docker compose up -d
    if ($LASTEXITCODE -ne 0) { throw 'docker compose up failed' }

    $port = Get-EnvValue 'YUI_PORT'
    if (-not $port) { $port = '8080' }
    $url = "http://localhost:$port"
    Say "Done! Open $url and create the first (admin) account."
    Say 'The first YuE2 start downloads the engine and model weights (~15 GB): follow it with'
    Write-Host "    cd `"$Dir`"; docker compose logs -f backend"
    if (-not $env:YUI_NO_BROWSER) { Start-Process $url }
}

# Wrapped in a function so errors stop the script without closing the console (irm | iex).
try {
    Install-YUI
} catch {
    Write-Host "x $($_.Exception.Message)" -ForegroundColor Red
}
