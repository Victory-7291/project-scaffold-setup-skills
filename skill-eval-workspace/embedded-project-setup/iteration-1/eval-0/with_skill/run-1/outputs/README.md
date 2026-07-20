# SmartSensor

Modern STM32/Cortex-M firmware scaffold for stm32g030c8t6 using VS Code, clangd,
CMake presets, Ninja, arm-none-eabi-gcc, OpenOCD, and Cortex-Debug.

## Host Toolchain

Selected host profile: `macos-arm64`

macOS Apple Silicon:

```bash
brew install cmake ninja open-ocd arm-none-eabi-gcc arm-none-eabi-gdb llvm
```

If you are generating this project for another machine, rerun the scaffold with
`--host-platform macos-arm64`, `macos-x64`, `linux-x64`, `linux-arm64`,
`windows-x64`, or `windows-arm64`.

## Build

```bash
bash scripts/build.sh
```

## Analyze

```bash
bash scripts/analyze.sh
```

## Format

```bash
bash scripts/format.sh --check
```

## Flash and Debug

```bash
bash scripts/flash.sh
bash scripts/openocd_server.sh
```

The generated BSP is a minimal stm32g030c8t6 smoke example. Replace it with CMSIS,
HAL, LL, or board-specific drivers before product firmware work.
