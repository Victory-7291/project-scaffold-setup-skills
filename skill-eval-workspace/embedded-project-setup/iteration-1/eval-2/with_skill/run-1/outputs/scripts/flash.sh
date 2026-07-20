#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PRESET="${PRESET:-stm32-debug}"
ELF="${ROOT_DIR}/build/${PRESET}/firmware.elf"

"${ROOT_DIR}/scripts/build.sh"

openocd               -f "interface/stlink.cfg"               -f "target/stm32f4x.cfg"               -c "program \"${ELF}\" verify reset exit"
