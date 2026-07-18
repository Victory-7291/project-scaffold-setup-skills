---
name: embedded-project-setup
description: Set up modern C or STM32/Cortex-M embedded projects from scratch with VS Code, clangd, clang-format, clang-tidy, CMakePresets.json, Ninja, arm-none-eabi-gcc, arm-none-eabi-gdb, firmware ELF/BIN/HEX outputs, OpenOCD, ST-Link or J-Link, Cortex-Debug, Docker/GitHub Actions, and layered CMSIS/HAL/LL/bare-metal structure. Use when Codex is asked to bootstrap, standardize, or modernize embedded firmware; create CMake toolchains, VS Code Cortex-Debug configs, flashing/debug scripts, linker/startup files, or embedded CI.
---

# Modern Embedded Project Setup

## Overview

Create or modernize embedded C firmware around this pipeline:

```text
VS Code -> clangd -> clang-format -> clang-tidy -> CMake -> Ninja -> GCC -> ELF/BIN -> OpenOCD -> MCU
```

Treat editor analysis, static checks, build generation, cross compilation, flashing, and debug as separate stages. This keeps local development, CI, and hardware bring-up predictable.

## Workflow

1. Identify the target before writing files.
   - Capture MCU, board, debug probe, flash/RAM size, CPU core, FPU/float ABI, OpenOCD target file, and whether the project will use CMSIS, HAL, LL, bare-metal register access, or a mix.
   - If unspecified, default to a minimal STM32G030C8T6 smoke project: Cortex-M0+, 64 KiB flash, 8 KiB RAM, ST-Link, OpenOCD target `stm32g0x`.

2. Generate or update the project.
   - For greenfield scaffolding, run from this skill directory:

```bash
python3 scripts/scaffold_embedded_project.py \
  --name firmware \
  --out /path/to/workspace/firmware
```

   - For existing firmware, inspect `CMakeLists.txt`, `CMakePresets.json`, toolchain files, linker scripts, startup files, `.vscode/`, `.clangd`, `.clang-tidy`, flash/debug scripts, Dockerfile, CI workflows, and local docs before editing.

3. Preserve the embedded layer model.
   - Keep application logic above board support and drivers.
   - Keep CMSIS as the lowest common Cortex-M/device layer when vendor headers are available.
   - Use HAL for portability and team velocity, LL for tighter peripheral paths, and direct registers only for startup, BSP smoke tests, bootloaders, or performance-critical code.
   - Do not vendor-copy STM32Cube or HAL trees blindly; prefer a documented submodule, package, or user-provided vendor directory.

4. Wire the toolchain.
   - Use CMake presets for `stm32-debug`, `stm32-release`, and `stm32-analyze`.
   - Use a `cmake/arm-none-eabi-gcc.cmake` toolchain file.
   - Export `compile_commands.json` for clangd.
   - Use Ninja for builds.
   - Produce `.elf`, `.bin`, `.hex`, `.map`, and size output.

5. Wire editor, flashing, and debug.
   - Recommend VS Code extensions: clangd, CMake Tools, Cortex-Debug.
   - Disable competing IntelliSense when clangd owns semantic analysis.
   - Use OpenOCD with ST-Link or J-Link as the GDB server.
   - Keep `scripts/build.sh`, `scripts/analyze.sh`, `scripts/flash.sh`, and `scripts/openocd_server.sh` as simple command-line entry points.

## Validation

Run what is available locally:

```bash
cmake --preset stm32-debug
cmake --build --preset stm32-debug
cmake --preset stm32-analyze
cmake --build --preset stm32-analyze
```

Run flashing or debug validation only when hardware is attached and the user expects hardware access:

```bash
bash scripts/flash.sh
bash scripts/openocd_server.sh
```

If `arm-none-eabi-gcc`, OpenOCD, or hardware is unavailable, report the skipped step and leave the project ready for that tool.

## References

- Read `references/embedded-project-blueprint.md` when choosing directory layout, CMake/toolchain settings, STM32 software layers, flashing/debug flow, or CI design.
- Read the scaffold script before changing generated linker/startup defaults, supported MCU arguments, or generated command entry points.
