param(
  [switch]$Check
)

$ErrorActionPreference = "Stop"
$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$SearchRoots = @("include", "src", "startup")
$Extensions = @(".h", ".c")

if (-not (Get-Command clang-format -ErrorAction SilentlyContinue)) {
  throw "clang-format is required"
}

$Files = @()
foreach ($SearchRoot in $SearchRoots) {
  $Path = Join-Path $RootDir $SearchRoot
  if (Test-Path $Path) {
    $Files += Get-ChildItem $Path -Recurse -File | Where-Object { $Extensions -contains $_.Extension }
  }
}

if ($Files.Count -eq 0) {
  exit 0
}

$FilePaths = @($Files | ForEach-Object { $_.FullName })
if ($Check) {
  clang-format --dry-run --Werror @FilePaths
} else {
  clang-format -i @FilePaths
}
