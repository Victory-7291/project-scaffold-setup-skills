# Smart Sensor Node - STM32G030C8T6

A minimal STM32G0 firmware project for a smart sensor node, configured for
macOS Apple Silicon with CMake, Ninja, ARM GCC, clang-format, clang-tidy,
OpenOCD, and Cortex-Debug in VS Code.

## Target hardware

- MCU: STM32G030C8T6
- Core: ARM Cortex-M0+
- Flash: 64 KiB
- RAM: 8 KiB

## Install dependencies (macOS / Apple Silicon)

```bash
brew install cmake ninja llvm arm-none-eabi-gcc openocd
```

Recommended VS Code extensions are listed in `.vscode/extensions.json`:

- C/C++ (`ms-vscode.cpptools`)
- CMake Tools (`ms-vscode.cmake-tools`)
- Cortex-Debug (`marus25.cortex-debug`)
- clang-format (`xaver.clang-format`)

## Build

```bash
cmake -B build -G Ninja -DCMAKE_TOOLCHAIN_FILE=cmake/toolchain-arm-none-eabi.cmake
cmake --build build
```

## Flash and debug

Start OpenOCD in a terminal:

```bash
openocd -f openocd.cfg
```

In VS Code, run the **Cortex Debug (STM32G030)** launch configuration.
