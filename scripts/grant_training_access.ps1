<#
.SYNOPSIS
    Grants training participants the standard IAM role set on the training GCP project.

.DESCRIPTION
    Reads e-mails from a participants file (one per line, '#' = comment), computes the
    missing (user, role) bindings and - with -Apply - writes them with a single
    read-modify-write of the project IAM policy (etag-protected, original policy backed up).
    Without -Apply it only prints the plan (dry run).

    The default role set mirrors the existing participants of adk-training-pz.

.EXAMPLE
    .\scripts\grant_training_access.ps1                     # dry run
    .\scripts\grant_training_access.ps1 -Apply              # grant roles
    .\scripts\grant_training_access.ps1 -Revoke -Apply      # remove the same roles after the training
#>
[CmdletBinding()]
param(
    [string]$Project = "adk-training-pz",
    [string]$ParticipantsFile = (Join-Path $PSScriptRoot "participants.txt"),
    [string[]]$Roles = @(
        "roles/aiplatform.user",                     # Gemini / Vertex AI, Agent Engine (Memory Bank)
        "roles/discoveryengine.admin",               # Vertex AI Search - creating data stores (RAG)
        "roles/discoveryengine.viewer",
        "roles/logging.viewer",
        "roles/run.developer",                       # Cloud Run deploy (module 06)
        "roles/serviceusage.serviceUsageConsumer",   # ADC quota project
        "roles/storage.admin",                       # buckets for RAG documents
        "roles/storage.objectViewer"
    ),
    [switch]$Apply,
    [switch]$Revoke
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    throw "gcloud not found. Install Google Cloud SDK first."
}
if (-not (Test-Path $ParticipantsFile)) {
    throw "Participants file not found: $ParticipantsFile (one e-mail per line)."
}

$emailRegex = '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
$emails = Get-Content $ParticipantsFile -Encoding UTF8 |
    ForEach-Object { ($_ -split '#')[0].Trim().ToLowerInvariant() } |
    Where-Object { $_ } |
    Sort-Object -Unique

$invalid = @($emails | Where-Object { $_ -notmatch $emailRegex })
if ($invalid.Count) { throw "Invalid e-mail(s): $($invalid -join ', ')" }
if (-not $emails) { throw "No e-mails in $ParticipantsFile." }

$account = (gcloud config get-value account 2>$null)
Write-Host "Project : $Project"
Write-Host "Caller  : $account"
Write-Host "Mode    : $(if ($Revoke) {'REVOKE'} else {'GRANT'}) / $(if ($Apply) {'APPLY'} else {'DRY RUN'})"
Write-Host "Users   : $($emails.Count)"
Write-Host ""

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backup = Join-Path $env:TEMP "iam_policy_${Project}_$stamp.json"
gcloud projects get-iam-policy $Project --format=json | Out-File -Encoding utf8 $backup
$policy = Get-Content $backup -Raw | ConvertFrom-Json
if (-not $policy.bindings) { $policy | Add-Member -NotePropertyName bindings -NotePropertyValue @() -Force }

$changes = 0
foreach ($role in $Roles) {
    $binding = $policy.bindings | Where-Object { $_.role -eq $role -and -not $_.condition } | Select-Object -First 1
    if (-not $binding -and -not $Revoke) {
        $binding = [pscustomobject]@{ role = $role; members = @() }
        $policy.bindings = @($policy.bindings) + $binding
    }
    if (-not $binding) { continue }
    $members = [System.Collections.Generic.List[string]]::new([string[]]@($binding.members))
    foreach ($email in $emails) {
        $member = "user:$email"
        if ($Revoke -and $members.Contains($member)) {
            [void]$members.Remove($member); $changes++
            Write-Host "  - $member  $role"
        } elseif (-not $Revoke -and -not $members.Contains($member)) {
            $members.Add($member); $changes++
            Write-Host "  + $member  $role"
        }
    }
    $binding.members = @($members)
}
$policy.bindings = @($policy.bindings | Where-Object { @($_.members).Count -gt 0 })

Write-Host ""
Write-Host "Changes : $changes  (backup of current policy: $backup)"
if ($changes -eq 0) { Write-Host "Nothing to do."; return }
if (-not $Apply) { Write-Host "Dry run - re-run with -Apply to write the policy."; return }

$newPolicyFile = Join-Path $env:TEMP "iam_policy_${Project}_${stamp}_new.json"
# UTF-8 without BOM - gcloud rejects a BOM-prefixed JSON file
[IO.File]::WriteAllText($newPolicyFile, ($policy | ConvertTo-Json -Depth 20), [Text.UTF8Encoding]::new($false))
gcloud projects set-iam-policy $Project $newPolicyFile --format=none
if ($LASTEXITCODE -ne 0) { throw "set-iam-policy failed (policy unchanged). Backup: $backup" }

$after = gcloud projects get-iam-policy $Project --format=json | ConvertFrom-Json
$missing = foreach ($role in $Roles) {
    $m = @(($after.bindings | Where-Object role -eq $role).members)
    foreach ($email in $emails) {
        $has = $m -contains "user:$email"
        if ($has -eq [bool]$Revoke) { "user:$email $role" }
    }
}
if ($missing) { Write-Warning "Not applied: $($missing -join '; ')" } else { Write-Host "OK - policy verified." }
