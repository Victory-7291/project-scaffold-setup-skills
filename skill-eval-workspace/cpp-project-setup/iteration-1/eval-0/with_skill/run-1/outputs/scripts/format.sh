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
done < <(find "${ROOT_DIR}/include" "${ROOT_DIR}/src" "${ROOT_DIR}/tests"               -type f \( -name '*.hpp' -o -name '*.h' -o -name '*.cpp' -o -name '*.cc' \) -print0)

if [ "${#FILES[@]}" -eq 0 ]; then
  exit 0
fi

if [ "${MODE}" = "--check" ] || [ "${MODE}" = "check" ]; then
  clang-format --dry-run --Werror "${FILES[@]}"
else
  clang-format -i "${FILES[@]}"
fi
