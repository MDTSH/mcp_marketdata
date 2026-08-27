# Weekly MCP market-data sync: prepare window, verify, commit, push.
# Does not force-push, amend, skip hooks, or change git config.
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SourceDefault = "Z:\market_data\snapshots"
$Days = 90
$RemoteUrl = "https://github.com/MDTSH/mcp_marketdata"
$LogPath = Join-Path $RepoRoot "reports\weekly_sync.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] [$Level] $Message"
    Write-Host $line
    $logDir = Split-Path -Parent $LogPath
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    Add-Content -Path $LogPath -Value $line -Encoding UTF8
}

function Resolve-Python {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) { return $cmd.Source }
    $cmd = Get-Command py -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) { return $cmd.Source }
    $candidates = @(
        "D:\ProgramData\Anaconda39\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe",
        "C:\Python39\python.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    throw "python not found on PATH or known install locations"
}

function Get-WindowCommitMessage {
    param([int]$WindowDays)
    $asOf = Get-Date
    $start = $asOf.AddDays(-$WindowDays)
    return ("sync: window {0} .. {1}" -f $start.ToString("yyyy-MM-dd"), $asOf.ToString("yyyy-MM-dd"))
}

function Assert-GitSafe {
    $gitDir = Join-Path $RepoRoot ".git"
    if (-not (Test-Path $gitDir)) {
        throw "dest is not a git repo: $RepoRoot"
    }
    Push-Location $RepoRoot
    try {
        $origin = git remote get-url origin 2>$null
        if (-not $origin) {
            throw "remote origin is missing. Expected $RemoteUrl"
        }
        if ($origin -notmatch "github\.com[/:]MDTSH/mcp_marketdata(\.git)?$") {
            throw "refusing to push: origin is '$origin' (expected $RemoteUrl)"
        }
        $branch = "main"
        git rev-parse --verify --quiet HEAD >$null 2>&1
        if ($LASTEXITCODE -eq 0) {
            $current = (git rev-parse --abbrev-ref HEAD).Trim()
            if ($current -and $current -ne "HEAD") {
                $branch = $current
            }
        }
        return @{ Origin = $origin; Branch = $branch }
    }
    finally {
        Pop-Location
    }
}

try {
    Write-Log "weekly_sync start repo=$RepoRoot"
    if (-not (Test-Path $SourceDefault)) {
        Write-Log "source missing: $SourceDefault" "ERROR"
        exit 2
    }

    $python = Resolve-Python
    Write-Log "python $python"

    $gitInfo = Assert-GitSafe
    Write-Log ("git origin={0} branch={1}" -f $gitInfo.Origin, $gitInfo.Branch)

    $prepare = Join-Path $ScriptDir "prepare_sync.py"
    $verify = Join-Path $ScriptDir "verify_window.py"

    Write-Log "running prepare_sync.py --days $Days"
    & $python $prepare --source $SourceDefault --dest $RepoRoot --days $Days
    if ($LASTEXITCODE -ne 0) {
        Write-Log "prepare_sync.py failed exit=$LASTEXITCODE" "ERROR"
        exit $LASTEXITCODE
    }

    Write-Log "running verify_window.py --days $Days"
    & $python $verify --source $SourceDefault --dest $RepoRoot --days $Days
    if ($LASTEXITCODE -ne 0) {
        Write-Log "verify_window.py failed exit=$LASTEXITCODE" "ERROR"
        exit $LASTEXITCODE
    }

    Push-Location $RepoRoot
    try {
        $legacySnapshots = Join-Path $RepoRoot "snapshots"
        if (Test-Path $legacySnapshots) {
            throw "leftover snapshots/ exists; publish only market_data/ (re-run prepare_sync.py)"
        }
        $addTargets = @("market_data", "reports", "scripts", "README.md", ".gitignore")
        foreach ($t in $addTargets) {
            if (Test-Path (Join-Path $RepoRoot $t)) {
                git add -- $t
                if ($LASTEXITCODE -ne 0) {
                    throw "git add failed for $t"
                }
            }
        }

        $porcelain = git status --porcelain
        if (-not $porcelain) {
            Write-Log "no changes; skip commit and push"
            exit 0
        }

        $msg = Get-WindowCommitMessage -WindowDays $Days
        Write-Log "git commit $msg"
        git commit -m $msg
        if ($LASTEXITCODE -ne 0) {
            Write-Log "git commit failed exit=$LASTEXITCODE" "ERROR"
            exit $LASTEXITCODE
        }

        $overLimit = @()
        $publishedDir = Join-Path $RepoRoot "market_data"
        if (Test-Path $publishedDir) {
            $overLimit = @(Get-ChildItem -Path $publishedDir -Recurse -File |
                Where-Object { $_.Length -ge 100MB } |
                ForEach-Object { "{0} ({1:N2} MB)" -f $_.FullName, ($_.Length / 1MB) })
        }
        if ($overLimit.Count -gt 0) {
            Write-Log ("refusing push: file(s) >= 100MB (no LFS): " + ($overLimit -join "; ")) "ERROR"
            exit 3
        }

        $branch = $gitInfo.Branch
        Write-Log "git push origin $branch"
        git push origin $branch
        if ($LASTEXITCODE -ne 0) {
            Write-Log "git push failed exit=$LASTEXITCODE (no force retry)" "ERROR"
            exit $LASTEXITCODE
        }
        Write-Log "weekly_sync done"
        exit 0
    }
    finally {
        Pop-Location
    }
}
catch {
    Write-Log $_.Exception.Message "ERROR"
    exit 1
}
