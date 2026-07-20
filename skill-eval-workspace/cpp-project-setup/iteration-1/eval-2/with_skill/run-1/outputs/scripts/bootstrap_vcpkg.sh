#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VCPKG_DIR="${ROOT_DIR}/.vcpkg"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required to bootstrap vcpkg" >&2
  exit 1
fi

if [ ! -d "${VCPKG_DIR}/.git" ]; then
  git clone https://github.com/microsoft/vcpkg "${VCPKG_DIR}"
fi

"${VCPKG_DIR}/bootstrap-vcpkg.sh" -disableMetrics
