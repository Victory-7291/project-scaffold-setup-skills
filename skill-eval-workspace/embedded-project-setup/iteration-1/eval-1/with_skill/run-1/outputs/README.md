# MotorCtrl

Modern STM32/Cortex-M firmware scaffold for stm32f446re using VS Code, clangd,
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

The generated BSP is a minimal stm32f446re smoke example. Replace it with CMSIS,
HAL, LL, or board-specific drivers before product firmware work.

## Software Layers

```text
src/app/        Application logic (app.c / app.h)
src/bsp/        Board support package for the NUCLEO-F446RE (board.c / board.h)
src/drivers/    Peripheral drivers (motor.c / motor.h placeholder)
vendor/cmsis/   CMSIS-Core and CMSIS-Device headers for STM32F4xx (placeholder)
vendor/hal/     STM32F4xx HAL/LL sources (placeholder)
```

### CMSIS / HAL Placeholders

This scaffold does not vendor STM32Cube sources. Add them to the project before
product firmware work, for example:

```bash
mkdir -p vendor/cmsis vendor/hal
# Copy or submodule STM32CubeF4 CMSIS and HAL drivers here.
```

Then update `CMakeLists.txt` to include `vendor/cmsis/Include`,
`vendor/cmsis/Device/ST/STM32F4xx/Include`, and the desired HAL source files.

Once CMSIS/HAL files are available, replace the bare-metal register access in
`src/bsp/board.c` and the stubs in `src/drivers/motor.c` with the HAL/LL APIs or
register code appropriate for the motor-control application.
