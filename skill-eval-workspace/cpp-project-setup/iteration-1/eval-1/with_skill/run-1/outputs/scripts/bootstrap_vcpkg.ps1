$ErrorActionPreference = "Stop"

$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$VcpkgDir = Join-Path $RootDir ".vcpkg"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "git is required to bootstrap vcpkg"
}

if (-not (Test-Path (Join-Path $VcpkgDir ".git"))) {
  git clone https://github.com/microsoft/vcpkg $VcpkgDir
}

& (Join-Path $VcpkgDir "bootstrap-vcpkg.bat") -disableMetrics
