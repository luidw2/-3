param(
    [ValidateSet('login','products','order')][string]$Scenario='login',
    [ValidateRange(1,200)][int]$Threads=2,
    [ValidateRange(1,100000)][int]$Loops=2,
    [int]$Ramp=1,
    [int]$ThinkMs=1500,
    [string]$ServerHost='127.0.0.1',
    [int]$Port=5000,
    [ValidateSet('http','https')][string]$Protocol='http',
    [string]$OutputDirectory=''
)
$ErrorActionPreference='Stop'
$perfRoot=$PSScriptRoot
$repoRoot=Split-Path $perfRoot -Parent
$toolRoot=Join-Path (Split-Path $repoRoot -Parent) '.local-tools'
$javaDir=Get-ChildItem -LiteralPath $toolRoot -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'bin/java.exe') } | Select-Object -First 1
if (-not $javaDir) { throw 'Portable Java not found in .local-tools' }
$env:JAVA_HOME=$javaDir.FullName
$java=Join-Path $javaDir.FullName 'bin/java.exe'
$jmeterRoot=Join-Path $toolRoot 'apache-jmeter-5.6.3'
$localRoot=Join-Path $perfRoot '.local'
$usersFile=Join-Path $localRoot 'users.csv'
if (-not (Test-Path -LiteralPath $usersFile)) { throw 'Run seed_data.py first' }
if ((@(Get-Content -LiteralPath $usersFile).Count-1) -lt $Threads) { throw 'Not enough test users: rerun seed_data.py --users N' }
$plans=@{
    login='performance/plans/login.jmx'
    products='performance/plans/products.jmx'
    order='performance/plans/order.jmx'
}
$out=if ($OutputDirectory) { [System.IO.Path]::GetFullPath($OutputDirectory) } else {
    Join-Path $localRoot ('results/'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff')+'-'+$Scenario)
}
if (Test-Path -LiteralPath $out) { throw 'Output directory already exists; previous evidence will not be overwritten' }
New-Item -ItemType Directory -Path $out -Force | Out-Null
$manifest=[ordered]@{
    scenario=$Scenario; started=(Get-Date).ToString('o'); threads=$Threads; loops=$Loops;
    ramp_seconds=$Ramp; think_ms=$ThinkMs; host=$ServerHost; port=$Port; protocol=$Protocol;
    tunnel='SM2 + SM4-CBC (current implementation)';
    timing='HTTP sampler elapsed excludes client preprocessing and response assertion time';
    git_commit=(& git -C $repoRoot rev-parse HEAD); git_status=(& git -C $repoRoot status --short | Out-String)
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $out 'run.json') -Encoding utf8
$jmeterArgs=@('-jar',(Join-Path $jmeterRoot 'bin/ApacheJMeter.jar'),'-n',
    '-t',(Join-Path $repoRoot $plans[$Scenario]),'-q',(Join-Path $localRoot 'jmeter.properties'),
    ('-Jperf_dir='+($perfRoot -replace '\\','/')),('-Jusers_file='+($usersFile -replace '\\','/')),
    "-Jhost=$ServerHost","-Jport=$Port","-Jprotocol=$Protocol","-Jthreads=$Threads","-Jloops=$Loops", "-Jramp=$Ramp","-Jthink_ms=$ThinkMs",
    '-Jjmeter.save.saveservice.output_format=csv','-Jjmeter.save.saveservice.response_data=false',
    '-Jjmeter.save.saveservice.samplerData=false','-Jjmeter.save.saveservice.requestHeaders=false',
    '-Jjmeter.save.saveservice.responseHeaders=false','-Jjmeter.save.saveservice.assertion_results_failure_message=true',
    '-Jjmeter.reportgenerator.sample_filter=^business-.*',
    '-l',(Join-Path $out 'results.jtl'),'-j',(Join-Path $out 'jmeter.log'),'-e','-o',(Join-Path $out 'html'))
& $java @jmeterArgs
if ($LASTEXITCODE -ne 0) { throw "JMeter failed: $out" }
$rows=@(Import-Csv -LiteralPath (Join-Path $out 'results.jtl'))
$failures=@($rows | Where-Object { $_.success -ne 'true' })
$measured=@($rows | Where-Object { $_.label -like 'business-*' })
if ($measured.Count -ne ($Threads*$Loops) -or $failures.Count -gt 0) {
    throw "Business validation failed: measured=$($measured.Count), failed=$($failures.Count). See $out"
}
Write-Output "PASS: $($measured.Count) business samples; results: $out"
