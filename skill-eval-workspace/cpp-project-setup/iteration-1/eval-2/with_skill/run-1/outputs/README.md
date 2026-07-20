# MathUtils

Modern C++ scaffold using CMake presets, Ninja, vcpkg manifest mode, GoogleTest,
clang-format, clang-tidy, Doxygen, and VS Code.

## Host Toolchain

Selected host profile: `windows-x64`

Windows x64:

Install Visual Studio 2022 Build Tools with the Desktop development with C++ workload,
CMake, Ninja, Git, LLVM, and Doxygen. Then run from a Developer PowerShell:

```powershell
pwsh scripts/bootstrap_vcpkg.ps1
```

If you are generating this project for another machine, rerun the scaffold with
`--host-platform macos-arm64`, `macos-x64`, `linux-x64`, `linux-arm64`,
`windows-x64`, or `windows-arm64`.

## Build

```powershell
pwsh scripts/bootstrap_vcpkg.ps1
cmake --preset windows-x64-debug
cmake --build --preset windows-x64-debug
ctest --test-dir build/windows-x64-debug --output-on-failure
```

## Quality

```powershell
pwsh scripts/format.ps1 -Check
cmake --preset windows-x64-tidy
cmake --build --preset windows-x64-tidy
cmake --build --preset windows-x64-debug --target docs
```
