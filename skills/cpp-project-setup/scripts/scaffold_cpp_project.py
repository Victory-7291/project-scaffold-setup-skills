#!/usr/bin/env python3
"""Scaffold a modern C++ CMake/vcpkg project."""

from __future__ import annotations

import argparse
import re
import stat
import textwrap
from pathlib import Path


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
    parser.add_argument("--cpp-standard", default="20", choices=["17", "20", "23"], help="C++ language standard")
    parser.add_argument("--clangd-preset", default="macos-debug", help="Preset whose build directory clangd should read")
    parser.add_argument("--force", action="store_true", help="Overwrite scaffold-owned files if they already exist")
    args = parser.parse_args()

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
        "CLANGD_PRESET": args.clangd_preset,
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
                  "name": "macos-debug",
                  "inherits": "base",
                  "displayName": "macOS Debug",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Debug",
                    "VCPKG_TARGET_TRIPLET": "arm64-osx"
                  }
                },
                {
                  "name": "macos-release",
                  "inherits": "base",
                  "displayName": "macOS Release",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "VCPKG_TARGET_TRIPLET": "arm64-osx"
                  }
                },
                {
                  "name": "macos-tidy",
                  "inherits": "macos-debug",
                  "displayName": "macOS clang-tidy",
                  "cacheVariables": {
                    "@UPPER@_ENABLE_CLANG_TIDY": "ON"
                  }
                },
                {
                  "name": "linux-debug",
                  "inherits": "base",
                  "displayName": "Linux Debug",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Debug",
                    "VCPKG_TARGET_TRIPLET": "x64-linux"
                  }
                },
                {
                  "name": "linux-release",
                  "inherits": "base",
                  "displayName": "Linux Release",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "VCPKG_TARGET_TRIPLET": "x64-linux"
                  }
                },
                {
                  "name": "linux-tidy",
                  "inherits": "linux-debug",
                  "displayName": "Linux clang-tidy",
                  "cacheVariables": {
                    "@UPPER@_ENABLE_CLANG_TIDY": "ON"
                  }
                },
                {
                  "name": "windows-debug",
                  "inherits": "base",
                  "displayName": "Windows Debug",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Debug",
                    "VCPKG_TARGET_TRIPLET": "x64-windows"
                  }
                },
                {
                  "name": "windows-release",
                  "inherits": "base",
                  "displayName": "Windows Release",
                  "cacheVariables": {
                    "CMAKE_BUILD_TYPE": "Release",
                    "VCPKG_TARGET_TRIPLET": "x64-windows"
                  }
                },
                {
                  "name": "windows-tidy",
                  "inherits": "windows-debug",
                  "displayName": "Windows clang-tidy",
                  "cacheVariables": {
                    "@UPPER@_ENABLE_CLANG_TIDY": "ON"
                  }
                }
              ],
              "buildPresets": [
                { "name": "macos-debug", "configurePreset": "macos-debug" },
                { "name": "macos-release", "configurePreset": "macos-release" },
                { "name": "macos-tidy", "configurePreset": "macos-tidy" },
                { "name": "linux-debug", "configurePreset": "linux-debug" },
                { "name": "linux-release", "configurePreset": "linux-release" },
                { "name": "linux-tidy", "configurePreset": "linux-tidy" },
                { "name": "windows-debug", "configurePreset": "windows-debug" },
                { "name": "windows-release", "configurePreset": "windows-release" },
                { "name": "windows-tidy", "configurePreset": "windows-tidy" }
              ],
              "testPresets": [
                {
                  "name": "macos-debug",
                  "configurePreset": "macos-debug",
                  "output": { "outputOnFailure": true }
                },
                {
                  "name": "linux-debug",
                  "configurePreset": "linux-debug",
                  "output": { "outputOnFailure": true }
                },
                {
                  "name": "windows-debug",
                  "configurePreset": "windows-debug",
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
                  "program": "${workspaceFolder}/build/windows-debug/src/@TARGET@_app.exe",
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

            ## Setup

            ```bash
            brew install cmake ninja llvm git
            bash scripts/bootstrap_vcpkg.sh
            cmake --preset macos-debug
            cmake --build --preset macos-debug
            ctest --test-dir build/macos-debug --output-on-failure
            ```

            Use `linux-debug` on Linux. On Windows, run `pwsh scripts/bootstrap_vcpkg.ps1`
            and then configure with the `windows-debug` preset from a Visual Studio developer shell.

            ## Quality

            ```bash
            bash scripts/format.sh --check
            cmake --preset macos-tidy
            cmake --build --preset macos-tidy
            cmake --build --preset macos-debug --target docs
            ```
            """,
            **values,
        ),
    }

    executable_files = {"scripts/bootstrap_vcpkg.sh", "scripts/format.sh"}
    for relative, content in files.items():
        write_file(root, relative, content, executable=relative in executable_files, force=args.force)

    print(f"Created modern C++ project at {root}")
    print("Next steps:")
    print("  bash scripts/bootstrap_vcpkg.sh")
    print("  cmake --preset macos-debug")
    print("  cmake --build --preset macos-debug")
    print("  ctest --test-dir build/macos-debug --output-on-failure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
