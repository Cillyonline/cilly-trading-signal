#Requires -Version 5.1

<#
.SYNOPSIS
    Formats sanitized local smoke evidence as Markdown.

.DESCRIPTION
    This helper accepts explicit operator-provided status values and prints a
    sanitized Markdown evidence block. It does not read .env files, cookies,
    browser sessions, logs, databases, provider payloads, screenshots, local
    storage, or private trading data.

    The output is process evidence only. It is not a production-readiness,
    live/realtime, broker-readiness, profitability, strategy-validation,
    trading-advice, real-money, or automatic-execution claim.

.PARAMETER EnvironmentClass
    Evidence environment class. Default: local.

.PARAMETER Workflow
    Smoke workflow name. Default: local smoke.

.PARAMETER CommitSha
    Optional commit SHA or branch context supplied by the operator.

.PARAMETER SmokeRunnerStatus
    Smoke runner result: pass, fail, skipped, or not run.

.PARAMETER ApiHealth
    API health result: pass, fail, skipped, or not run.

.PARAMETER WebLoad
    Web load result: pass, fail, skipped, or not run.

.PARAMETER BrowserChecklist
    Browser checklist result: pass, fail, skipped, or not run.

.PARAMETER FollowUpIssue
    Optional sanitized follow-up issue URL or identifier.

.PARAMETER SanitizedDetails
    Optional sanitized detail text. Do not include secrets, logs, cookies, tokens,
    private symbols, private notes, account data, or screenshots.

.EXAMPLE
    .\scripts\format_smoke_evidence.ps1 -CommitSha abc123 -SmokeRunnerStatus pass -ApiHealth pass -WebLoad pass

    Prints a sanitized Markdown evidence block for a local smoke run.
#>

[CmdletBinding()]
param(
    [ValidateSet('local', 'private staging', 'disposable target', 'sample-only browser smoke')]
    [string]$EnvironmentClass = 'local',

    [string]$Workflow = 'local smoke',

    [string]$CommitSha = 'not recorded',

    [ValidateSet('pass', 'fail', 'skipped', 'not run')]
    [string]$SmokeRunnerStatus = 'not run',

    [ValidateSet('pass', 'fail', 'skipped', 'not run')]
    [string]$ApiHealth = 'not run',

    [ValidateSet('pass', 'fail', 'skipped', 'not run')]
    [string]$WebLoad = 'not run',

    [ValidateSet('pass', 'fail', 'skipped', 'not run')]
    [string]$BrowserChecklist = 'not run',

    [string]$FollowUpIssue = 'none',

    [string]$SanitizedDetails = 'none'
)

$ErrorActionPreference = 'Stop'

function Format-SafeLine($Value) {
    $singleLine = ($Value -replace '[\r\n]+', ' ').Trim()
    if ([string]::IsNullOrWhiteSpace($singleLine)) {
        return 'none'
    }
    return $singleLine
}

$timestamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')

@(
    '## Local Smoke Evidence',
    '',
    "- Date/time UTC: $timestamp",
    "- Environment class: $(Format-SafeLine $EnvironmentClass)",
    "- Workflow: $(Format-SafeLine $Workflow)",
    "- Commit SHA: $(Format-SafeLine $CommitSha)",
    '- Check or command: scripts/smoke_test.ps1 / browser checklist summary',
    "- Smoke runner status: $SmokeRunnerStatus",
    "- API health: $ApiHealth",
    "- Web load: $WebLoad",
    "- Browser checklist: $BrowserChecklist",
    "- Sanitized details: $(Format-SafeLine $SanitizedDetails)",
    "- Follow-up issue: $(Format-SafeLine $FollowUpIssue)",
    '- Secrets/private data/raw logs/screenshots with sensitive data included: no',
    '- Cookies/tokens/browser storage/provider keys/.env values read or included: no',
    '- Production-readiness, broker-readiness, real-money, profitability, live/realtime, trading-advice, or automatic-execution claim made: no'
) -join [Environment]::NewLine
