#!/usr/bin/env bash
set -euo pipefail

echo "Starting OpenOCD GDB server for STM32F4..."

openocd \
    -f interface/stlink.cfg \
    -f target/stm32f4x.cfg \
    -c "init" \
    -c "halt"
