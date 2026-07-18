[CmdletBinding()]
param(
    [switch]$AllowMainReadOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-GitReadOnly {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $output = & git --no-optional-locks @Arguments
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "La commande Git en lecture seule 'git $($Arguments -join ' ')' a echoue (code $exitCode)."
    }

    return @($output)
}

function Test-DataPath {
    param([string]$Path)

    $normalized = $Path.Replace('\', '/')
    return $normalized -match '(?i)(^|/)data(/|$)'
}

function Test-SensitivePath {
    param([string]$Path)

    $normalized = $Path.Replace('\', '/')
    return $normalized -match '(?i)(^|/)(\.env(?:\..*)?|[^/]*(?:secret|token|credential)[^/]*)$'
}

try {
    $null = Invoke-GitReadOnly -Arguments @('rev-parse', '--is-inside-work-tree')

    $branch = (Invoke-GitReadOnly -Arguments @('branch', '--show-current') | Select-Object -First 1).ToString().Trim()
    if ([string]::IsNullOrWhiteSpace($branch)) {
        throw 'Impossible de determiner la branche actuelle (HEAD detachee ou depot invalide).'
    }

    Write-Host "Branche actuelle : $branch"
    if ($branch -eq 'main' -and -not $AllowMainReadOnly) {
        [Console]::Error.WriteLine("Execution refusee sur main. Utiliser -AllowMainReadOnly uniquement pour un controle explicitement autorise et strictement en lecture seule.")
        exit 2
    }

    Write-Host 'Git status --short :'
    $status = @(Invoke-GitReadOnly -Arguments @('status', '--short', '--untracked-files=all'))
    if ($status.Count -eq 0) {
        Write-Host '  (propre)'
    }
    else {
        $status | ForEach-Object { Write-Host $_ }
    }

    Write-Host 'Git diff --check :'
    $diffCheck = @(Invoke-GitReadOnly -Arguments @('diff', '--check'))
    if ($diffCheck.Count -eq 0) {
        Write-Host '  OK'
    }
    else {
        $diffCheck | ForEach-Object { Write-Host $_ }
    }

    $modified = @(@(
            Invoke-GitReadOnly -Arguments @('-c', 'core.quotepath=false', 'diff', '--name-only')
            Invoke-GitReadOnly -Arguments @('-c', 'core.quotepath=false', 'diff', '--cached', '--name-only')
            Invoke-GitReadOnly -Arguments @('-c', 'core.quotepath=false', 'ls-files', '--others', '--exclude-standard')
        ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)

    Write-Host 'Fichiers modifies, staged ou non suivis :'
    if ($modified.Count -eq 0) {
        Write-Host '  (aucun)'
    }
    else {
        $modified | ForEach-Object { Write-Host $_ }
    }

    $tracked = @(Invoke-GitReadOnly -Arguments @('-c', 'core.quotepath=false', 'ls-files'))
    $dataViolations = @((@($tracked) + @($modified)) |
            Where-Object { Test-DataPath -Path $_ } |
            Sort-Object -Unique)
    if ($dataViolations.Count -gt 0) {
        throw "Violation data/ : chemin suivi, staged, modifie ou non suivi detecte : $($dataViolations -join ', ')"
    }

    $staged = @(Invoke-GitReadOnly -Arguments @('-c', 'core.quotepath=false', 'diff', '--cached', '--name-only'))
    $sensitiveStaged = @(@($staged) |
            Where-Object { Test-SensitivePath -Path $_ } |
            Sort-Object -Unique)
    if ($sensitiveStaged.Count -gt 0) {
        throw "Violation secrets : fichier .env, secret, token ou credential staged : $($sensitiveStaged -join ', ')"
    }

    Write-Host 'Dernier commit :'
    Invoke-GitReadOnly -Arguments @('log', '-1', '--oneline', '--decorate') |
        ForEach-Object { Write-Host $_ }

    Write-Host 'Preflight AGIcore : OK (controles strictement en lecture seule).'
    exit 0
}
catch {
    [Console]::Error.WriteLine("Preflight AGIcore : ECHEC. $($_.Exception.Message)")
    exit 1
}
