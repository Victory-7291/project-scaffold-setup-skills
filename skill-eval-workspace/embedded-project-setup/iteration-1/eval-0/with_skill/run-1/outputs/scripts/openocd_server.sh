#!/usr/bin/env bash
set -euo pipefail

openocd               -f "interface/stlink.cfg"               -f "target/stm32g0x.cfg"
