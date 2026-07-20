# image_tool

A modern C++ command-line utility for inspecting image metadata.

## Prerequisites

- macOS Apple Silicon (arm64) host
- Xcode Command Line Tools
- CMake >= 3.25
- Ninja
- vcpkg
- clang-format and clang-tidy (from Homebrew or Xcode)

## Build

```bash
cmake --preset macos-arm64-debug
cmake --build --preset macos-arm64-debug
```

## Test

```bash
ctest --preset macos-arm64-debug
```

## Run

```bash
./build/macos-arm64-debug/image_tool --list-formats
./build/macos-arm64-debug/image_tool --input /path/to/image.png
```

## Format and Lint

```bash
clang-format -i src/**/*.cpp include/**/*.hpp tests/**/*.cpp
clang-tidy -p build/macos-arm64-debug src/**/*.cpp tests/**/*.cpp
```

## VS Code

Open the workspace folder. Use `CMake: build macos-arm64-debug` and the
`Debug image_tool (arm64)` launch configuration.
