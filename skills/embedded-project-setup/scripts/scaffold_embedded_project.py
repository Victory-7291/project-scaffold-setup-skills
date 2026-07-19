#!/usr/bin/env python3
"""Scaffold a modern STM32/Cortex-M embedded C project."""

from __future__ import annotations

import argparse
import re
import stat
import textwrap
from pathlib import Path


def safe_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()
    if not name:
        raise ValueError("project name must contain at least one letter or digit")
    if name[0].isdigit():
        name = f"firmware_{name}"
    return name


def cmake_project_name(value: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", value.strip())
    joined = "".join(part[:1].upper() + part[1:] for part in parts if part)
    return joined or "Firmware"


def render(template: str, **values: str) -> str:
    result = textwrap.dedent(template).lstrip("\n")
    for key, value in values.items():
        result = result.replace(f"@{key}@", value)
    return result


def write_file(root: Path, relative: str, content: str, *, executable: bool = False, force: bool = False) -> None:
    path = root / relative
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; rerun with --force to overwrite scaffold-owned files")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def cmake_list(items: list[str], indent: str = "  ") -> str:
    return "\n".join(f"{indent}{item}" for item in items)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a modern STM32 embedded C project scaffold.")
    parser.add_argument("--name", required=True, help="Firmware target name, for example smart_lock_fw")
    parser.add_argument("--out", help="Output directory. Defaults to ./<sanitized-name>.")
    parser.add_argument("--mcu", default="stm32g030c8t6", help="MCU name used in docs and VS Code")
    parser.add_argument("--device-define", default="STM32G030xx", help="Preprocessor define for vendor headers")
    parser.add_argument("--cpu", default="cortex-m0plus", help="GCC -mcpu value")
    parser.add_argument("--clang-target", default="arm-none-eabi", help="Target triple passed to clangd/clang-tidy")
    parser.add_argument("--fpu", default="", help="Optional GCC -mfpu value, for example fpv4-sp-d16")
    parser.add_argument("--float-abi", default="", help="Optional GCC -mfloat-abi value, for example hard")
    parser.add_argument("--flash-kb", type=int, default=64, help="Flash size for generated linker script")
    parser.add_argument("--ram-kb", type=int, default=8, help="RAM size for generated linker script")
    parser.add_argument("--openocd-interface", default="stlink", help="OpenOCD interface cfg stem")
    parser.add_argument("--openocd-target", default="stm32g0x", help="OpenOCD target cfg stem")
    parser.add_argument("--clangd-preset", default="stm32-debug", help="Preset whose build dir clangd should read")
    parser.add_argument("--force", action="store_true", help="Overwrite scaffold-owned files if they already exist")
    args = parser.parse_args()

    target = safe_name(args.name)
    cmake_name = cmake_project_name(args.name)
    root = Path(args.out) if args.out else Path.cwd() / target
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    cpu_flags = [f"-mcpu={args.cpu}", "-mthumb"]
    if args.fpu:
        cpu_flags.append(f"-mfpu={args.fpu}")
    if args.float_abi:
        cpu_flags.append(f"-mfloat-abi={args.float_abi}")

    values = {
        "TARGET": target,
        "CMAKE_PROJECT": cmake_name,
        "MCU": args.mcu,
        "MCU_UPPER": args.mcu.upper(),
        "DEVICE_DEFINE": args.device_define,
        "CPU": args.cpu,
        "CLANG_TARGET": args.clang_target,
        "CPU_FLAGS": cmake_list(cpu_flags, indent="  "),
        "FLASH_KB": str(args.flash_kb),
        "RAM_KB": str(args.ram_kb),
        "OPENOCD_INTERFACE": args.openocd_interface,
        "OPENOCD_TARGET": args.openocd_target,
        "CLANGD_PRESET": args.clangd_preset,
        "UPPER": target.upper(),
    }

    files = {
        "CMakeLists.txt": render(
            """
            cmake_minimum_required(VERSION 3.24)

            project(@CMAKE_PROJECT@ VERSION 0.1.0 LANGUAGES C)

            set(CMAKE_C_STANDARD 11)
            set(CMAKE_C_STANDARD_REQUIRED ON)
            set(CMAKE_C_EXTENSIONS OFF)
            set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
            set(CMAKE_EXECUTABLE_SUFFIX ".elf")

            set(FIRMWARE_TARGET @TARGET@)
            set(MCU_FLAGS
            @CPU_FLAGS@
            )

            option(@UPPER@_ENABLE_CLANG_TIDY "Enable clang-tidy during firmware builds" OFF)

            if(@UPPER@_ENABLE_CLANG_TIDY)
              find_program(CLANG_TIDY_EXE NAMES clang-tidy REQUIRED)
              set(CMAKE_C_CLANG_TIDY
                "${CLANG_TIDY_EXE}"
                "--extra-arg-before=--target=@CLANG_TARGET@"
              )
            endif()

            add_executable(${FIRMWARE_TARGET})

            target_sources(${FIRMWARE_TARGET}
              PRIVATE
                startup/startup.c
                src/main.c
                src/app/app.c
                src/bsp/board.c
            )

            target_include_directories(${FIRMWARE_TARGET}
              PRIVATE
                include
                src
            )

            target_compile_definitions(${FIRMWARE_TARGET}
              PRIVATE
                @DEVICE_DEFINE@
            )

            target_compile_options(${FIRMWARE_TARGET}
              PRIVATE
                ${MCU_FLAGS}
                -ffunction-sections
                -fdata-sections
                -Wall
                -Wextra
                -Wpedantic
                -Wconversion
                -Wshadow
                -g
            )

            target_link_options(${FIRMWARE_TARGET}
              PRIVATE
                ${MCU_FLAGS}
                -T${CMAKE_CURRENT_SOURCE_DIR}/ldscripts/@TARGET@_flash.ld
                -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/${FIRMWARE_TARGET}.map
                -Wl,--gc-sections
                -Wl,--print-memory-usage
                -nostdlib
            )

            add_custom_command(TARGET ${FIRMWARE_TARGET} POST_BUILD
              COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${FIRMWARE_TARGET}> ${CMAKE_CURRENT_BINARY_DIR}/${FIRMWARE_TARGET}.hex
              COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${FIRMWARE_TARGET}> ${CMAKE_CURRENT_BINARY_DIR}/${FIRMWARE_TARGET}.bin
              COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${FIRMWARE_TARGET}>
              COMMENT "Generating HEX/BIN and printing firmware size"
              VERBATIM
            )
            """,
            **values,
        ),
        "cmake/arm-none-eabi-gcc.cmake": render(
            """
            set(CMAKE_SYSTEM_NAME Generic)
            set(CMAKE_SYSTEM_PROCESSOR arm)
            set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

            find_program(ARM_NONE_EABI_GCC arm-none-eabi-gcc REQUIRED)
            find_program(ARM_NONE_EABI_OBJCOPY arm-none-eabi-objcopy REQUIRED)
            find_program(ARM_NONE_EABI_SIZE arm-none-eabi-size REQUIRED)
            find_program(ARM_NONE_EABI_GDB arm-none-eabi-gdb)

            set(CMAKE_C_COMPILER "${ARM_NONE_EABI_GCC}")
            set(CMAKE_OBJCOPY "${ARM_NONE_EABI_OBJCOPY}" CACHE FILEPATH "objcopy")
            set(CMAKE_SIZE "${ARM_NONE_EABI_SIZE}" CACHE FILEPATH "size")
            set(CMAKE_GDB "${ARM_NONE_EABI_GDB}" CACHE FILEPATH "gdb")
            """,
            **values,
        ),
        "CMakePresets.json": render(
            """
            {
              "version": 6,
              "cmakeMinimumRequired": {
                "major": 3,
                "minor": 24,
                "patch": 0
              },
              "configurePresets": [
                {
                  "name": "base",
                  "hidden": true,
                  "generator": "Ninja",
                  "binaryDir": "${sourceDir}/build/${presetName}",
                  "toolchainFile": "${sourceDir}/cmake/arm-none-eabi-gcc.cmake",
                  "cacheVariables": {
                    "CMAKE_EXPORT_COMPILE_COMMANDS": "ON"
                  }
                },
                {
                  "name": "stm32-debug",
                  "inherits": "base",
                  "displayName": "STM32 Debug",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Debug"
                  }
                },
                {
                  "name": "stm32-release",
                  "inherits": "base",
                  "displayName": "STM32 Release",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Release"
                  }
                },
                {
                  "name": "stm32-analyze",
                  "inherits": "stm32-debug",
                  "displayName": "STM32 clang-tidy",
                  "cacheVariables": {
                    "@UPPER@_ENABLE_CLANG_TIDY": "ON"
                  }
                }
              ],
              "buildPresets": [
                { "name": "stm32-debug", "configurePreset": "stm32-debug" },
                { "name": "stm32-release", "configurePreset": "stm32-release" },
                { "name": "stm32-analyze", "configurePreset": "stm32-analyze" }
              ]
            }
            """,
            **values,
        ),
        "include/project_config.h": render(
            """
            #pragma once

            #define PROJECT_HEARTBEAT_DELAY_CYCLES (120000u)
            """,
            **values,
        ),
        "src/main.c": render(
            """
            #include "app/app.h"

            int main(void) {
              app_init();

              while (1) {
                app_tick();
              }
            }
            """,
            **values,
        ),
        "src/app/app.h": render(
            """
            #pragma once

            void app_init(void);
            void app_tick(void);
            """,
            **values,
        ),
        "src/app/app.c": render(
            """
            #include "app/app.h"

            #include "bsp/board.h"
            #include "project_config.h"

            static unsigned int led_on;

            void app_init(void) {
              board_init();
              led_on = 0u;
              board_led_set(led_on);
            }

            void app_tick(void) {
              led_on = (led_on == 0u) ? 1u : 0u;
              board_led_set(led_on);
              board_delay(PROJECT_HEARTBEAT_DELAY_CYCLES);
            }
            """,
            **values,
        ),
        "src/bsp/board.h": render(
            """
            #pragma once

            void board_init(void);
            void board_led_set(unsigned int enabled);
            void board_delay(unsigned int cycles);
            """,
            **values,
        ),
        "src/bsp/board.c": render(
            """
            #include "bsp/board.h"

            #define REG32(address) (*(volatile unsigned int *)(address))

            #define RCC_IOPENR REG32(0x40021034u)
            #define RCC_IOPENR_GPIOAEN (1u << 0u)

            #define GPIOA_BASE (0x50000000u)
            #define GPIOA_MODER REG32(GPIOA_BASE + 0x00u)
            #define GPIOA_BSRR REG32(GPIOA_BASE + 0x18u)

            #define LED_PIN (5u)
            #define MODER_BITS_PER_PIN (2u)
            #define GPIO_MODER_MASK (0x3u)
            #define GPIO_MODER_OUTPUT (0x1u)

            void board_init(void) {
              RCC_IOPENR |= RCC_IOPENR_GPIOAEN;

              const unsigned int shift = LED_PIN * MODER_BITS_PER_PIN;
              unsigned int moder = GPIOA_MODER;
              moder &= (unsigned int)~(GPIO_MODER_MASK << shift);
              moder |= (GPIO_MODER_OUTPUT << shift);
              GPIOA_MODER = moder;
            }

            void board_led_set(unsigned int enabled) {
              if (enabled) {
                GPIOA_BSRR = (1u << LED_PIN);
              } else {
                GPIOA_BSRR = (1u << (LED_PIN + 16u));
              }
            }

            void board_delay(unsigned int cycles) {
              volatile unsigned int remaining = cycles;
              while (remaining > 0u) {
                __asm volatile("nop");
                --remaining;
              }
            }
            """,
            **values,
        ),
        "startup/startup.c": render(
            """
            typedef unsigned int uint32_t;
            typedef unsigned long uintptr_t;

            extern uint32_t _estack;
            extern uint32_t _sidata;
            extern uint32_t _sdata;
            extern uint32_t _edata;
            extern uint32_t _sbss;
            extern uint32_t _ebss;

            extern int main(void);

            void Reset_Handler(void);
            void Default_Handler(void);
            void SystemInit(void);

            void NMI_Handler(void) __attribute__((weak, alias("Default_Handler")));
            void HardFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
            void SVC_Handler(void) __attribute__((weak, alias("Default_Handler")));
            void PendSV_Handler(void) __attribute__((weak, alias("Default_Handler")));
            void SysTick_Handler(void) __attribute__((weak, alias("Default_Handler")));

            void SystemInit(void) {}

            __attribute__((section(".isr_vector"), used)) const uintptr_t g_pfnVectors[] = {
                (uintptr_t)&_estack,
                (uintptr_t)Reset_Handler,
                (uintptr_t)NMI_Handler,
                (uintptr_t)HardFault_Handler,
                0u,
                0u,
                0u,
                0u,
                0u,
                0u,
                0u,
                (uintptr_t)SVC_Handler,
                0u,
                0u,
                (uintptr_t)PendSV_Handler,
                (uintptr_t)SysTick_Handler,
            };

            void Reset_Handler(void) {
              uint32_t *src = &_sidata;
              for (uint32_t *dst = &_sdata; dst < &_edata; ++dst) {
                *dst = *src;
                ++src;
              }

              for (uint32_t *dst = &_sbss; dst < &_ebss; ++dst) {
                *dst = 0u;
              }

              SystemInit();
              (void)main();

              while (1) {
              }
            }

            void Default_Handler(void) {
              while (1) {
              }
            }
            """,
            **values,
        ),
        "ldscripts/@TARGET@_flash.ld": render(
            """
            ENTRY(Reset_Handler)

            MEMORY
            {
              FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = @FLASH_KB@K
              RAM   (xrw) : ORIGIN = 0x20000000, LENGTH = @RAM_KB@K
            }

            _estack = ORIGIN(RAM) + LENGTH(RAM);

            SECTIONS
            {
              .isr_vector :
              {
                KEEP(*(.isr_vector))
              } > FLASH

              .text :
              {
                *(.text*)
                *(.rodata*)
                KEEP(*(.init))
                KEEP(*(.fini))
                . = ALIGN(4);
                _etext = .;
              } > FLASH

              .ARM.exidx :
              {
                *(.ARM.exidx*)
              } > FLASH

              _sidata = LOADADDR(.data);

              .data : AT(_etext)
              {
                . = ALIGN(4);
                _sdata = .;
                *(.data*)
                . = ALIGN(4);
                _edata = .;
              } > RAM

              .bss :
              {
                . = ALIGN(4);
                _sbss = .;
                *(.bss*)
                *(COMMON)
                . = ALIGN(4);
                _ebss = .;
              } > RAM

              . = ALIGN(4);
              end = .;

              /DISCARD/ :
              {
                *(.note.GNU-stack)
                *(.comment)
              }
            }
            """,
            **values,
        ),
        ".vscode/extensions.json": render(
            """
            {
              "recommendations": [
                "llvm-vs-code-extensions.vscode-clangd",
                "ms-vscode.cmake-tools",
                "marus25.cortex-debug"
              ]
            }
            """,
            **values,
        ),
        ".vscode/settings.json": render(
            """
            {
              "cmake.useCMakePresets": "always",
              "cmake.configureOnOpen": true,
              "C_Cpp.intelliSenseEngine": "disabled",
              "clangd.arguments": [
                "--background-index",
                "--clang-tidy",
                "--query-driver=**/arm-none-eabi-*",
                "--compile-commands-dir=${workspaceFolder}/build/@CLANGD_PRESET@"
              ]
            }
            """,
            **values,
        ),
        ".vscode/launch.json": render(
            """
            {
              "version": "0.2.0",
              "configurations": [
                {
                  "name": "Debug @TARGET@",
                  "type": "cortex-debug",
                  "request": "launch",
                  "servertype": "openocd",
                  "cwd": "${workspaceFolder}",
                  "executable": "${workspaceFolder}/build/stm32-debug/@TARGET@.elf",
                  "device": "@MCU_UPPER@",
                  "runToEntryPoint": "main",
                  "configFiles": [
                    "interface/@OPENOCD_INTERFACE@.cfg",
                    "target/@OPENOCD_TARGET@.cfg"
                  ]
                }
              ]
            }
            """,
            **values,
        ),
        ".clangd": render(
            """
            CompileFlags:
              CompilationDatabase: build/@CLANGD_PRESET@
              Add:
                - --target=@CLANG_TARGET@
            Diagnostics:
              ClangTidy: true
            """,
            **values,
        ),
        ".clang-format": render(
            """
            BasedOnStyle: LLVM
            IndentWidth: 2
            ColumnLimit: 100
            DerivePointerAlignment: false
            PointerAlignment: Right
            """,
            **values,
        ),
        ".clang-tidy": render(
            """
            Checks: >
              -*,
              bugprone-*,
              clang-analyzer-*,
              performance-*,
              readability-*,
              -bugprone-reserved-identifier,
              -clang-analyzer-core.FixedAddressDereference,
              -clang-analyzer-security.ArrayBound,
              -performance-no-int-to-ptr,
              -readability-magic-numbers,
              -readability-isolate-declaration,
              -readability-redundant-casting,
              -readability-uppercase-literal-suffix
            WarningsAsErrors: ''
            HeaderFilterRegex: '.*'
            FormatStyle: file
            """,
            **values,
        ),
        "scripts/format.sh": render(
            """
            #!/usr/bin/env bash
            set -euo pipefail

            ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
            MODE="${1:-fix}"

            if ! command -v clang-format >/dev/null 2>&1; then
              echo "clang-format is required" >&2
              exit 1
            fi

            FILES=()
            while IFS= read -r -d '' file; do
              FILES+=("${file}")
            done < <(find "${ROOT_DIR}/include" "${ROOT_DIR}/src" "${ROOT_DIR}/startup" \
              -type f \\( -name '*.h' -o -name '*.c' \\) -print0)

            if [ "${#FILES[@]}" -eq 0 ]; then
              exit 0
            fi

            if [ "${MODE}" = "--check" ] || [ "${MODE}" = "check" ]; then
              clang-format --dry-run --Werror "${FILES[@]}"
            else
              clang-format -i "${FILES[@]}"
            fi
            """,
            **values,
        ),
        "scripts/build.sh": render(
            """
            #!/usr/bin/env bash
            set -euo pipefail

            ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
            PRESET="${PRESET:-stm32-debug}"

            cd "${ROOT_DIR}"
            cmake --preset "${PRESET}"

            build_cmd=(cmake --build --preset "${PRESET}")
            if [ -n "${JOBS:-}" ]; then
              build_cmd+=(--parallel "${JOBS}")
            fi
            "${build_cmd[@]}"
            """,
            **values,
        ),
        "scripts/analyze.sh": render(
            """
            #!/usr/bin/env bash
            set -euo pipefail

            ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
            PRESET=stm32-analyze "${ROOT_DIR}/scripts/build.sh"
            """,
            **values,
        ),
        "scripts/flash.sh": render(
            """
            #!/usr/bin/env bash
            set -euo pipefail

            ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
            PRESET="${PRESET:-stm32-debug}"
            ELF="${ROOT_DIR}/build/${PRESET}/@TARGET@.elf"

            "${ROOT_DIR}/scripts/build.sh"

            openocd \
              -f "interface/@OPENOCD_INTERFACE@.cfg" \
              -f "target/@OPENOCD_TARGET@.cfg" \
              -c "program \\"${ELF}\\" verify reset exit"
            """,
            **values,
        ),
        "scripts/openocd_server.sh": render(
            """
            #!/usr/bin/env bash
            set -euo pipefail

            openocd \
              -f "interface/@OPENOCD_INTERFACE@.cfg" \
              -f "target/@OPENOCD_TARGET@.cfg"
            """,
            **values,
        ),
        "Dockerfile": render(
            """
            FROM ubuntu:24.04

            RUN apt-get update && apt-get install -y --no-install-recommends \\
                ca-certificates \\
                cmake \\
                ninja-build \\
                gcc-arm-none-eabi \\
                binutils-arm-none-eabi \\
                gdb-multiarch \\
                openocd \\
                clang-format \\
                clang-tidy \\
                python3 \\
              && rm -rf /var/lib/apt/lists/*

            WORKDIR /work
            """,
            **values,
        ),
        ".github/workflows/firmware.yml": render(
            """
            name: firmware

            on:
              push:
                paths:
                  - "CMakeLists.txt"
                  - "CMakePresets.json"
                  - "cmake/**"
                  - "include/**"
                  - "src/**"
                  - "startup/**"
                  - "ldscripts/**"
                  - "scripts/**"
                  - "Dockerfile"
                  - ".github/workflows/firmware.yml"
              pull_request:
                paths:
                  - "CMakeLists.txt"
                  - "CMakePresets.json"
                  - "cmake/**"
                  - "include/**"
                  - "src/**"
                  - "startup/**"
                  - "ldscripts/**"
                  - "scripts/**"
                  - "Dockerfile"
                  - ".github/workflows/firmware.yml"

            jobs:
              build:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - name: Build toolchain image
                    run: docker build -t @TARGET@-toolchain .
                  - name: Check formatting
                    run: docker run --rm -v "${{ github.workspace }}:/work" -w /work @TARGET@-toolchain bash scripts/format.sh --check
                  - name: Analyze firmware
                    run: docker run --rm -v "${{ github.workspace }}:/work" -w /work @TARGET@-toolchain bash scripts/analyze.sh
                  - name: Build firmware
                    run: docker run --rm -v "${{ github.workspace }}:/work" -w /work @TARGET@-toolchain bash scripts/build.sh
                  - name: Upload firmware artifacts
                    uses: actions/upload-artifact@v4
                    with:
                      name: @TARGET@-firmware
                      path: |
                        build/stm32-debug/@TARGET@.elf
                        build/stm32-debug/@TARGET@.bin
                        build/stm32-debug/@TARGET@.hex
                        build/stm32-debug/@TARGET@.map
            """,
            **values,
        ),
        ".gitignore": render(
            """
            build/
            .cache/
            compile_commands.json
            .DS_Store
            """,
            **values,
        ),
        "README.md": render(
            """
            # @CMAKE_PROJECT@

            Modern STM32/Cortex-M firmware scaffold for @MCU@ using VS Code, clangd,
            CMake presets, Ninja, arm-none-eabi-gcc, OpenOCD, and Cortex-Debug.

            ## Toolchain

            macOS:

            ```bash
            brew install cmake ninja open-ocd arm-none-eabi-gcc arm-none-eabi-gdb llvm
            ```

            ## Build

            ```bash
            cmake --preset stm32-debug
            cmake --build --preset stm32-debug
            ```

            Or:

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

            The generated BSP is a minimal @MCU@ smoke example. Replace it with CMSIS,
            HAL, LL, or board-specific drivers before product firmware work.
            """,
            **values,
        ),
    }

    executable_files = {
        "scripts/build.sh",
        "scripts/format.sh",
        "scripts/analyze.sh",
        "scripts/flash.sh",
        "scripts/openocd_server.sh",
    }
    for relative, content in files.items():
        resolved_relative = relative.replace("@TARGET@", target)
        write_file(root, resolved_relative, content, executable=resolved_relative in executable_files, force=args.force)

    print(f"Created embedded firmware project at {root}")
    print("Next steps:")
    print("  cmake --preset stm32-debug")
    print("  cmake --build --preset stm32-debug")
    print("  bash scripts/flash.sh   # when hardware is attached")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
