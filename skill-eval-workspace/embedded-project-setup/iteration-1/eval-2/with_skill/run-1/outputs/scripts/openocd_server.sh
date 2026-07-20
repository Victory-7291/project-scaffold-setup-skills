#!/usr/bin/env bash
set -euo pipefail

openocd               -f "interface/stlink.cfg"               -f "target/stm32f4x.cfg"
