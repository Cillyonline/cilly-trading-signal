#Requires -Version 5.1

<#
.SYNOPSIS
    MVP smoke test runner. Brings up the local Docker stack, applies migrations,
    and verifies API health.

.DESCRIPTION
    This script performs preflight checks (Docker CLI, Docker Compose CLI, Docker
    Engine reachability), starts the local stack defined in infra/docker-compose.yml,
    applies Alembic migrations inside the local API container, and polls
    /api/health until the API responds or a timeout expires.

    It is release-validation tooling for the manual trading cockpit. It does not
    make any production-readiness, profitability, or execution claim. The smoke
    workflow continues in the browser using the sample CSV fixtures under
    test-data/csv/. See docs/MVP_SMOKE_TEST.md. The migration step is for
    local smoke validation and does not define production migration policy.

.PARAMETER Cleanup
    Tear down the local stack (docker compose down). Does not remove volumes.

.PARAMETER PurgeVolumes
    With -Cleanup, also remove named volumes (postgres-data, caddy-data,
    caddy-config). This wipes the local Postgres database.

.PARAMETER TimeoutSeconds
    How long to poll the API health endpoint before giving up. Default 120.

.EXAMPLE
    .\scripts\smoke_test.ps1
    Run preflight, bring the stack up, and wait for /api/health.

.EXAMPLE
    .\scripts\smoke_test.ps1 -Cleanup
    Bring the stack down (volumes preserved).

.EXAMPLE
    .\scripts\smoke_test.ps1 -Cleanup -PurgeVolumes
    Bring the stack down and remove the Postgres volume.
#>

[CmdletBinding()]
param(
    [switch]$Cleanup,
    [switch]$PurgeVolumes,
    [int]$TimeoutSeconds = 120
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ComposeFile = Join-Path $RepoRoot 'infra\docker-compose.yml'
$EnvFile = Join-Path $RepoRoot '.env'
$EnvExample = Join-Path $RepoRoot '.env.example'
$HealthUrl = 'http://localhost:8000/api/health'

function Write-Step($Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-Pass($Message) {
    Write-Host "[PASS] $Message" -ForegroundColor Green
}

function Write-Fail($Message) {
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Test-DockerCli {
    $command = Get-Command -Name 'docker' -ErrorAction SilentlyContinue
    if (-not $command) {
        Write-Fail 'docker CLI not found in PATH. Install Docker Desktop and retry.'
        return $false
    }
    $version = & docker --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Fail 'docker --version exited non-zero. Is Docker installed?'
        return $false
    }
    Write-Pass "docker CLI: $version"
    return $true
}

function Test-DockerComposeCli {
    $version = & docker compose version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Fail 'docker compose plugin not available. Update Docker Desktop.'
        return $false
    }
    Write-Pass "docker compose: $version"
    return $true
}

function Test-DockerEngine {
    & docker info --format '{{.ServerVersion}}' 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Fail 'Docker engine is not reachable. Start Docker Desktop and wait for it to finish initialising before retrying.'
        return $false
    }
    Write-Pass 'Docker engine reachable.'
    return $true
}

function Test-ComposeFile {
    if (-not (Test-Path -LiteralPath $ComposeFile)) {
        Write-Fail "Compose file not found at $ComposeFile."
        return $false
    }
    Write-Pass "Compose file: $ComposeFile"
    return $true
}

function Ensure-EnvFile {
    if (Test-Path -LiteralPath $EnvFile) {
        Write-Pass '.env present.'
        return $true
    }
    if (-not (Test-Path -LiteralPath $EnvExample)) {
        Write-Fail "Neither .env nor .env.example found at $RepoRoot."
        return $false
    }
    Copy-Item -LiteralPath $EnvExample -Destination $EnvFile
    Write-Pass '.env created from .env.example (local placeholders only; do not commit).'
    return $true
}

function Invoke-Preflight {
    Write-Step 'Preflight checks'
    $checks = @(
        (Test-DockerCli),
        (Test-DockerComposeCli),
        (Test-DockerEngine),
        (Test-ComposeFile),
        (Ensure-EnvFile)
    )
    if ($checks -contains $false) {
        Write-Host ''
        Write-Fail 'Preflight failed. Resolve the items above and rerun.'
        exit 1
    }
}

function Invoke-StackUp {
    Write-Step 'Starting the stack (docker compose up --build -d)'
    & docker compose -f $ComposeFile up --build -d
    if ($LASTEXITCODE -ne 0) {
        Write-Fail 'docker compose up failed.'
        exit 1
    }
    Write-Pass 'Stack started.'
}

function Invoke-DatabaseMigrations {
    Write-Step 'Applying database migrations (alembic upgrade head)'
    & docker compose -f $ComposeFile exec -T api alembic upgrade head
    if ($LASTEXITCODE -ne 0) {
        Write-Fail 'Database migrations failed. Check API logs and migration output before continuing the smoke test.'
        exit 1
    }
    Write-Pass 'Database migrations applied.'
}

function Wait-ForApiHealth {
    Write-Step "Waiting for $HealthUrl (timeout ${TimeoutSeconds}s)"
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-RestMethod -Uri $HealthUrl -Method Get -TimeoutSec 5
            Write-Pass "API health: $($response | ConvertTo-Json -Compress)"
            return
        }
        catch {
            Start-Sleep -Seconds 3
        }
    }
    Write-Fail 'API did not become healthy within the timeout. Check logs with: docker compose -f infra/docker-compose.yml logs api'
    exit 1
}

function Invoke-StackDown {
    Write-Step 'Stopping the stack (docker compose down)'
    if ($PurgeVolumes) {
        & docker compose -f $ComposeFile down --volumes
    }
    else {
        & docker compose -f $ComposeFile down
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Fail 'docker compose down failed.'
        exit 1
    }
    if ($PurgeVolumes) {
        Write-Pass 'Stack stopped and volumes removed.'
    }
    else {
        Write-Pass 'Stack stopped (volumes preserved).'
    }
}

if ($Cleanup) {
    if (-not (Test-ComposeFile)) {
        exit 1
    }
    Invoke-StackDown
    exit 0
}

Invoke-Preflight
Invoke-StackUp
Invoke-DatabaseMigrations
Wait-ForApiHealth

Write-Host ''
Write-Pass 'Smoke runner finished. Continue with the browser workflow:'
Write-Host '  - Web app:    http://localhost:3000'
Write-Host '  - API health: http://localhost:8000/api/health'
Write-Host '  - Sample CSV fixtures: test-data/csv/'
Write-Host ''
Write-Host 'Tear down with: .\scripts\smoke_test.ps1 -Cleanup'
