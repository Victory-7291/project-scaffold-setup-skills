# Firmware Package / SDK Matrix

Use this matrix before generating build files, linker/startup glue, include paths, or source lists. The shared editor/build workflow can be consistent, but the silicon support package is target-specific.

## Decision Rules

- Select the firmware package or SDK before writing `CMakeLists.txt`, `CMakePresets.json`, VS Code tasks, flash scripts, or CI.
- Record package name, upstream URL or package manager, local path, and pinned version/tag/manifest revision in the README or dependency manifest.
- CMSIS is a Cortex-M/SecurCore convention. Use CMSIS Core and CMSIS Device for Arm Cortex-M targets when vendor headers are available; do not require CMSIS for AVR, ESP32, or other non-Arm targets.
- Prefer the dependency model that the ecosystem expects. `vendor/` is a good fit for STM32Cube packages and Pico SDK submodules, but ESP-IDF, Zephyr, and nRF Connect SDK often work better as external or `west`-managed workspaces.
- If network access is unavailable or approval is needed, do not fake vendor files. Leave exact commands and TODOs, then wire build files only to paths that actually exist.
- Do not compile entire vendor example trees. Pull in the minimum CMSIS, HAL/LL, SDK, BSP, middleware, startup, linker, Kconfig, devicetree, or component files required by the chosen app.

## Target Matrix

| Target/platform | Primary firmware package or SDK | Preferred dependency model | What it supplies | Integration notes |
| --- | --- | --- | --- | --- |
| STM32 | `STM32Cube<series>`, for example `STMicroelectronics/STM32CubeG0` for STM32G0 | `vendor/STM32Cube<series>` as a git submodule or recursive clone pinned to an ST tag | CMSIS Core/Device, STM32 HAL/LL, BSP, middleware, board examples, startup/linker examples | Add include paths from `Drivers/CMSIS/Include`, `Drivers/CMSIS/Device/ST/STM32<series>xx/Include`, and selected HAL/LL `Inc` folders. Compile only selected `Drivers/STM32<series>xx_HAL_Driver/Src/*.c` files. Provide a project-owned `stm32<series>xx_hal_conf.h`. Use vendor startup/linker files or a reviewed project-owned linker/startup pair. |
| ESP32 / ESP32-C / ESP32-S | Espressif `esp-idf` | External SDK path via `IDF_PATH`, or an `external/esp-idf`/submodule path pinned to a release; use `idf.py` | SoC support, HAL/LL-style components, drivers, FreeRTOS integration, bootloader, partition table tooling, CMake functions, flash/monitor tools | Do not generate a generic `arm-none-eabi` CMake toolchain. Use `idf.py create-project`, `idf.py set-target <chip>`, `idf.py build`, `idf.py flash`, and ESP-IDF component structure. |
| AVR bare-metal | AVR GNU Toolchain plus AVR-LibC; Microchip Device Family Packs (`*.atpack`) when the selected MCU is not fully supported by installed GCC/AVR-LibC | Normally installed toolchain/runtime, not vendored. Optionally pin `.atpack` files under `vendor/microchip-packs/` for unsupported/new devices or reproducible builds | `avr-gcc`, binutils, standard C subset, device headers, startup code, device libraries, device specs; `.atpack` fills gaps for newer devices | Use `avr-gcc -mmcu=<device>` as the source of truth. CMSIS is not applicable. Generate `.elf`, `.hex`, optional `.eep`, and flash through `avrdude` or an existing Microchip/Arduino flow. |
| AVR Arduino-style | Arduino AVR Boards / `arduino:avr` core (`arduino/ArduinoCore-avr`) | Install with Arduino CLI or document the Arduino package cache; only vendor the core when the repo intentionally owns the platform | Arduino core, variants, board definitions, bootloaders, upload recipes | Use `arduino-cli compile --fqbn ...` or mirror the platform recipes if the user explicitly wants CMake. Keep board/core version pinned in docs. |
| RP2040 / RP2350 | Raspberry Pi `pico-sdk` | `vendor/pico-sdk` submodule or external SDK path via `PICO_SDK_PATH`; run SDK submodule update | RP-series headers, register definitions, startup/linker/boot glue, CMake functions, standard libraries, hardware libraries, `elf2uf2`/extra outputs | Include `pico_sdk_import.cmake` or `pico-sdk/pico_sdk_init.cmake` before `project()`, call `pico_sdk_init()`, link `pico_stdlib` or specific SDK libraries, and call `pico_add_extra_outputs()`. For RP2350 RISC-V, use the Pico-supported RISC-V toolchain path/platform rather than Arm GCC. |
| Nordic nRF greenfield | nRF Connect SDK (`nrfconnect/sdk-nrf`) | `west` workspace initialized from the SDK manifest and pinned with `--mr <tag>`; app may be inside the workspace or a manifest-driven app repo | Nordic SDK subsystems, samples, apps, `west.yml` manifest, Zephyr, nrfx/nrfxlib, Nordic HAL modules, bootloaders and security components depending on config | Prefer NCS for new nRF52/nRF53/nRF54/nRF91 work. Use `west build -b <board>`, Kconfig, devicetree overlays, sysbuild, `west flash`, and Nordic/J-Link tooling. |
| Nordic nRF direct bare-metal | `nrfx` plus CMSIS Core/Device support, or legacy nRF5 SDK only for existing/explicit legacy projects | `vendor/nrfx` plus a pinned CMSIS package/module, or preserve an existing nRF5 SDK dependency | Low-level nRF peripheral drivers/HAL and Cortex-M headers; legacy nRF5 SDK may include SoftDevice-era examples and drivers | Use this only when the user rejects Zephyr/NCS or is maintaining legacy firmware. Record why NCS is not being used. |
| Zephyr-supported boards | Zephyr RTOS (`zephyrproject-rtos/zephyr`) plus modules from its `west` manifest | `west` workspace or application manifest; pin Zephyr revision and project groups | RTOS kernel, arch/startup/linker integration, drivers, devicetree, Kconfig, board definitions, modules/HALs, build/flash/debug runners | Use `west init`, `west update`, `west zephyr-export`, `west build -b <board>`, `west flash`, and `west debug`. Do not replace Zephyr's toolchain/board model with a generic CMake toolchain file. |
| Standalone RTOS on vendor SDK | RTOS kernel such as FreeRTOS plus the vendor firmware package selected above | Vendor SDK under its normal model, RTOS kernel as submodule/package, app-owned integration layer | Scheduler/kernel plus vendor CMSIS/HAL/SDK/device support underneath | RTOS is not the device package. Choose STM32Cube, Pico SDK, nrfx/NCS, ESP-IDF, Microchip support, etc. first, then add RTOS portable layer, heap config, interrupt priority rules, and startup integration. |

## Common Commands

STM32Cube package under `vendor/`:

```bash
git submodule add https://github.com/STMicroelectronics/STM32CubeG0 vendor/STM32CubeG0
git -C vendor/STM32CubeG0 checkout vX.Y.Z
git -C vendor/STM32CubeG0 submodule update --init --recursive
```

ESP-IDF as an external SDK path:

```bash
git clone --recursive --branch vX.Y.Z https://github.com/espressif/esp-idf external/esp-idf
external/esp-idf/install.sh esp32
. external/esp-idf/export.sh
idf.py set-target esp32
idf.py build
```

Pico SDK as a submodule:

```bash
git submodule add https://github.com/raspberrypi/pico-sdk vendor/pico-sdk
git -C vendor/pico-sdk submodule update --init --recursive
cmake -S . -B build -DPICO_SDK_PATH=vendor/pico-sdk
cmake --build build
```

nRF Connect SDK workspace:

```bash
west init -m https://github.com/nrfconnect/sdk-nrf --mr vX.Y.Z ncs
cd ncs
west update
west zephyr-export
west build -b <board> <app>
```

Zephyr workspace:

```bash
west init -m https://github.com/zephyrproject-rtos/zephyr zephyrproject
cd zephyrproject
west update
west sdk install
west build -b <board> <app>
```

AVR bare-metal smoke check:

```bash
avr-gcc -mmcu=atmega328p -Os -Wall -Wextra -c src/main.c -o build/main.o
avr-gcc -mmcu=atmega328p build/main.o -Wl,-Map=build/firmware.map -o build/firmware.elf
avr-objcopy -O ihex -R .eeprom build/firmware.elf build/firmware.hex
```

## Package Selection Checklist

Before committing a generated or modernized firmware scaffold, verify:

- The README names the selected package/SDK, version, source URL, local path, and update command.
- `.gitmodules`, `west.yml`, `idf_component.yml`, Arduino CLI config, or package notes exist when the ecosystem needs them.
- CMake, `idf.py`, `west`, Arduino CLI, or Make source lists reference actual package files.
- Startup, linker, vector table, interrupt names, memory map, and system clock initialization come from the selected package or are explicitly project-owned.
- CI either fetches the same pinned package or uses a pinned container/toolchain image that already includes it.
- The project can build without a user's global IDE state unless the README clearly declares the required external SDK path.

## Official References

- STM32CubeG0: https://github.com/STMicroelectronics/STM32CubeG0
- ESP-IDF: https://github.com/espressif/esp-idf
- AVR-LibC: https://avrdudes.github.io/avr-libc/avr-libc-user-manual/
- GCC AVR options and device support notes: https://gcc.gnu.org/onlinedocs/gcc/AVR-Options.html
- Microchip Packs Repository: https://packs.download.microchip.com/
- Arduino AVR core: https://github.com/arduino/ArduinoCore-avr
- Raspberry Pi Pico SDK: https://github.com/raspberrypi/pico-sdk
- nRF Connect SDK: https://github.com/nrfconnect/sdk-nrf
- Zephyr west: https://docs.zephyrproject.org/latest/develop/west/index.html
- Zephyr getting started and SDK: https://docs.zephyrproject.org/latest/develop/getting_started/index.html
- CMSIS-Core: https://arm-software.github.io/CMSIS_6/latest/Core/index.html
