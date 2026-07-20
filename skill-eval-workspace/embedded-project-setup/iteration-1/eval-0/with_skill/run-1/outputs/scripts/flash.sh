#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PRESET="${PRESET:-stm32-debug}"
ELF="${ROOT_DIR}/build/${PRESET}/smart_sensor.elf"

"${ROOT_DIR}/scripts/build.sh"

openocd               -f "interface/stlink.cfg"               -f "target/stm32g0x.cfg"               -c "program \"${ELF}\" verify reset exit"
