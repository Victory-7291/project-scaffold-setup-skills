#Requires -Version 5.1
<#
.SYNOPSIS
    Formats all C++ source and header files in the math_utils project.
.DESCRIPTION
    Uses clang-format to format source files in include, src, and tests.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$projectRoot = Resolve-Path -Path "$PSScriptRoot\.."

$clangFormat = Get-Command clang-format -ErrorAction SilentlyContinue
if (-not $clangFormat) {
    throw 'clang-format is not available in PATH. Please install LLVM and try again.'
}

$extensions = @('*.cpp', '*.hpp', '*.h')
$directories = @(
    Join-Path $projectRoot 'include'
    Join-Path $projectRoot 'src'
    Join-Path $projectRoot 'tests'
)

$files = foreach ($dir in $directories) {
    if (Test-Path $dir) {
        foreach ($ext in $extensions) {
            Get-ChildItem -Path $dir -Recurse -Filter $ext -File -ErrorAction SilentlyContinue
        }
    }
}

if (-not $files) {
    Write-Host 'No source files found to format.' -ForegroundColor Yellow
    return
}

Write-Host "Formatting $($files.Count) source file(s) with clang-format..." -ForegroundColor Cyan
& $clangFormat -i @files
if ($LASTEXITCODE -ne 0) {
    throw "clang-format failed with exit code $LASTEXITCODE"
}

Write-Host 'Formatting completed successfully.' -ForegroundColor Green
