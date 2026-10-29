param([int]$Port=5000,[string]$Python='python',[string]$Database='')
$ErrorActionPreference='Stop'
$repoRoot=Split-Path $PSScriptRoot -Parent
$backend=Get-ChildItem -LiteralPath $repoRoot -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'run.py') } | Select-Object -First 1
if (-not $backend) { throw 'Backend run.py not found' }
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) { throw "Port $Port already in use; existing service was not interrupted." }
$pythonPath=(Get-Command $Python).Source
$logs=Join-Path $backend.FullName 'logs'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$localRoot=Join-Path $PSScriptRoot '.local'
New-Item -ItemType Directory -Path $localRoot -Force | Out-Null
$names=@('FLASK_HOST','FLASK_PORT','FLASK_DEBUG','TUNNEL_ENABLED','PYTHONIOENCODING','DB_NAME')
$previous=@{}
foreach ($name in $names) { $previous[$name]=[Environment]::GetEnvironmentVariable($name,'Process') }
try {
    $env:FLASK_HOST='127.0.0.1'; $env:FLASK_PORT="$Port"; $env:FLASK_DEBUG='0'
    $env:TUNNEL_ENABLED='1'; $env:PYTHONIOENCODING='utf-8'
    if ($Database) {
        if ($Database -notmatch '^perf9_[a-zA-Z0-9_]+$') { throw 'Isolated DB name must start with perf9_' }
        $env:DB_NAME=$Database
    }
    $process=Start-Process -FilePath $pythonPath -ArgumentList 'run.py' -WorkingDirectory $backend.FullName -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logs "startup-$Port.stdout.log") -RedirectStandardError (Join-Path $logs "startup-$Port.stderr.log") -PassThru
} finally {
    foreach ($name in $names) { [Environment]::SetEnvironmentVariable($name,$previous[$name],'Process') }
}
$processFile=if ($Port -eq 5000) { 'backend-process.json' } else { "backend-process-$Port.json" }
@{pid=$process.Id;port=$Port;host='127.0.0.1';debug=$false;tunnel=$true;database=$Database} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $localRoot $processFile) -Encoding utf8
for ($i=0;$i -lt 30;$i++) {
    if ($process.HasExited) { throw 'Backend exited; inspect logs/startup.stderr.log' }
    try {
        $response=Invoke-WebRequest -Uri "http://127.0.0.1:$Port/" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200 -and $response.Content -eq 'Hello, World!') {
            Write-Output "Backend ready: http://127.0.0.1:$Port/ PID=$($process.Id), debug=off, tunnel=on"
            exit 0
        }
    } catch { Start-Sleep -Milliseconds 500 }
}
throw 'Backend readiness timeout; inspect startup logs'
