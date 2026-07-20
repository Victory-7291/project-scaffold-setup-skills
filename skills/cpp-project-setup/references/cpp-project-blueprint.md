# Modern C++ Project Blueprint

## Toolchain

Use this default chain unless the user or repository has a stronger existing convention:

```text
Git
  -> GitHub
  -> VS Code
       -> CMake Tools
       -> clangd
       -> CodeLLDB on macOS/Linux, C/C++ debugging on Windows
  -> CMake
       -> CMakePresets.json
       -> vcpkg manifest mode
       -> platform triplets such as arm64-osx, x64-linux, x64-windows
  -> Ninja
  -> Clang on macOS, GCC on Linux, MSVC on Windows
       -> GoogleTest
       -> clang-format
       -> clang-tidy
       -> Doxygen
```

## Discovery First

Before generating or patching files, classify the user's workspace:

- Greenfield: the target directory is empty or clearly meant to be created.
- Existing project: the directory already has source files, build metadata, scripts, editor settings, CI, docs, or git history.

For existing projects, write down the current pipeline before editing:

- Build system: CMake, Make, Meson, Bazel, Visual Studio solutions, ad hoc scripts, or mixed.
- Dependency model: vcpkg, Conan, FetchContent, submodules, system packages, vendored code, or none.
- Compiler and standard: Clang/GCC/MSVC, C++ version, warnings, platform assumptions.
- Developer entry points: presets, shell scripts, PowerShell scripts, VS Code tasks, Make targets, CI jobs.
- Quality gates: tests, format, lint, static analysis, docs, packaging, install/export rules.

Modernize by filling gaps in that pipeline instead of replacing a working build graph.

## Host Profiles

Choose the developer host profile from the user's real machine, not necessarily the agent sandbox:

| Host profile | vcpkg triplet | Default compiler/debugger | Notes |
| --- | --- | --- | --- |
| `macos-arm64` | `arm64-osx` | Clang + CodeLLDB | Apple Silicon Homebrew installs are usually under `/opt/homebrew`. |
| `macos-x64` | `x64-osx` | Clang + CodeLLDB | Intel Homebrew installs are often under `/usr/local`. |
| `linux-x64` | `x64-linux` | GCC or Clang + CodeLLDB | Use distro packages for CMake, Ninja, LLVM tools, Doxygen, and build essentials. |
| `linux-arm64` | `arm64-linux` | GCC or Clang + CodeLLDB | Same project shape as Linux x64, different vcpkg triplet and package availability. |
| `windows-x64` | `x64-windows` | MSVC + `cppvsdbg` | Run CMake from a Visual Studio Developer PowerShell or Developer Command Prompt. |
| `windows-arm64` | `arm64-windows` | MSVC ARM64 + `cppvsdbg` | Install the ARM64 C++ build tools workload. |

## Greenfield Layout

Prefer this structure for a new project:

```text
project/
  CMakeLists.txt
  CMakePresets.json
  vcpkg.json
  cmake/
    Warnings.cmake
  include/<project>/
    core.hpp
  src/
    CMakeLists.txt
    core.cpp
    main.cpp
  tests/
    CMakeLists.txt
    test_core.cpp
  docs/
    Doxyfile.in
  scripts/
    bootstrap_vcpkg.sh
    bootstrap_vcpkg.ps1
    format.sh
    format.ps1
  .vscode/
    extensions.json
    settings.json
    launch.json
  .clangd
  .clang-format
  .clang-tidy
  .gitignore
  README.md
```

## CMake Decisions

- Set `CMAKE_EXPORT_COMPILE_COMMANDS` to `ON`.
- Keep C++ standard explicit and disable compiler extensions.
- Put reusable code in a library target even when the project also has an executable.
- Link tests against the library target, not against app internals.
- Keep warning flags in `cmake/Warnings.cmake` so target setup stays readable.
- Use `PROJECT_ENABLE_CLANG_TIDY` or a project-prefixed equivalent instead of forcing clang-tidy on every build.
- Use Doxygen behind an option or explicit `docs` target so normal builds stay fast.

## vcpkg Decisions

- Use manifest mode with `vcpkg.json`.
- Prefer project-local bootstrap (`.vcpkg/`) when the user wants reproducibility.
- Keep `.vcpkg/` ignored by git; commit `vcpkg.json`, not installed packages.
- Provide a shell bootstrap for macOS/Linux and a PowerShell bootstrap for Windows when generating a cross-platform scaffold.
- Use triplets in presets:
  - macOS Apple Silicon: `arm64-osx`
  - macOS Intel: `x64-osx`
  - Linux x64: `x64-linux`
  - Linux arm64: `arm64-linux`
  - Windows x64: `x64-windows`
  - Windows arm64: `arm64-windows`

## VS Code Decisions

- Recommend `ms-vscode.cmake-tools`, `llvm-vs-code-extensions.vscode-clangd`, `vadimcn.vscode-lldb`, and `ms-vscode.cpptools`.
- Disable Microsoft IntelliSense if clangd owns semantic analysis.
- Use CMake Tools presets instead of hand-written build tasks.
- Add launch configs only for concrete executables; use CodeLLDB for macOS/Linux and `cppvsdbg` for Windows/MSVC.
- Keep clangd pointed at the active preset's build directory; update this path if the user changes presets.

## Quality Gates

Use these local checks where possible:

```bash
bash scripts/bootstrap_vcpkg.sh
cmake --preset macos-arm64-debug
cmake --build --preset macos-arm64-debug
ctest --test-dir build/macos-arm64-debug --output-on-failure
bash scripts/format.sh --check
cmake --preset macos-arm64-tidy
cmake --build --preset macos-arm64-tidy
cmake --build --preset macos-arm64-debug --target docs
```

Use the selected host profile's preset names on Linux, Windows, or non-arm64 macOS. On Windows, prefer the generated PowerShell scripts.

## Existing Project Rules

- Do not replace a hand-tuned CMake graph without first understanding targets, install rules, exported packages, and CI.
- Preserve user-owned dependency managers unless asked to migrate.
- If adding vcpkg to a project that already uses submodules, Conan, FetchContent, or system packages, document the transition and keep the edit scoped.
- Update docs when changing build, dependency, or editor workflow.
