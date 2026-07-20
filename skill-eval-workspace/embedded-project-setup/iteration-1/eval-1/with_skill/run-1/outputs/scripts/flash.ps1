$ErrorActionPreference = "Stop"

$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$Preset = if ($env:PRESET) { $env:PRESET } else { "stm32-debug" }
$Elf = Join-Path $RootDir "build/$Preset/motor_ctrl.elf"

& (Join-Path $PSScriptRoot "build.ps1")

openocd `
  -f "interface/stlink.cfg" `
  -f "target/stm32f4x.cfg" `
  -c "program `"$Elf`" verify reset exit"
