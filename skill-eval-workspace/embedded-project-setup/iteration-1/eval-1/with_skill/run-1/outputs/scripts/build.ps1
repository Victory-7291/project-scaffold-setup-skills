$ErrorActionPreference = "Stop"

$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$Preset = if ($env:PRESET) { $env:PRESET } else { "stm32-debug" }

Push-Location $RootDir
try {
  cmake --preset $Preset

  $BuildArgs = @("--build", "--preset", $Preset)
  if ($env:JOBS) {
    $BuildArgs += @("--parallel", $env:JOBS)
  }
  cmake @BuildArgs
} finally {
  Pop-Location
}
