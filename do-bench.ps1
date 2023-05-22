
$processor_counts = @(15, 30, 50, 64, 100, 128, 224)
#$processor_counts = @(50, 15, 30, 224, 100, 128, 64)
#$processor_counts = @(224)
$iters = 5

$a = @()

#rm -r -fo $PSScriptRoot\artifacts\
#
#
#$cmd1 = "dotnet.exe run -f net8.0 -c Release --filter '`"System.Buffers.Tests.RentReturnArrayPoolTests<Object>.SingleParallel(RentalSize: 4096, ManipulateArray: True, Async: True, UseSharedPool: True)`"' --coreRun `"C:\Users\Administrator\anthony\runtime\artifacts\bin\testhost\net8.0-windows-Release-x64\shared\Microsoft.NETCore.App\8.0.0\corerun.exe`""
#
#foreach ($pc in $processor_counts)
#{
#  Write-Output "Running processor count: $pc"
#  $env:DOTNET_PROCESSOR_COUNT = $pc
#
#  $means = @()
#  for ($i = 0; $i -lt $iters; $i++)
#  {
#    Invoke-Expression $cmd1
#    $json_data = Get-Content -Raw $PSScriptRoot\artifacts\bin\MicroBenchmarks\Release\net8.0\BenchmarkDotNet.Artifacts\results\System.Buffers.Tests.RentReturnArrayPoolTests_Object_-report-full.json | ConvertFrom-Json
#    $mean = $json_data.Benchmarks[0].Statistics.Mean 
#    $means += $mean
#  }
#
#  $a += [PSCustomObject]@{
#    Async = "True"
#    UseSharedPool = "True"
#    Mean1 = $means[0]
#    Mean2 = $means[1]
#    Mean3 = $means[2]
#    Mean4 = $means[3]
#    Mean5 = $means[4]
#    ProcessorCounts = $pc
#  }
#}
#
rm -r -fo $PSScriptRoot\artifacts\

#$cmd2 = "dotnet.exe run -f net8.0 -c Release --filter '`"System.Buffers.Tests.RentReturnArrayPoolTests<Object>.SingleParallel(RentalSize: 4096, ManipulateArray: True, Async: True, UseSharedPool: False)`"' --coreRun `"C:\Users\Administrator\anthony\runtime\artifacts\bin\testhost\net8.0-windows-Release-x64\shared\Microsoft.NETCore.App\8.0.0\corerun.exe`""
$cmd2 = "dotnet.exe run -f net8.0 -c Release --filter '`"System.Buffers.Tests.RentReturnArrayPoolTests<Object>.SingleParallel(RentalSize: 4096, ManipulateArray: False, Async: True, UseSharedPool: False)`"' --coreRun `"C:\Users\Administrator\anthony\runtime\artifacts\bin\testhost\net8.0-windows-Release-x64\shared\Microsoft.NETCore.App\8.0.0\corerun.exe`""

foreach ($pc in $processor_counts)
{
  Write-Output "Running processor count: $pc"
  $env:DOTNET_PROCESSOR_COUNT = $pc

  $means = @()
  for ($i = 0; $i -lt $iters; $i++)
  {
    Invoke-Expression $cmd2
    $json_data = Get-Content -Raw $PSScriptRoot\artifacts\bin\MicroBenchmarks\Release\net8.0\BenchmarkDotNet.Artifacts\results\System.Buffers.Tests.RentReturnArrayPoolTests_Object_-report-full.json | ConvertFrom-Json
    $mean = $json_data.Benchmarks[0].Statistics.Mean 
    $means += $mean
  }

  $a += [PSCustomObject]@{
    Async = "True"
    UseSharedPool = "False"
    Mean1 = $means[0]
    Mean2 = $means[1]
    Mean3 = $means[2]
    Mean4 = $means[3]
    Mean5 = $means[4]
    ProcessorCounts = $pc
  }
}

$a | Export-Csv -Path "out.csv" -NoTypeInformation


