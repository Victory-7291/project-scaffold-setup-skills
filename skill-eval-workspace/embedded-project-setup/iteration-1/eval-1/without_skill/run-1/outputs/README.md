# NUCLEO-F446RE Motor Control Firmware

Bare-metal firmware scaffold for the STMicroelectronics NUCLEO-F446RE development board.

## Target hardware

* MCU: STM32F446RE
* Core: ARM Cortex-M4 with FPU (fpv4-sp-d16)
* Flash: 512 KiB
* RAM: 128 KiB
* Floating point ABI: hard
* Debug probe: ST-Link / OpenOCD target `stm32f4x`

## Project layout

```
app/            Application layer (main control logic, motor control state machine)
bsp/            Board support package (NUCLEO-F446RE pin mappings, LEDs, buttons)
drivers/        Peripheral driver layer (GPIO, timer, UART, etc.)
drivers/cmsis/  CMSIS-Core headers/device definitions (placeholder)
drivers/hal/    STM32 HAL implementation (placeholder)
startup/        Reset handler and vector table
linker/         Linker script for STM32F446RE
src/            Top-level main.c
build/          Build artifacts
```

## Build

```bash
make
```

This produces `build/firmware.elf`, `build/firmware.bin`, and `build/firmware.hex`.

## Flash with OpenOCD

```bash
make flash
```

Or manually:

```bash
openocd -f openocd.cfg -c "program build/firmware.elf verify reset exit"
```

## CMSIS / HAL placeholders

This scaffold intentionally does not bundle STMicroelectronics proprietary code.
To use the full CMSIS and HAL:

1. Copy `CMSIS/Core/Include` and the STM32F4xx CMSIS device files into `drivers/cmsis/`.
2. Copy the STM32F4xx HAL sources/headers into `drivers/hal/`.
3. Update the include path in `Makefile` (`INC_DIRS`) to point to those directories.
4. Remove or replace the stub headers (`cmsis_stub.h`, `hal_stub.h`) with real headers.
