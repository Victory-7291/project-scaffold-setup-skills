#!/usr/bin/env bash
# Convenience helper to ensure OpenOCD is available before launching VS Code debug session.
set -euo pipefail

if ! command -v openocd &>/dev/null; then
    echo "ERROR: openocd is not installed or not on PATH."
    exit 1
fi

echo "OpenOCD is available. Launch Cortex-Debug from VS Code (Run and Debug -> 'Cortex-Debug ST-Link')."
