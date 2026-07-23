#!/usr/bin/env python3
"""Scaffold a modern C++ CMake/vcpkg project."""

from __future__ import annotations

import argparse
import platform
import re
import stat
import textwrap
from pathlib import Path


HOST_PROFILES = {
    "macos-arm64": {
        "debug_preset": "macos-arm64-debug",
        "tidy_preset": "macos-arm64-tidy",
        "bootstrap": "bash scripts/bootstrap_vcpkg.sh",
        "format": "bash scripts/format.sh --check",
        "shell": "bash",
        "setup": """macOS Apple Silicon:

```bash
brew install cmake ninja llvm git doxygen
bash scripts/bootstrap_vcpkg.sh
```""",
    },
    "macos-x64": {
        "debug_preset": "macos-x64-debug",
        "tidy_preset": "macos-x64-tidy",
        "bootstrap": "bash scripts/bootstrap_vcpkg.sh",
        "format": "bash scripts/format.sh --check",
        "shell": "bash",
        "setup": """macOS Intel:

```bash
brew install cmake ninja llvm git doxygen
bash scripts/bootstrap_vcpkg.sh
```""",
    },
    "linux-x64": {
        "debug_preset": "linux-x64-debug",
        "tidy_preset": "linux-x64-tidy",
        "bootstrap": "bash scripts/bootstrap_vcpkg.sh",
        "format": "bash scripts/format.sh --check",
        "shell": "bash",
        "setup": """Ubuntu/Debian Linux x64:

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake ninja-build git clang clang-format clang-tidy lldb doxygen curl zip unzip tar pkg-config
bash scripts/bootstrap_vcpkg.sh
```""",
    },
    "linux-arm64": {
        "debug_preset": "linux-arm64-debug",
        "tidy_preset": "linux-arm64-tidy",
        "bootstrap": "bash scripts/bootstrap_vcpkg.sh",
        "format": "bash scripts/format.sh --check",
        "shell": "bash",
        "setup": """Ubuntu/Debian Linux arm64:

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake ninja-build git clang clang-format clang-tidy lldb doxygen curl zip unzip tar pkg-config
bash scripts/bootstrap_vcpkg.sh
```""",
    },
    "windows-x64": {
        "debug_preset": "windows-x64-debug",
        "tidy_preset": "windows-x64-tidy",
        "bootstrap": "pwsh scripts/bootstrap_vcpkg.ps1",
        "format": "pwsh scripts/format.ps1 -Check",
        "shell": "powershell",
        "setup": """Windows x64:

Install Visual Studio 2022 Build Tools with the Desktop development with C++ workload,
CMake, Ninja, Git, LLVM, and Doxygen. Then run from a Developer PowerShell:

```powershell
pwsh scripts/bootstrap_vcpkg.ps1
```""",
    },
    "windows-arm64": {
        "debug_preset": "windows-arm64-debug",
        "tidy_preset": "windows-arm64-tidy",
        "bootstrap": "pwsh scripts/bootstrap_vcpkg.ps1",
        "format": "pwsh scripts/format.ps1 -Check",
        "shell": "powershell",
        "setup": """Windows arm64:

Install Visual Studio 2022 Build Tools with ARM64 C++ tools, CMake, Ninja, Git,
LLVM, and Doxygen. Then run from a Developer PowerShell:

```powershell
pwsh scripts/bootstrap_vcpkg.ps1
```""",
    },
}

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def detect_host_platform() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    is_arm = machine in {"arm64", "aarch64"} or machine.startswith("armv")
    is_x64 = machine in {"x86_64", "amd64", "x64"}

    if system == "darwin":
        return "macos-arm64" if is_arm else "macos-x64"
    if system == "linux":
        return "linux-arm64" if is_arm else "linux-x64"
    if system == "windows":
        return "windows-arm64" if is_arm else "windows-x64"
    if is_x64:
        return "linux-x64"
    raise ValueError(f"unsupported host platform: system={platform.system()} machine={platform.machine()}")


def snake_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()
    if not name:
        raise ValueError("project name must contain at least one letter or digit")
    if name[0].isdigit():
        name = f"project_{name}"
    return name


def package_name(value: str) -> str:
    name = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return name or "cpp-project"


def cmake_project_name(value: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", value.strip())
    joined = "".join(part[:1].upper() + part[1:] for part in parts if part)
    return joined or "CppProject"


def render(template: str, **values: str) -> str:
    result = textwrap.dedent(template).lstrip("\n")
    for key, value in values.items():
        result = result.replace(f"@{key}@", value)
    return result


def render_asset(relative: str, **values: str) -> str:
    return render((ASSETS_DIR / relative).read_text(encoding="utf-8"), **values)


def write_file(root: Path, relative: str, content: str, *, executable: bool = False, force: bool = False) -> None:
    path = root / relative
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; rerun with --force to overwrite scaffold-owned files")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a modern C++ project scaffold.")
    parser.add_argument("--name", required=True, help="Project name, for example future_cv_tools")
    parser.add_argument("--out", help="Output directory. Defaults to ./<sanitized-name>.")
    parser.add_argument(
        "--host-platform",
        default="auto",
        choices=["auto", *HOST_PROFILES.keys()],
        help="Developer host profile used for default presets and README commands",
    )
    parser.add_argument("--cpp-standard", default="20", choices=["17", "20", "23"], help="C++ language standard")
    parser.add_argument("--clangd-preset", help="Preset whose build directory clangd should read")
    parser.add_argument("--force", action="store_true", help="Overwrite scaffold-owned files if they already exist")
    args = parser.parse_args()

    host_platform = detect_host_platform() if args.host_platform == "auto" else args.host_platform
    host_profile = HOST_PROFILES[host_platform]
    clangd_preset = args.clangd_preset or host_profile["debug_preset"]
    windows_debug_preset = "windows-arm64-debug" if host_platform == "windows-arm64" else "windows-x64-debug"

    target = snake_name(args.name)
    package = package_name(args.name)
    cmake_name = cmake_project_name(args.name)
    namespace = target
    upper = target.upper()
    root = Path(args.out) if args.out else Path.cwd() / target
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    values = {
        "TARGET": target,
        "PACKAGE": package,
        "CMAKE_PROJECT": cmake_name,
        "NAMESPACE": namespace,
        "UPPER": upper,
        "CPP_STANDARD": args.cpp_standard,
        "CLANGD_PRESET": clangd_preset,
        "HOST_PLATFORM": host_platform,
        "HOST_SETUP": host_profile["setup"].strip(),
        "HOST_DEBUG_PRESET": host_profile["debug_preset"],
        "HOST_TIDY_PRESET": host_profile["tidy_preset"],
        "HOST_BOOTSTRAP_COMMAND": host_profile["bootstrap"],
        "HOST_FORMAT_COMMAND": host_profile["format"],
        "HOST_SHELL": host_profile["shell"],
        "WINDOWS_DEBUG_PRESET": windows_debug_preset,
    }

    files = {
        "CMakeLists.txt": render(
            """
            cmake_minimum_required(VERSION 3.24)

            project(@CMAKE_PROJECT@ VERSION 0.1.0 LANGUAGES CXX)

            set(CMAKE_CXX_STANDARD @CPP_STANDARD@)
            set(CMAKE_CXX_STANDARD_REQUIRED ON)
            set(CMAKE_CXX_EXTENSIONS OFF)
            set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

            option(@UPPER@_ENABLE_CLANG_TIDY "Enable clang-tidy during the build" OFF)

            if(@UPPER@_ENABLE_CLANG_TIDY)
              find_program(CLANG_TIDY_EXE NAMES clang-tidy REQUIRED)
              set(CMAKE_CXX_CLANG_TIDY "${CLANG_TIDY_EXE}")
            endif()

            include(cmake/Warnings.cmake)

            add_subdirectory(src)

            include(CTest)
            if(BUILD_TESTING)
              add_subdirectory(tests)
            endif()

            find_package(Doxygen)
            if(DOXYGEN_FOUND)
              configure_file(docs/Doxyfile.in "${CMAKE_CURRENT_BINARY_DIR}/Doxyfile" @ONLY)
              add_custom_target(docs
                COMMAND "${DOXYGEN_EXECUTABLE}" "${CMAKE_CURRENT_BINARY_DIR}/Doxyfile"
                WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
                COMMENT "Generating API documentation with Doxygen"
                VERBATIM)
            endif()
            """,
            **values,
        ),
        "cmake/Warnings.cmake": render(
            """
            function(target_project_warnings target_name)
              if(MSVC)
                target_compile_options("${target_name}" PRIVATE /W4 /permissive-)
              else()
                target_compile_options("${target_name}" PRIVATE
                  -Wall
                  -Wextra
                  -Wpedantic
                  -Wconversion
                  -Wsign-conversion
                  -Wshadow
                )
              endif()
            endfunction()
            """,
            **values,
        ),
        "src/CMakeLists.txt": render(
            """
            add_library(@TARGET@_lib core.cpp)
            add_library(@TARGET@::lib ALIAS @TARGET@_lib)

            target_include_directories(@TARGET@_lib
              PUBLIC
                "${PROJECT_SOURCE_DIR}/include"
            )
            target_project_warnings(@TARGET@_lib)

            add_executable(@TARGET@_app main.cpp)
            target_link_libraries(@TARGET@_app PRIVATE @TARGET@::lib)
            target_project_warnings(@TARGET@_app)
            """,
            **values,
        ),
        f"include/{target}/core.hpp": render(
            """
            #pragma once

            #include <string>
            #include <string_view>

            namespace @NAMESPACE@ {

            [[nodiscard]] std::string greeting(std::string_view name);

            }  // namespace @NAMESPACE@
            """,
            **values,
        ),
        "src/core.cpp": render(
            """
            #include "@TARGET@/core.hpp"

            namespace @NAMESPACE@ {

            std::string greeting(std::string_view name) {
              if (name.empty()) {
                return "hello, modern C++";
              }
              return "hello, " + std::string{name};
            }

            }  // namespace @NAMESPACE@
            """,
            **values,
        ),
        "src/main.cpp": render(
            """
            #include <iostream>

            #include "@TARGET@/core.hpp"

            int main(int argc, char** argv) {
              const char* name = argc > 1 ? argv[1] : "";
              std::cout << @NAMESPACE@::greeting(name) << '\\n';
              return 0;
            }
            """,
            **values,
        ),
        "tests/CMakeLists.txt": render(
            """
            find_package(GTest CONFIG REQUIRED)
            include(GoogleTest)

            add_executable(@TARGET@_tests test_core.cpp)
            target_link_libraries(@TARGET@_tests PRIVATE @TARGET@::lib GTest::gtest_main)
            target_project_warnings(@TARGET@_tests)

            gtest_discover_tests(@TARGET@_tests)
            """,
            **values,
        ),
        "tests/test_core.cpp": render(
            """
            #include <gtest/gtest.h>

            #include "@TARGET@/core.hpp"

            TEST(CoreTest, GreetsNamedUser) {
              EXPECT_EQ(@NAMESPACE@::greeting("Codex"), "hello, Codex");
            }

            TEST(CoreTest, GreetsDefaultUser) {
              EXPECT_EQ(@NAMESPACE@::greeting(""), "hello, modern C++");
            }
            """,
            **values,
        ),
        "vcpkg.json": render(
            """
            {
              "name": "@PACKAGE@",
              "version-string": "0.1.0",
              "dependencies": [
                "gtest"
              ]
            }
            """,
            **values,
        ),
        "CMakePresets.json": render(
            """
            {
              "version": 6,
              "cmakeMinimumRequired": {
                "major": 3,
                "minor": 24,
                "patch": 0
              },
              "configurePresets": [
                {
                  "name": "base",
                  "hidden": true,
                  "generator": "Ninja",
                  "binaryDir": "${sourceDir}/build/${presetName}",
                  "cacheVariables": {
                    "CMAKE_EXPORT_COMPILE_COMMANDS": "ON",
                    "CMAKE_TOOLCHAIN_FILE": "${sourceDir}/.vcpkg/scripts/buildsystems/vcpkg.cmake"
                  }
                },
                {
                  "name": "macos-arm64-debug",
                  "inherits": "base",
                  "displayName": "macOS arm64 Debug",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Debug",
                    "VCPKG_TARGET_TRIPLET": "arm64-osx"
                  }
                },
                {
                  "name": "macos-arm64-release",
                  "inherits": "base",
                  "displayName": "macOS arm64 Release",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "VCPKG_TARGET_TRIPLET": "arm64-osx"
                  }
                },
                {
                  "name": "macos-arm64-tidy",
                  "inherits": "macos-arm64-debug",
                  "displayName": "macOS arm64 clang-tidy",
                  "cacheVariables": {
                    "@UPPER@_ENABLE_CLANG_TIDY": "ON"
                  }
                },
                {
                  "name": "macos-x64-debug",
                  "inherits": "base",
                  "displayName": "macOS x64 Debug",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Debug",
                    "VCPKG_TARGET_TRIPLET": "x64-osx"
                  }
                },
                {
                  "name": "macos-x64-release",
                  "inherits": "base",
                  "displayName": "macOS x64 Release",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "VCPKG_TARGET_TRIPLET": "x64-osx"
                  }
                },
                {
                  "name": "macos-x64-tidy",
                  "inherits": "macos-x64-debug",
                  "displayName": "macOS x64 clang-tidy",
                  "cacheVariables": {
                    "@UPPER@_ENABLE_CLANG_TIDY": "ON"
                  }
                },
                {
                  "name": "linux-x64-debug",
                  "inherits": "base",
                  "displayName": "Linux x64 Debug",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Debug",
                    "VCPKG_TARGET_TRIPLET": "x64-linux"
                  }
                },
                {
                  "name": "linux-x64-release",
                  "inherits": "base",
                  "displayName": "Linux x64 Release",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "VCPKG_TARGET_TRIPLET": "x64-linux"
                  }
                },
                {
                  "name": "linux-x64-tidy",
                  "inherits": "linux-x64-debug",
                  "displayName": "Linux x64 clang-tidy",
                  "cacheVariables": {
                    "@UPPER@_ENABLE_CLANG_TIDY": "ON"
                  }
                },
                {
                  "name": "linux-arm64-debug",
                  "inherits": "base",
                  "displayName": "Linux arm64 Debug",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Debug",
                    "VCPKG_TARGET_TRIPLET": "arm64-linux"
                  }
                },
                {
                  "name": "linux-arm64-release",
                  "inherits": "base",
                  "displayName": "Linux arm64 Release",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "VCPKG_TARGET_TRIPLET": "arm64-linux"
                  }
                },
                {
                  "name": "linux-arm64-tidy",
                  "inherits": "linux-arm64-debug",
                  "displayName": "Linux arm64 clang-tidy",
                  "cacheVariables": {
                    "@UPPER@_ENABLE_CLANG_TIDY": "ON"
                  }
                },
                {
                  "name": "windows-x64-debug",
                  "inherits": "base",
                  "displayName": "Windows x64 Debug",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Debug",
                    "VCPKG_TARGET_TRIPLET": "x64-windows"
                  }
                },
                {
                  "name": "windows-x64-release",
                  "inherits": "base",
                  "displayName": "Windows x64 Release",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "VCPKG_TARGET_TRIPLET": "x64-windows"
                  }
                },
                {
                  "name": "windows-x64-tidy",
                  "inherits": "windows-x64-debug",
                  "displayName": "Windows x64 clang-tidy",
                  "cacheVariables": {
                    "@UPPER@_ENABLE_CLANG_TIDY": "ON"
                  }
                },
                {
                  "name": "windows-arm64-debug",
                  "inherits": "base",
                  "displayName": "Windows arm64 Debug",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Debug",
                    "VCPKG_TARGET_TRIPLET": "arm64-windows"
                  }
                },
                {
                  "name": "windows-arm64-release",
                  "inherits": "base",
                  "displayName": "Windows arm64 Release",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "VCPKG_TARGET_TRIPLET": "arm64-windows"
                  }
                },
                {
                  "name": "windows-arm64-tidy",
                  "inherits": "windows-arm64-debug",
                  "displayName": "Windows arm64 clang-tidy",
                  "cacheVariables": {
                    "@UPPER@_ENABLE_CLANG_TIDY": "ON"
                  }
                }
              ],
              "buildPresets": [
                { "name": "macos-arm64-debug", "configurePreset": "macos-arm64-debug" },
                { "name": "macos-arm64-release", "configurePreset": "macos-arm64-release" },
                { "name": "macos-arm64-tidy", "configurePreset": "macos-arm64-tidy" },
                { "name": "macos-x64-debug", "configurePreset": "macos-x64-debug" },
                { "name": "macos-x64-release", "configurePreset": "macos-x64-release" },
                { "name": "macos-x64-tidy", "configurePreset": "macos-x64-tidy" },
                { "name": "linux-x64-debug", "configurePreset": "linux-x64-debug" },
                { "name": "linux-x64-release", "configurePreset": "linux-x64-release" },
                { "name": "linux-x64-tidy", "configurePreset": "linux-x64-tidy" },
                { "name": "linux-arm64-debug", "configurePreset": "linux-arm64-debug" },
                { "name": "linux-arm64-release", "configurePreset": "linux-arm64-release" },
                { "name": "linux-arm64-tidy", "configurePreset": "linux-arm64-tidy" },
                { "name": "windows-x64-debug", "configurePreset": "windows-x64-debug" },
                { "name": "windows-x64-release", "configurePreset": "windows-x64-release" },
                { "name": "windows-x64-tidy", "configurePreset": "windows-x64-tidy" },
                { "name": "windows-arm64-debug", "configurePreset": "windows-arm64-debug" },
                { "name": "windows-arm64-release", "configurePreset": "windows-arm64-release" },
                { "name": "windows-arm64-tidy", "configurePreset": "windows-arm64-tidy" }
              ],
              "testPresets": [
                {
                  "name": "macos-arm64-debug",
                  "configurePreset": "macos-arm64-debug",
                  "output": { "outputOnFailure": true }
                },
                {
                  "name": "macos-x64-debug",
                  "configurePreset": "macos-x64-debug",
                  "output": { "outputOnFailure": true }
                },
                {
                  "name": "linux-x64-debug",
                  "configurePreset": "linux-x64-debug",
                  "output": { "outputOnFailure": true }
                },
                {
                  "name": "linux-arm64-debug",
                  "configurePreset": "linux-arm64-debug",
                  "output": { "outputOnFailure": true }
                },
                {
                  "name": "windows-x64-debug",
                  "configurePreset": "windows-x64-debug",
                  "output": { "outputOnFailure": true }
                },
                {
                  "name": "windows-arm64-debug",
                  "configurePreset": "windows-arm64-debug",
                  "output": { "outputOnFailure": true }
                }
              ]
            }
            """,
            **values,
        ),
        ".vscode/extensions.json": render(
            """
            {
              "recommendations": [
                "ms-vscode.cmake-tools",
                "llvm-vs-code-extensions.vscode-clangd",
                "vadimcn.vscode-lldb",
                "ms-vscode.cpptools"
              ]
            }
            """,
            **values,
        ),
        ".vscode/settings.json": render(
            """
            {
              "cmake.useCMakePresets": "always",
              "cmake.configureOnOpen": true,
              "C_Cpp.intelliSenseEngine": "disabled",
              "clangd.arguments": [
                "--background-index",
                "--clang-tidy",
                "--compile-commands-dir=${workspaceFolder}/build/@CLANGD_PRESET@"
              ]
            }
            """,
            **values,
        ),
        ".vscode/launch.json": render(
            """
            {
              "version": "0.2.0",
              "configurations": [
                {
                  "name": "Debug @TARGET@_app (macOS/Linux)",
                  "type": "lldb",
                  "request": "launch",
                  "program": "${workspaceFolder}/build/@CLANGD_PRESET@/src/@TARGET@_app",
                  "args": [],
                  "cwd": "${workspaceFolder}"
                },
                {
                  "name": "Debug @TARGET@_app (Windows MSVC)",
                  "type": "cppvsdbg",
                  "request": "launch",
                  "program": "${workspaceFolder}/build/@WINDOWS_DEBUG_PRESET@/src/@TARGET@_app.exe",
                  "args": [],
                  "cwd": "${workspaceFolder}",
                  "console": "integratedTerminal"
                }
              ]
            }
            """,
            **values,
        ),
        ".clangd": render(
            """
            CompileFlags:
              CompilationDatabase: build/@CLANGD_PRESET@
            Diagnostics:
              ClangTidy: true
            """,
            **values,
        ),
        ".clang-format": render(
            """
            BasedOnStyle: Google
            Standard: c++@CPP_STANDARD@
            ColumnLimit: 100
            DerivePointerAlignment: false
            PointerAlignment: Left
            AllowShortBlocksOnASingleLine: Never
            AllowShortFunctionsOnASingleLine: Empty
            """,
            **values,
        ),
        ".clang-tidy": render(
            """
            Checks: >
              -*,
              bugprone-*,
              clang-analyzer-*,
              modernize-*,
              performance-*,
              readability-*,
              -modernize-use-trailing-return-type
            WarningsAsErrors: ''
            HeaderFilterRegex: '.*'
            FormatStyle: file
            """,
            **values,
        ),
        "docs/Doxyfile.in": render(
            """
            PROJECT_NAME           = "@CMAKE_PROJECT@"
            OUTPUT_DIRECTORY       = @CMAKE_CURRENT_BINARY_DIR@/docs
            INPUT                  = @CMAKE_SOURCE_DIR@/include @CMAKE_SOURCE_DIR@/src
            RECURSIVE              = YES
            EXTRACT_ALL            = YES
            GENERATE_HTML          = YES
            GENERATE_LATEX         = NO
            QUIET                  = YES
            WARN_IF_UNDOCUMENTED   = NO
            """,
            **values,
        ),
        "scripts/bootstrap_vcpkg.sh": render(
            """
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
            """,
            **values,
        ),
        "scripts/bootstrap_vcpkg.ps1": render(
            """
            $ErrorActionPreference = "Stop"

            $RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
            $VcpkgDir = Join-Path $RootDir ".vcpkg"

            if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
              throw "git is required to bootstrap vcpkg"
            }

            if (-not (Test-Path (Join-Path $VcpkgDir ".git"))) {
              git clone https://github.com/microsoft/vcpkg $VcpkgDir
            }

            & (Join-Path $VcpkgDir "bootstrap-vcpkg.bat") -disableMetrics
            """,
            **values,
        ),
        "scripts/format.sh": render(
            """
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
            done < <(find "${ROOT_DIR}/include" "${ROOT_DIR}/src" "${ROOT_DIR}/tests" \
              -type f \\( -name '*.hpp' -o -name '*.h' -o -name '*.cpp' -o -name '*.cc' \\) -print0)

            if [ "${#FILES[@]}" -eq 0 ]; then
              exit 0
            fi

            if [ "${MODE}" = "--check" ] || [ "${MODE}" = "check" ]; then
              clang-format --dry-run --Werror "${FILES[@]}"
            else
              clang-format -i "${FILES[@]}"
            fi
            """,
            **values,
        ),
        "scripts/format.ps1": render(
            """
            param(
              [switch]$Check
            )

            $ErrorActionPreference = "Stop"
            $RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
            $SearchRoots = @("include", "src", "tests")
            $Extensions = @(".hpp", ".h", ".cpp", ".cc")

            if (-not (Get-Command clang-format -ErrorAction SilentlyContinue)) {
              throw "clang-format is required"
            }

            $Files = @()
            foreach ($SearchRoot in $SearchRoots) {
              $Path = Join-Path $RootDir $SearchRoot
              if (Test-Path $Path) {
                $Files += Get-ChildItem $Path -Recurse -File | Where-Object { $Extensions -contains $_.Extension }
              }
            }

            if ($Files.Count -eq 0) {
              exit 0
            }

            $FilePaths = @($Files | ForEach-Object { $_.FullName })
            if ($Check) {
              clang-format --dry-run --Werror @FilePaths
            } else {
              clang-format -i @FilePaths
            }
            """,
            **values,
        ),
        ".gitignore": render(
            """
            build/
            .vcpkg/
            .cache/
            compile_commands.json
            .DS_Store
            """,
            **values,
        ),
        "README.md": render(
            """
            # @CMAKE_PROJECT@

            Modern C++ scaffold using CMake presets, Ninja, vcpkg manifest mode, GoogleTest,
            clang-format, clang-tidy, Doxygen, and VS Code.

            ## Host Toolchain

            Selected host profile: `@HOST_PLATFORM@`

            @HOST_SETUP@

            If you are generating this project for another machine, rerun the scaffold with
            `--host-platform macos-arm64`, `macos-x64`, `linux-x64`, `linux-arm64`,
            `windows-x64`, or `windows-arm64`.

            ## Build

            ```@HOST_SHELL@
            @HOST_BOOTSTRAP_COMMAND@
            cmake --preset @HOST_DEBUG_PRESET@
            cmake --build --preset @HOST_DEBUG_PRESET@
            ctest --test-dir build/@HOST_DEBUG_PRESET@ --output-on-failure
            ```

            ## Quality

            ```@HOST_SHELL@
            @HOST_FORMAT_COMMAND@
            cmake --preset @HOST_TIDY_PRESET@
            cmake --build --preset @HOST_TIDY_PRESET@
            cmake --build --preset @HOST_DEBUG_PRESET@ --target docs
            ```
            """,
            **values,
        ),
    }

    template_files = {
        "CMakeLists.txt": "CMakeLists.txt",
        "CMakePresets.json": "CMakePresets.json",
        "vcpkg.json": "vcpkg.json",
        ".vscode/extensions.json": "extensions.json",
        ".vscode/settings.json": "settings.json",
    }
    for relative, asset in template_files.items():
        files[relative] = render_asset(asset, **values)

    executable_files = {"scripts/bootstrap_vcpkg.sh", "scripts/format.sh"}
    for relative, content in files.items():
        write_file(root, relative, content, executable=relative in executable_files, force=args.force)

    print(f"Created modern C++ project at {root}")
    print(f"Host profile: {host_platform}")
    print("Next steps:")
    print(f"  {host_profile['bootstrap']}")
    print(f"  cmake --preset {host_profile['debug_preset']}")
    print(f"  cmake --build --preset {host_profile['debug_preset']}")
    print(f"  ctest --test-dir build/{host_profile['debug_preset']} --output-on-failure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
