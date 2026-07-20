#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/../build"
ELF="${BUILD_DIR}/cubemx_legacy_fw.elf"

if [[ ! -f "${ELF}" ]]; then
    echo "ERROR: ELF not found: ${ELF}"
    echo "Build the project first with: cmake -B build -G Ninja && cmake --build build"
    exit 1
fi

echo "Flashing ${ELF} via OpenOCD..."

openocd \
    -f interface/stlink.cfg \
    -f target/stm32f4x.cfg \
    -c "init" \
    -c "reset halt" \
    -c "flash write_image erase ${ELF}" \
    -c "reset run" \
    -c "shutdown"

echo "Flash complete."
