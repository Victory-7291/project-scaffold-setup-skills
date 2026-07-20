#Requires -Version 5.1
<#
.SYNOPSIS
    Bootstraps the math_utils development environment on Windows x64.
.DESCRIPTION
    Configures CMake with the Windows x64 toolchain and builds the project.
#>
[CmdletBinding()]
param(
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Debug',

    [string]$BuildDirectory = "$PSScriptRoot\..\build\windows-x64-$($Configuration.ToLowerInvariant())"
)

$ErrorActionPreference = 'Stop'

$projectRoot = Resolve-Path -Path "$PSScriptRoot\.."
$toolchain = Join-Path $projectRoot 'cmake\toolchain-x64-windows.cmake'

if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
    throw 'CMake is not available in PATH. Please install CMake and try again.'
}

Write-Host "Bootstrapping math_utils for Windows x64 ($Configuration)..." -ForegroundColor Cyan
Write-Host "Project root: $projectRoot"
Write-Host "Build directory: $BuildDirectory"

$cmakeArgs = @(
    '-S', $projectRoot
    '-B', $BuildDirectory
    '-G', 'Visual Studio 17 2022'
    '-A', 'x64'
    '-T', 'ClangCL'
    "-DCMAKE_TOOLCHAIN_FILE=$toolchain"
    "-DCMAKE_BUILD_TYPE=$Configuration"
    '-DMATH_UTILS_BUILD_TESTS=ON'
    '-DMATH_UTILS_ENABLE_CLANG_TIDY=ON'
)

& cmake @cmakeArgs
if ($LASTEXITCODE -ne 0) {
    throw "CMake configuration failed with exit code $LASTEXITCODE"
}

& cmake --build $BuildDirectory --config $Configuration --parallel
if ($LASTEXITCODE -ne 0) {
    throw "Build failed with exit code $LASTEXITCODE"
}

& ctest --test-dir $BuildDirectory --build-config $Configuration --output-on-failure
if ($LASTEXITCODE -ne 0) {
    throw "Tests failed with exit code $LASTEXITCODE"
}

Write-Host 'Bootstrap completed successfully.' -ForegroundColor Green
