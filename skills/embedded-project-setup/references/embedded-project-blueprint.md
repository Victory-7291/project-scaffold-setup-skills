# Modern Embedded Project Blueprint

## Toolchain

Use this local development chain for Arm Cortex-M firmware:

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
  -> Cortex-M MCU
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

## Discovery First

Before generating or patching files, classify the user's workspace:

- Greenfield: the target directory is empty or clearly meant to be created.
- Existing firmware: the directory already has source files, linker scripts, startup files, CubeMX metadata, vendor trees, build scripts, editor settings, CI, docs, or git history.

For existing firmware, write down the current pipeline before editing:

- Build system: CMake, Make, vendor IDE, CubeMX output, custom scripts, or mixed.
- Toolchain: `arm-none-eabi-gcc`, vendor compiler, clang-based flow, compiler version, CPU/FPU/float ABI flags.
- Firmware target: vendor/family, MCU, board, memory origins and sizes, linker script, startup file, vector table, bootloader assumptions.
- Dependency model: firmware package/SDK name, version/tag, source URL, local path, CMSIS when applicable, vendor HAL/LL or SDK drivers, RTOS kernel, submodules, `west` manifests, generated vendor trees, package managers, or global SDK paths.
- Developer entry points: presets, scripts, VS Code tasks, flash/debug commands, OpenOCD/J-Link configs.
- Quality gates: format, lint/static analysis, host tests, firmware artifacts, CI and release upload.

Modernize by preserving proven hardware bring-up details and filling gaps in the toolchain.

## Host Profiles

Choose the developer host profile from the user's real machine, not necessarily the agent sandbox:

| Host profile | Toolchain install path | Notes |
| --- | --- | --- |
| `macos-arm64` | Homebrew packages for CMake, Ninja, LLVM tools, OpenOCD, Arm GNU toolchain | Apple Silicon Homebrew installs are usually under `/opt/homebrew`. |
| `macos-x64` | Homebrew packages for CMake, Ninja, LLVM tools, OpenOCD, Arm GNU toolchain | Intel Homebrew installs are often under `/usr/local`. |
| `linux-x64` | Distro packages such as `gcc-arm-none-eabi`, `binutils-arm-none-eabi`, `gdb-multiarch`, `openocd` | Package names vary by distribution. |
| `linux-arm64` | Same package families as Linux x64 | Some distros lag on embedded toolchain package versions. |
| `windows-x64` | Arm GNU Toolchain for Windows, CMake, Ninja, OpenOCD, LLVM tools on `PATH` | Use PowerShell scripts or a shell with the same tools on `PATH`. |
| `windows-arm64` | Native arm64 packages when available; otherwise compatible x64 tools | Verify debugger/probe drivers on the target machine. |

## Firmware Package First

Choose and pin the target firmware package before generating include paths or source lists. The package is the layer that replaces the blind parts of vendor IDE or CubeMX output: CMSIS/device headers, HAL/LL or SDK drivers, startup/linker examples, board support, middleware, RTOS integration, and flash/debug conventions.

Use `references/firmware-package-matrix.md` for the detailed target-to-package mapping. The short version:

| Target | Package decision |
| --- | --- |
| STM32 | Use the matching `STM32Cube<series>` package, such as `STM32CubeG0`, under `vendor/` or an external path. Select CMSIS and the HAL/LL files needed by the app; do not compile every example. |
| ESP32 | Use ESP-IDF and `idf.py`; avoid generic Arm CMake toolchains. |
| AVR | Use AVR GNU Toolchain plus AVR-LibC, with Microchip `.atpack` device support when required. CMSIS is not part of this stack. |
| RP2040/RP2350 | Use Pico SDK through `PICO_SDK_PATH`, a submodule, or the SDK import file. |
| Nordic nRF | Prefer nRF Connect SDK managed by `west`; use direct `nrfx` plus CMSIS only for explicit bare-metal or legacy needs. |
| Zephyr/RTOS | Let Zephyr or the vendor RTOS package own board, startup, linker, devicetree/Kconfig, and flash runners where applicable. For standalone FreeRTOS, pick the vendor silicon package first, then add the RTOS kernel. |

Document the dependency path in the README. If package fetching needs network approval, leave exact commands rather than fake files.

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
  vendor/
    README.md
  scripts/
    build.sh
    build.ps1
    format.sh
    format.ps1
    analyze.sh
    analyze.ps1
    flash.sh
    flash.ps1
    openocd_server.sh
    openocd_server.ps1
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

Treat `vendor/` as optional and target-specific. STM32Cube and Pico SDK often fit there as pinned submodules. ESP-IDF, nRF Connect SDK, and Zephyr often use external SDK paths or `west` workspaces instead of a per-project vendor tree. If the target uses `west`, place `west.yml`, board overlays, `prj.conf`, and application CMake files according to the Zephyr/NCS application model rather than forcing this direct Cortex-M layout.

## Target Model

Separate the reusable Cortex-M toolchain from target-family details:

| Field | Why it matters | Examples |
| --- | --- | --- |
| Target family | Names presets, docs, and generated comments without locking the scaffold to one vendor. | `generic-cortex-m`, `stm32g0`, `nrf52`, `rp2040`, `samd21`, `lpc17xx` |
| MCU | Names the actual silicon target for docs, debug config, and device defines. | `stm32g030c8t6`, `nrf52840`, `rp2040`, `atsamd21g18a` |
| Board | Captures probe wiring, LEDs, clocks, power, and external memory assumptions. | `nucleo-f446re`, `custom-nrf52840-board` |
| CPU/FPU/float ABI | Controls GCC/clangd flags and ABI compatibility. | `cortex-m0plus`, `cortex-m4` + `fpv4-sp-d16` + `hard` |
| Memory map | Controls linker script origins and sizes. | flash at `0x08000000` for many STM32 parts, `0x00000000` for many vendor maps, `0x10000000` for RP2040 XIP |
| OpenOCD probe/target | Controls flash/debug access and cannot be guessed reliably across vendors. | `interface/stlink.cfg`, `interface/jlink.cfg`, `target/stm32f4x.cfg`, `target/nrf52.cfg`, `target/rp2040.cfg` |
| BSP template | Determines whether generated smoke code touches real hardware. | `portable` for build-only smoke, target-specific templates only when known-correct |

For an unknown target, generate the portable BSP so the project can compile without board-specific register writes. Treat LED blink, clock setup, pinmux, external memory, and vendor HAL integration as target-specific follow-up work.

## Reusable Templates

Keep stable generated configuration in `assets/` and render it through the scaffold script:

- `CMakeLists.txt`
- `CMakePresets.json`
- `.clangd`
- `.clang-tidy`
- `.vscode/settings.json`
- `.vscode/extensions.json`
- `.vscode/launch.json`
- `.vscode/tasks.json`
- `Dockerfile`
- `.dockerignore`

Use `@PLACEHOLDER@` values for firmware target names, target family, board, MCU, CPU flags, device defines, memory origins/sizes, OpenOCD interface/target files, clang target, CMake preset names, and selected clangd preset. Do not copy product secrets, absolute workstation paths, vendor tree assumptions, or a board-specific HAL source list into the generic templates.

## Layering

Keep the software stack explicit. A direct Cortex-M STM32-style project often looks like this:

```text
Application
  -> board support / drivers / middleware
  -> vendor HAL/LL/SDK API or direct registers
  -> CMSIS Device
  -> Cortex-M processor
  -> MCU peripheral hardware
```

- Use CMSIS for CPU/device definitions when available on Cortex-M targets.
- Use vendor HALs or SDK drivers when portability, official examples, and team velocity matter.
- Use lower-level vendor APIs when peripheral paths need less abstraction but still benefit from vendor definitions.
- Use bare-metal registers for startup, board smoke tests, bootloaders, or tightly constrained paths.
- Do not treat `clangd` as the compiler; it consumes `compile_commands.json` produced by CMake.

For ESP-IDF, Pico SDK, Zephyr, nRF Connect SDK, Arduino cores, and other framework-led projects, preserve the framework's own layer model. Do not rewrite those ecosystems into a generic CMSIS/HAL shape.

## CMake Decisions

- Use `CMAKE_SYSTEM_NAME Generic` and `CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY` in the toolchain file.
- Set `CMAKE_EXPORT_COMPILE_COMMANDS` to `ON`.
- Keep CPU, FPU, float ABI, MCU define, linker script, memory origins/sizes, and OpenOCD target visible in generated files.
- Produce `.elf`, `.bin`, `.hex`, `.map`, and `arm-none-eabi-size` output after build.
- Keep target-neutral preset names by default: `firmware-debug`, `firmware-release`, and `firmware-analyze`. Allow a custom prefix for teams that want `nrf52-debug`, `rp2040-debug`, or a product-specific prefix.
- Enable clang-tidy only in the analyze preset or behind an option.
- Pass `--target=arm-none-eabi` into clangd and clang-tidy when using cross GCC flags, otherwise host LLVM tools may reject Cortex-M CPU options.
- Suppress default clang-tidy checks that are noisy for linker symbols and memory-mapped registers; keep project logic checks enabled.
- A minimal smoke firmware can use `-nostdlib` and avoid C library headers. When the project starts using libc, printf, HAL code that expects standard headers, or syscalls, add the matching newlib/runtime package and switch linker specs deliberately.

## Debug and Flash Decisions

- Use OpenOCD as the bridge between GDB and ST-Link/J-Link.
- Use Cortex-Debug in VS Code for interactive debug.
- Keep shell and PowerShell scripts for build, format, analyze, flash, and OpenOCD server startup when generating a cross-platform scaffold.
- Run flash/debug commands only when hardware is attached and the user expects hardware access.
- If flashing fails, check power, SWD wiring, OpenOCD target file, probe interface file, target voltage, reset strategy, flash origin, and SWD speed.

## CI Decisions

- Use Docker to pin GCC, CMake, Ninja, OpenOCD, clang-format, and clang-tidy versions.
- Trigger CI on firmware paths, workflow paths, and toolchain files.
- Run formatting and analyze checks before the artifact-producing debug build.
- Upload `.elf`, `.bin`, `.hex`, and `.map` artifacts.
- Add host-side unit tests later for portable modules; do not block initial MCU bring-up on a test harness unless requested.

## Existing Firmware Rules

- Do not mix app and firmware build systems without a clear boundary.
- Do not move vendor HAL/CMSIS/SDK trees unless all include paths, linker/startup references, docs, and CI are updated.
- Preserve chip-specific linker scripts and startup files unless the target MCU changes.
- Treat CubeMX-generated files as user/vendor-owned unless the repo already marks editable sections.
- Preserve the existing package pinning model unless there is a clear reason to change it. If you convert a zip-vendored package to a submodule, or a global SDK path to a local manifest, update clone/setup docs and CI in the same change.
