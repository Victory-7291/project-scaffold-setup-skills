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
