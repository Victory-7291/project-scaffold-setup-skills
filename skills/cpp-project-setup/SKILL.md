---
name: cpp-project-setup
description: Set up modern C++ projects from scratch with Git/GitHub, VS Code, CMake Tools, clangd, CodeLLDB or Windows C/C++ debugging, CMakePresets.json, vcpkg manifest mode, platform triplets, Ninja, Clang/GCC/MSVC, GoogleTest, clang-format, clang-tidy, Doxygen, and CI-ready structure. Use when Codex is asked to bootstrap, standardize, or modernize a C++ CMake project; create VS Code C++ settings; add vcpkg/CMake presets; establish tests, linting, formatting, documentation, or a reproducible developer workflow.
---

# Modern C++ Project Setup

## Overview

Create or modernize a C++ project around a reproducible toolchain:

```text
Git -> GitHub -> VS Code -> CMakePresets + vcpkg -> Ninja -> compiler -> tests/lint/docs
```

Prefer project-local, repeatable setup over global machine assumptions. Use the bundled scaffold script for greenfield projects; patch existing projects carefully after reading their current CMake, dependency, and editor configuration.

## Workflow

1. Determine whether the task is greenfield or an existing project.
   - For greenfield work, default to an app plus reusable library target, C++20, Ninja, vcpkg manifest mode, GoogleTest, clang-format, clang-tidy, Doxygen, and VS Code settings.
   - For existing work, inspect `CMakeLists.txt`, `CMakePresets.json`, `vcpkg.json`, `.vscode/`, `.clangd`, `.clang-format`, `.clang-tidy`, CI files, and local docs before editing.

2. Generate or update the project.
   - For greenfield scaffolding, run:

```bash
python3 /Users/wan/.codex/skills/cpp-project-setup/scripts/scaffold_cpp_project.py \
  --name my_app \
  --out /path/to/workspace/my_app
```

   - For existing projects, use `references/cpp-project-blueprint.md` as a checklist and adapt to the repository's current style instead of replacing unrelated files.

3. Keep the toolchain contract explicit.
   - Use `CMakePresets.json` for configure/build profiles.
   - Use vcpkg manifest mode through `vcpkg.json`.
   - Use triplets such as `arm64-osx`, `x64-linux`, and `x64-windows`.
   - Use Ninja as the generator unless the user or platform requires otherwise.
   - Use Clang on macOS, GCC on Linux, and MSVC on Windows by default.

4. Wire editor support.
   - Recommend VS Code extensions: CMake Tools, clangd, CodeLLDB for macOS/Linux, and Microsoft C/C++ debugging support for Windows.
   - Disable competing IntelliSense when clangd is responsible for semantic analysis.
   - Make `compile_commands.json` available through CMake configure output and point clangd at the active preset's build directory.

5. Add quality gates.
   - Add GoogleTest tests with `ctest`.
   - Add `.clang-format` and `.clang-tidy`.
   - Add a Doxygen configuration path, but do not require docs generation for a normal build.
   - Add CI only when requested or when the project setup task includes GitHub/GitHub Actions.

## Validation

Run the strongest available validation for the target machine:

```bash
bash scripts/bootstrap_vcpkg.sh
cmake --preset macos-debug
cmake --build --preset macos-debug
ctest --test-dir build/macos-debug --output-on-failure
cmake --preset macos-tidy
cmake --build --preset macos-tidy
```

Adjust preset names for Linux or Windows. If vcpkg, compilers, or Doxygen are unavailable, report exactly what was skipped and why.

## References

- Read `references/cpp-project-blueprint.md` when choosing project layout, presets, dependency policy, editor settings, tests, formatting, linting, docs, or CI details.
- Read the scaffold script before changing its generated files or adding new options.
