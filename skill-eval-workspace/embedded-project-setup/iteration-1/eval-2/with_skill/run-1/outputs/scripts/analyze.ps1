$ErrorActionPreference = "Stop"

$PreviousPreset = $env:PRESET
$env:PRESET = "stm32-analyze"
try {
  & (Join-Path $PSScriptRoot "build.ps1")
} finally {
  $env:PRESET = $PreviousPreset
}
