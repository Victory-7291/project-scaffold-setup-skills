# Modern Embedded Project Blueprint

## Toolchain

Use this local development chain for STM32/Cortex-M firmware:

```text
VS Code
  -> clangd
  -> clang-format
  -> clang-tidy
  -> CMake
  -> Ninja
  -> arm-none-eabi-gcc
  -> firmware.elf / firmware.bin / firmware.hex
  -> OpenOCD + ST-Link or J-Link
  -> STM32 MCU
```

Use this CI chain when GitHub Actions or another CI system is part of the task:

```text
Git push
  -> Docker toolchain image
  -> clang-format check
  -> clang-tidy
  -> CMake
  -> Ninja
  -> arm-none-eabi-gcc
  -> ELF/BIN/HEX artifacts
  -> optional unit tests
  -> release or artifact upload
```

## Greenfield Layout

Prefer this structure for a new firmware project:

```text
firmware/
  CMakeLists.txt
  CMakePresets.json
  cmake/
    arm-none-eabi-gcc.cmake
  include/
    project_config.h
  src/
    main.c
    app/
      app.c
      app.h
    bsp/
      board.c
      board.h
    drivers/
  startup/
    startup.c
  ldscripts/
    <mcu>_flash.ld
  scripts/
    build.sh
    analyze.sh
    flash.sh
    openocd_server.sh
  .vscode/
    extensions.json
    settings.json
    launch.json
  .clangd
  .clang-format
  .clang-tidy
  Dockerfile
  .github/workflows/firmware.yml
  README.md
```

## Layering

Keep the software stack explicit:

```text
Application
  -> board support / drivers / middleware
  -> HAL API, LL API, or direct registers
  -> CMSIS Device
  -> Cortex-M processor
  -> STM32 peripheral hardware
```

- Use CMSIS for CPU/device definitions when available.
- Use HAL when portability, official examples, and team velocity matter.
- Use LL when peripheral paths need less abstraction but still benefit from vendor definitions.
- Use bare-metal registers for startup, board smoke tests, bootloaders, or tightly constrained paths.
- Do not treat `clangd` as the compiler; it consumes `compile_commands.json` produced by CMake.

## CMake Decisions

- Use `CMAKE_SYSTEM_NAME Generic` and `CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY` in the toolchain file.
- Set `CMAKE_EXPORT_COMPILE_COMMANDS` to `ON`.
- Keep CPU, FPU, float ABI, MCU define, linker script, and OpenOCD target visible in generated files.
- Produce `.elf`, `.bin`, `.hex`, `.map`, and `arm-none-eabi-size` output after build.
- Keep `stm32-debug`, `stm32-release`, and `stm32-analyze` presets.
- Enable clang-tidy only in the analyze preset or behind an option.
- A minimal smoke firmware can use `-nostdlib` and avoid C library headers. When the project starts using libc, printf, HAL code that expects standard headers, or syscalls, add the matching newlib/runtime package and switch linker specs deliberately.

## Debug and Flash Decisions

- Use OpenOCD as the bridge between GDB and ST-Link/J-Link.
- Use Cortex-Debug in VS Code for interactive debug.
- Keep CLI scripts for build, analyze, flash, and OpenOCD server startup.
- Run flash/debug commands only when hardware is attached and the user expects hardware access.
- If flashing fails, check power, SWD wiring, OpenOCD target file, probe interface file, and SWD speed.

## CI Decisions

- Use Docker to pin GCC, CMake, Ninja, OpenOCD, clang-format, and clang-tidy versions.
- Trigger CI on firmware paths, workflow paths, and toolchain files.
- Upload `.elf`, `.bin`, `.hex`, and `.map` artifacts.
- Add host-side unit tests later for portable modules; do not block initial MCU bring-up on a test harness unless requested.

## Existing Firmware Rules

- Do not mix app and firmware build systems without a clear boundary.
- Do not move vendor HAL/CMSIS trees unless all include paths, linker/startup references, docs, and CI are updated.
- Preserve chip-specific linker scripts and startup files unless the target MCU changes.
- Treat CubeMX-generated files as user/vendor-owned unless the repo already marks editable sections.
