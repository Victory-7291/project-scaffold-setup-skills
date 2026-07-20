# ImageTool

Modern C++ scaffold using CMake presets, Ninja, vcpkg manifest mode, GoogleTest,
clang-format, clang-tidy, Doxygen, and VS Code.

## Host Toolchain

Selected host profile: `macos-arm64`

macOS Apple Silicon:

```bash
brew install cmake ninja llvm git doxygen
bash scripts/bootstrap_vcpkg.sh
```

If you are generating this project for another machine, rerun the scaffold with
`--host-platform macos-arm64`, `macos-x64`, `linux-x64`, `linux-arm64`,
`windows-x64`, or `windows-arm64`.

## Build

```bash
bash scripts/bootstrap_vcpkg.sh
cmake --preset macos-arm64-debug
cmake --build --preset macos-arm64-debug
ctest --test-dir build/macos-arm64-debug --output-on-failure
```

## Quality

```bash
bash scripts/format.sh --check
cmake --preset macos-arm64-tidy
cmake --build --preset macos-arm64-tidy
cmake --build --preset macos-arm64-debug --target docs
```
