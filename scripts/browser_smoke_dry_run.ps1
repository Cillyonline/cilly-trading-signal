#Requires -Version 5.1

<#
.SYNOPSIS
    Safe browser-smoke dry run for sample/local targets.

.DESCRIPTION
    Checks a small set of owner/operator web routes and prints sanitized Markdown
    evidence. The script does not read .env files, credentials, cookies, browser
    profiles, local storage, screenshots, raw logs, raw API responses, provider
    keys, private symbols, broker data, or private trading records.

    This is an explicit local/manual dry run. It is not a required CI gate and it
    is not production-readiness, live/realtime, broker-readiness, profitability,
    strategy-validation, trading-advice, or automatic-execution evidence.

.PARAMETER TargetBaseUrl
    Base URL to check. Defaults to http://localhost:3000. In local-sample mode,
    only localhost or 127.0.0.1 targets are allowed.

.PARAMETER Mode
    Dry-run mode: local-sample or private-staging-dry-run.

.PARAMETER ApprovedPrivateStaging
    Required when Mode is private-staging-dry-run.

.PARAMETER CommitSha
    Optional commit SHA or branch context supplied by the operator.

.PARAMETER TimeoutSeconds
    Per-route request timeout. Default 15 seconds.

.EXAMPLE
    .\scripts\browser_smoke_dry_run.ps1 -CommitSha abc123

    Checks the local web app at http://localhost:3000 and prints sanitized evidence.
#>

[CmdletBinding()]
param(
    [string]$TargetBaseUrl = 'http://localhost:3000',

    [ValidateSet('local-sample', 'private-staging-dry-run')]
    [string]$Mode = 'local-sample',

    [switch]$ApprovedPrivateStaging,

    [string]$CommitSha = 'not recorded',

    [ValidateRange(1, 120)]
    [int]$TimeoutSeconds = 15
)

$ErrorActionPreference = 'Stop'

$RouteChecks = @(
    @{ Path = '/login'; Name = 'login' },
    @{ Path = '/'; Name = 'dashboard' },
    @{ Path = '/import'; Name = 'import' },
    @{ Path = '/signals'; Name = 'signals' }
)

function Format-SafeLine($Value) {
    $singleLine = ($Value -replace '[\r\n]+', ' ').Trim()
    if ([string]::IsNullOrWhiteSpace($singleLine)) {
        return 'none'
    }
    return $singleLine
}

function Get-SanitizedErrorCategory($ErrorRecord) {
    $exception = $ErrorRecord.Exception
    if ($exception.Response -and $exception.Response.StatusCode) {
        $statusCode = [int]$exception.Response.StatusCode
        if ($statusCode -ge 500) {
            return 'route_5xx'
        }
        if ($statusCode -eq 401 -or $statusCode -eq 403) {
            return 'auth_boundary'
        }
        if ($statusCode -eq 404) {
            return 'route_unavailable'
        }
        return "http_$statusCode"
    }

    $message = $exception.Message
    if ($message -match 'timed out|timeout') {
        return 'request_timeout'
    }
    if ($message -match 'refused|NameResolutionFailure|No such host|could not be resolved') {
        return 'target_unreachable'
    }
    return 'request_failed'
}

function Get-RouteUrl([uri]$BaseUri, [string]$Path) {
    return [uri]::new($BaseUri, $Path)
}

try {
    $baseUri = [uri]$TargetBaseUrl
} catch {
    Write-Error 'TargetBaseUrl must be a valid URI.'
}

if ($baseUri.Scheme -notin @('http', 'https')) {
    Write-Error 'TargetBaseUrl must use http or https.'
}

$isLocalTarget = $baseUri.Host -in @('localhost', '127.0.0.1', '::1')
if ($Mode -eq 'local-sample' -and -not $isLocalTarget) {
    Write-Error 'local-sample mode only allows localhost, 127.0.0.1, or ::1 targets.'
}

if ($Mode -eq 'private-staging-dry-run' -and -not $ApprovedPrivateStaging) {
    Write-Error 'private-staging-dry-run requires -ApprovedPrivateStaging for this exact target and commit.'
}

$timestamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$targetClass = if ($isLocalTarget) { 'local' } else { 'private staging' }
$results = New-Object System.Collections.Generic.List[object]

foreach ($route in $RouteChecks) {
    $url = Get-RouteUrl -BaseUri $baseUri -Path $route.Path
    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec $TimeoutSeconds -UseBasicParsing -MaximumRedirection 5
        $statusCode = [int]$response.StatusCode
        $status = if ($statusCode -ge 200 -and $statusCode -lt 400) { 'pass' } else { 'fail' }
        $category = if ($status -eq 'pass') { 'none' } else { "http_$statusCode" }
    } catch {
        $status = 'fail'
        $category = Get-SanitizedErrorCategory $_
    }

    $results.Add([pscustomobject]@{
        Name = $route.Name
        Path = $route.Path
        Status = $status
        Category = $category
    })
}

$failed = @($results | Where-Object { $_.Status -ne 'pass' })
$routeSummary = ($results | ForEach-Object { "$($_.Path)=$($_.Status)" }) -join ', '
$failedPages = if ($failed.Count -eq 0) { 'none' } else { ($failed | ForEach-Object { $_.Path }) -join ', ' }
$failureCategories = if ($failed.Count -eq 0) { 'none' } else { ($failed | ForEach-Object { $_.Category } | Sort-Object -Unique) -join ', ' }

@(
    '## Browser Smoke Evidence',
    '',
    "- Date/time: $timestamp",
    '- Operator or role: not recorded',
    "- Environment class: $Mode",
    "- Target URL class: $targetClass",
    "- Branch or commit SHA: $(Format-SafeLine $CommitSha)",
    '- Browser and viewport class: http dry-run / viewport not applicable',
    '- Data scope: sample / synthetic / paper only',
    "- Pages or workflows checked: $routeSummary",
    "- Route-level status: $(if ($failed.Count -eq 0) { 'pass' } else { 'fail' })",
    "- Failed or blocked pages: $failedPages",
    "- Sanitized failure category: $failureCategories",
    '- Follow-up issues or PRs: none recorded by script',
    '- Screenshots captured: no',
    '- Cookies, tokens, local storage, `.env` values, provider keys, database URLs, raw logs, raw API responses, private symbols, broker data, or private trading records included: no',
    '- Production-readiness, live/realtime, broker-readiness, profitability, strategy-validation, trading-advice, or automatic-execution claim made: no'
) -join [Environment]::NewLine

if ($failed.Count -gt 0) {
    exit 1
}
