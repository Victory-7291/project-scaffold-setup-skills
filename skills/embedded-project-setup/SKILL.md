---
name: embedded-project-setup
description: Create, modify or improve modern STM32/Cortex-M embedded C firmware projects with platform-aware host toolchains for macOS/Linux/Windows on arm64 or x64, VS Code, clangd, clang-format, clang-tidy, CMakePresets.json, Ninja, arm-none-eabi-gcc/gdb, firmware ELF/BIN/HEX/MAP outputs, OpenOCD, ST-Link or J-Link, Cortex-Debug, Docker/GitHub Actions, and layered CMSIS/HAL/LL/bare-metal structure. Use when users is asked to bootstrap new MCU firmware, inspect and modernize an existing firmware repo, create cross CMake toolchains, VS Code Cortex-Debug configs, flashing/debug scripts, linker/startup files, BSP smoke code, or embedded CI. Prefer cpp-project-setup for host-side C++ app/library projects.
---

# Modern Embedded Project Setup

## Overview

Create or modernize embedded C firmware around this pipeline:

```text
VS Code -> clangd -> clang-format -> clang-tidy -> CMake -> Ninja -> GCC -> ELF/BIN -> OpenOCD -> MCU
```

Treat editor analysis, static checks, build generation, cross compilation, flashing, and debug as separate stages. First classify the user's working directory and host platform, then either generate a greenfield scaffold or modernize the existing firmware pipeline.

## Workflow

1. Determine the user's working directory and whether firmware already exists.
   - Check the user-provided path or current working directory before writing files.
   - Treat the directory as an existing firmware project if it already has source files, linker scripts, startup files, CubeMX files, CMake/Make/build scripts, vendor trees, flash/debug scripts, editor settings, CI, docs, or git history.
   - For existing firmware, inventory the full development pipeline before editing: build system, toolchain file, compiler version, MCU/board assumptions, linker/startup flow, vendor dependency model, flash/debug flow, tests or host-side checks, formatting/linting/static analysis, CI, and firmware artifacts.

2. Detect the user's host development environment.
   - Determine OS and architecture: macOS/Linux/Windows plus arm64 or x64. Use local commands such as `uname -s`, `uname -m`, or PowerShell/.NET runtime information where appropriate.
   - Select a host profile: `macos-arm64`, `macos-x64`, `linux-x64`, `linux-arm64`, `windows-x64`, or `windows-arm64`.
   - If the agent is running somewhere other than the user's real development machine, ask for the user's OS/architecture instead of assuming the sandbox matches their workstation.

3. Identify the firmware target before writing files.
   - Capture MCU, board, debug probe, flash/RAM size, CPU core, FPU/float ABI, OpenOCD target file, and whether the project will use CMSIS, HAL, LL, bare-metal register access, or a mix.
   - If unspecified, default to a minimal STM32G030C8T6 smoke project: Cortex-M0+, 64 KiB flash, 8 KiB RAM, ST-Link, OpenOCD target `stm32g0x`.

4. Generate or update the project.
   - For greenfield scaffolding, run from this skill directory:

```bash
python3 scripts/scaffold_embedded_project.py \
  --name firmware \
  --out /path/to/workspace/firmware \
  --host-platform macos-arm64
```

   - For existing firmware, inspect `CMakeLists.txt`, `CMakePresets.json`, toolchain files, linker scripts, startup files, `.vscode/`, `.clangd`, `.clang-tidy`, flash/debug scripts, Dockerfile, CI workflows, and local docs before editing.
   - Omit `--host-platform` only when generating on the same machine where the project will be developed; the script will auto-detect that host.

5. Preserve the embedded layer model.
   - Keep application logic above board support and drivers.
   - Keep CMSIS as the lowest common Cortex-M/device layer when vendor headers are available.
   - Use HAL for portability and team velocity, LL for tighter peripheral paths, and direct registers only for startup, BSP smoke tests, bootloaders, or performance-critical code.
   - Do not vendor-copy STM32Cube or HAL trees blindly; prefer a documented submodule, package, or user-provided vendor directory.

6. Wire the toolchain.
   - Use CMake presets for `stm32-debug`, `stm32-release`, and `stm32-analyze`.
   - Use a `cmake/arm-none-eabi-gcc.cmake` toolchain file.
   - Export `compile_commands.json` for clangd.
   - Pass the embedded target triple to clangd and clang-tidy so host LLVM tools understand ARM CPU flags.
   - Use Ninja for builds.
   - Produce `.elf`, `.bin`, `.hex`, `.map`, and size output.

7. Wire editor, flashing, and debug.
   - Recommend VS Code extensions: clangd, CMake Tools, Cortex-Debug.
   - Disable competing IntelliSense when clangd owns semantic analysis.
   - Use OpenOCD with ST-Link or J-Link as the GDB server.
   - Keep shell and PowerShell command entry points for build, format, analyze, flash, and OpenOCD server startup when generating a cross-platform scaffold.

## Validation

Run what is available locally:

```bash
cmake --preset stm32-debug
cmake --build --preset stm32-debug
bash scripts/format.sh --check
cmake --preset stm32-analyze
cmake --build --preset stm32-analyze
```

On Windows, use the generated PowerShell entry points such as `pwsh scripts/build.ps1`, `pwsh scripts/format.ps1 -Check`, and `pwsh scripts/analyze.ps1`.

Run flashing or debug validation only when hardware is attached and the user expects hardware access:

```bash
bash scripts/flash.sh
bash scripts/openocd_server.sh
```

If `clang-format`, `clang-tidy`, `arm-none-eabi-gcc`, OpenOCD, or hardware is unavailable, report the skipped step and leave the project ready for that tool.

## References

- Read `references/embedded-project-blueprint.md` when choosing directory layout, CMake/toolchain settings, STM32 software layers, flashing/debug flow, or CI design.
- Read the scaffold script before changing generated linker/startup defaults, supported MCU arguments, or generated command entry points.
