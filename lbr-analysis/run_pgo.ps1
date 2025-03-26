param (
  [switch]$Force
)
# Store the original location
$originalLocation = Get-Location

Set-Variable -Name "PGOFileName" -Value "-pgo-schema.txt"
Set-Variable -Name "LBRFileName" -Value "-lbr-schema.txt"

Set-Variable -Name "OutputDirPath" -Value (Join-Path $PSScriptRoot "run_pgo_output")
Set-Variable -Name "ArtifactsDirPath" -Value (Join-Path $OutputDirPath "artifacts")

Set-Variable -Name 'MicroBenchmarkPath' -Value (Join-Path $PSScriptRoot "../src/benchmarks/micro")
Set-Variable -Name 'CoreRunPath' -Value "C:\runtime\artifacts\tests\coreclr\windows.x64.Checked\Tests\Core_Root\corerun.exe"

function Setup-Directory {
    New-Item -ItemType Directory -Path $OutputDirPath > $null
    New-Item -ItemType Directory -Path $ArtifactsDirPath > $null

    Write-Host "Output directory created: $OutputDirPath"
    Write-Host "Artifacts directory created: $ArtifactsDirPath"
}

if (-not (Test-Path $OutputDirPath)) {
    Setup-Directory
} elseif ($Force) {
    Remove-Item -Recurse -Force $OutputDirPath
    if (Test-Path $OutputDirPath) {
        Write-Host "Failed to remove output directory. Please remove manually and try again."
        exit
    }
    Setup-Directory
} else {
    Write-Host "Output directory already exists. Please remove or run with force option."
    exit
}

function Format-Benchmark-String {
    param (
        [string]$benchmark
    )
    $replacements = @{
        '\.' = '-'
        '\<' = '('
        '\>' = ')'
    }
    foreach ($pattern in $replacements.Keys) {
        $benchmark = $benchmark -replace $pattern, $replacements[$pattern]
    }
    return $benchmark
}

function Run-BenchmarkPGO {
    param (
        [string]$benchmark
    )

    $env:DOTNET_UseLBRSampling = "0"
    $env:DOTNET_WritePGOData = "1"
    $env:DOTNET_AppendPGOData = "1"

    $benchmark_pgo_file = Join-Path $OutputDirPath "$(Format-Benchmark-String -benchmark $benchmark)$PGOFileName"
    $env:DOTNET_PGODataPath = $benchmark_pgo_file

    $cleanUpEnvVars = {
        Remove-Item Env:DOTNET_UseLBRSampling
        Remove-Item Env:DOTNET_WritePGOData
        Remove-Item Env:DOTNET_PGODataPath
        Remove-Item Env:DOTNET_AppendPGOData
    }

    & "dotnet.exe" run -c Release --framework "net10.0" --filter $benchmark --artifacts $ArtifactsDirPath --coreRun $CoreRunPath --keepFiles

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error running PGO collection for $benchmark"
        & $cleanUpEnvVars
        return $false
    }

    $result = Validate-Schema-File -schema_file $benchmark_pgo_file
    & $cleanUpEnvVars
    return $result
}

function Run-BenchmarkLBR {
    param (
        [string]$benchmark
    )

    $env:DOTNET_UseLBRSampling = "1"
    $env:DOTNET_WriteLBRData = "1"
    $env:DOTNET_AppendLBRData = "1"
    $env:DOTNET_TieredPGO = "0"
    $env:DOTNET_TC_CallCountingDelayMs = "500"

    $benchmark_lbr_file = Join-Path $OutputDirPath "$(Format-Benchmark-String -benchmark $benchmark)$LBRFileName"
    $env:DOTNET_LBRDataPath = $benchmark_lbr_file

    $cleanUpEnvVars = {
        Remove-Item Env:DOTNET_UseLBRSampling
        Remove-Item Env:DOTNET_WriteLBRData
        Remove-Item Env:DOTNET_AppendLBRData
        Remove-Item Env:DOTNET_TieredPGO
        Remove-Item Env:DOTNET_TC_CallCountingDelayMs
        Remove-Item Env:DOTNET_LBRDataPath
    }

    & "dotnet.exe" run -c Release --framework "net10.0" --filter $benchmark --artifacts $ArtifactsDirPath --coreRun $CoreRunPath --keepFiles

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error running LBR collection for $benchmark"
        & $cleanUpEnvVars
        return $false
    }

    $result = Validate-Schema-File -schema_file $benchmark_lbr_file
    & $cleanUpEnvVars
    return $result
}

function Validate-Schema-File {
    param (
        [string]$schema_file
    )

    # Check if the schema file exists
    if (-not (Test-Path $schema_file)) {
        Write-Warning "Schema file not found: $schema_file"
        return $false
    }

    return $true
}

try {
    # Change to the subdirectory src/benchmarks/micro relative to the script location
    Set-Location -Path $MicroBenchmarkPath

    # Set the environment variable PERFLAB_TARGET_FRAMEWORKS to net10.0
    $env:PERFLAB_TARGET_FRAMEWORKS = "net10.0"

    # Create a variable that contains a list of benchmarks to run
    $benchmarks = @("System.Numerics.Tensors.Tests.Perf_FloatingPointTensorPrimitives<Single>.Exp") 

    # Loop over the list of benchmarks and run the command
    foreach ($benchmark in $benchmarks) {
        Run-BenchmarkPGO -benchmark $benchmark
        Run-BenchmarkLBR -benchmark $benchmark
    }
}
catch {
    Write-Host "An error occurred: $_"
}
finally {
    # Return to the original location
    Set-Location -Path $originalLocation
}