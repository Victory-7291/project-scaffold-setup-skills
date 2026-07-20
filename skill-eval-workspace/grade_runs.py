#!/usr/bin/env python3
"""Grade scaffold skill evals programmatically."""

import json
import re
from pathlib import Path

WORKSPACE = Path("/Users/wan/Documents/project-scaffold-setup-skills/skill-eval-workspace")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def check_file_exists(outputs: Path, rel: str) -> tuple[bool, str]:
    path = outputs / rel
    exists = path.exists()
    return exists, f"{'Found' if exists else 'Missing'} {rel}"


def check_contains(outputs: Path, rel: str, *patterns: str) -> tuple[bool, str]:
    content = read_text(outputs / rel)
    if not content:
        return False, f"{rel} not found or empty"
    missing = [p for p in patterns if p not in content]
    if missing:
        return False, f"{rel} missing: {missing}"
    return True, f"{rel} contains all required patterns"


def check_regex(outputs: Path, rel: str, *regexes: str) -> tuple[bool, str]:
    content = read_text(outputs / rel)
    if not content:
        return False, f"{rel} not found or empty"
    missing = [r for r in regexes if not re.search(r, content, re.IGNORECASE)]
    if missing:
        return False, f"{rel} missing regex matches: {missing}"
    return True, f"{rel} matches all required regexes"


# Assertion checkers keyed by (skill, eval_name, assertion_text)
CHECKERS = {
    ("cpp-project-setup", "greenfield-macos-arm64-image-tool"): [
        lambda o: check_contains(o, "CMakeLists.txt", "CMAKE_CXX_STANDARD 20", "CMAKE_EXPORT_COMPILE_COMMANDS"),
        lambda o: check_contains(o, "vcpkg.json", "gtest"),
        lambda o: check_contains(o, "CMakePresets.json", "macos-arm64-debug", "macos-arm64-tidy"),
        lambda o: check_contains(o, "src/CMakeLists.txt", "image_tool_lib", "image_tool_app"),
        lambda o: check_contains(o, "tests/test_core.cpp", "TEST", "image_tool::"),
        lambda o: check_contains(o, ".vscode/launch.json", "lldb", "image_tool_app"),
        lambda o: check_contains(o, "README.md", "macOS Apple Silicon", "macos-arm64"),
    ],
    ("cpp-project-setup", "modernize-legacy-makefile"): [
        lambda o: (not (o / "Makefile").exists() or check_contains(o, "src/main.cpp", "Hello, legacy C++ project")[0], "legacy behavior checked"),
        lambda o: check_contains(o, "CMakeLists.txt", "add_library", "add_executable"),
        lambda o: check_file_exists(o, "vcpkg.json") and check_file_exists(o, "CMakePresets.json"),
        lambda o: check_file_exists(o, "tests/test_core.cpp") or check_file_exists(o, "tests/test_greeter.cpp"),
        lambda o: check_file_exists(o, ".clang-format") and check_file_exists(o, ".clang-tidy") and check_file_exists(o, ".vscode/settings.json"),
        lambda o: check_contains(o, "README.md", "build", "test"),
    ],
    ("cpp-project-setup", "greenfield-windows-x64-math-utils"): [
        lambda o: check_contains(o, "CMakeLists.txt", "CMAKE_CXX_STANDARD 20", "math_utils_lib"),
        lambda o: check_contains(o, "CMakePresets.json", "windows-x64-debug", "windows-x64-release", "windows-x64-tidy"),
        lambda o: check_contains(o, ".vscode/launch.json", "cppvsdbg"),
        lambda o: check_file_exists(o, "scripts/bootstrap_vcpkg.ps1") and check_file_exists(o, "scripts/format.ps1"),
        lambda o: check_contains(o, "tests/test_core.cpp", "TEST"),
        lambda o: check_contains(o, "README.md", "PowerShell", "bootstrap_vcpkg.ps1"),
    ],
    ("embedded-project-setup", "greenfield-stm32g0-smart-sensor"): [
        lambda o: check_contains(o, "CMakeLists.txt", "arm-none-eabi", "ELF"),
        lambda o: check_contains(o, "cmake/arm-none-eabi-gcc.cmake", "CMAKE_SYSTEM_NAME Generic", "arm-none-eabi-gcc"),
        lambda o: check_contains(o, "CMakePresets.json", "stm32-debug", "stm32-release", "stm32-analyze"),
        lambda o: check_contains(o, "startup/startup.c", "g_pfnVectors", "Reset_Handler"),
        lambda o: check_regex(o, "ldscripts/smart_sensor_flash.ld", r"FLASH\s*\(rx\)\s*:\s*ORIGIN\s*=\s*0x08000000,\s*LENGTH\s*=\s*64K", r"RAM\s*\(xrw\)\s*:\s*ORIGIN\s*=\s*0x20000000,\s*LENGTH\s*=\s*8K"),
        lambda o: check_contains(o, ".vscode/launch.json", "cortex-debug", "openocd"),
        lambda o: check_contains(o, "scripts/flash.sh", "stlink", "stm32g0x"),
        lambda o: check_contains(o, "README.md", "macOS Apple Silicon", "build"),
    ],
    ("embedded-project-setup", "custom-stm32f446re-motor-ctrl"): [
        lambda o: check_contains(o, "CMakeLists.txt", "-mcpu=cortex-m4", "fpv4-sp-d16", "-mfloat-abi=hard"),
        lambda o: check_contains(o, "CMakePresets.json", "stm32-debug", "stm32-release", "stm32-analyze"),
        lambda o: check_regex(o, "ldscripts/motor_ctrl_flash.ld", r"LENGTH\s*=\s*512K", r"LENGTH\s*=\s*128K"),
        lambda o: check_contains(o, ".vscode/launch.json", "stlink", "stm32f4x"),
        lambda o: check_file_exists(o, "src/app/app.c") and check_file_exists(o, "src/bsp/board.c") and check_file_exists(o, "src/drivers/motor.c"),
        lambda o: check_contains(o, "README.md", "STM32F446RE", "CMSIS", "HAL"),
    ],
    ("embedded-project-setup", "modernize-cubemx-keil"): [
        lambda o: check_file_exists(o, "Src/main.c") and check_file_exists(o, "Inc/main.h"),
        lambda o: check_contains(o, "CMakeLists.txt", "arm-none-eabi"),
        lambda o: check_file_exists(o, "cmake/arm-none-eabi-gcc.cmake"),
        lambda o: check_contains(o, "CMakePresets.json", "stm32-debug", "stm32-release", "stm32-analyze"),
        lambda o: check_file_exists(o, ".clang-format") and check_file_exists(o, ".clang-tidy") and check_file_exists(o, ".clangd"),
        lambda o: check_contains(o, ".vscode/launch.json", "cortex-debug", "openocd"),
        lambda o: check_file_exists(o, "scripts/flash.sh") and check_file_exists(o, "scripts/openocd_server.sh"),
        lambda o: check_contains(o, "README.md", "build", "flash"),
    ],
}


def grade_run(skill: str, eval_name: str, outputs: Path, assertions: list[str]) -> dict:
    checkers = CHECKERS.get((skill, eval_name), [])
    expectations = []
    passed = 0
    for assertion, checker in zip(assertions, checkers):
        try:
            result = checker(outputs)
            if isinstance(result, tuple):
                ok, evidence = result
            else:
                ok = bool(result)
                evidence = str(result)
        except Exception as e:
            ok = False
            evidence = f"Checker failed: {e}"
        if ok:
            passed += 1
        expectations.append({"text": assertion, "passed": ok, "evidence": evidence})

    total = len(expectations)
    return {
        "expectations": expectations,
        "summary": {"passed": passed, "failed": total - passed, "total": total, "pass_rate": passed / total if total else 0.0},
    }


def main():
    for skill_dir in WORKSPACE.iterdir():
        if not skill_dir.is_dir():
            continue
        skill = skill_dir.name
        iteration_dir = skill_dir / "iteration-1"
        if not iteration_dir.exists():
            continue
        for eval_dir in iteration_dir.iterdir():
            if not eval_dir.is_dir():
                continue
            metadata_path = eval_dir / "eval_metadata.json"
            if not metadata_path.exists():
                continue
            metadata = json.loads(metadata_path.read_text())
            assertions = metadata.get("assertions", [])
            for config in ("with_skill", "without_skill"):
                config_dir = eval_dir / config
                if not config_dir.exists():
                    continue
                run_dir = config_dir / "run-1"
                run_dir.mkdir(exist_ok=True)
                outputs_dir = config_dir / "outputs"
                timing_file = config_dir / "timing.json"
                metrics_file = outputs_dir / "metrics.json"
                if outputs_dir.exists():
                    (run_dir / "outputs").mkdir(exist_ok=True)
                    for item in outputs_dir.iterdir():
                        dest = run_dir / "outputs" / item.name
                        if dest.exists():
                            if dest.is_dir():
                                import shutil
                                shutil.rmtree(dest)
                            else:
                                dest.unlink()
                        item.rename(dest)
                    if outputs_dir.exists() and not any(outputs_dir.iterdir()):
                        outputs_dir.rmdir()
                if timing_file.exists():
                    timing_file.rename(run_dir / "timing.json")
                if metrics_file.exists() and (run_dir / "outputs" / "metrics.json").exists():
                    pass
                grading = grade_run(skill, eval_dir.name, run_dir / "outputs", assertions)
                # Load metrics/timing if available
                metrics = {}
                if (run_dir / "outputs" / "metrics.json").exists():
                    metrics = json.loads((run_dir / "outputs" / "metrics.json").read_text())
                timing = {}
                if (run_dir / "timing.json").exists():
                    timing = json.loads((run_dir / "timing.json").read_text())
                grading["execution_metrics"] = metrics
                grading["timing"] = timing
                (run_dir / "grading.json").write_text(json.dumps(grading, indent=2))
                print(f"Graded {skill}/{eval_dir.name}/{config}: {grading['summary']['passed']}/{grading['summary']['total']}")


if __name__ == "__main__":
    main()
