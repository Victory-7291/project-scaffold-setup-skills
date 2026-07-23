# Project Scaffold Setup Skills

Reusable skills for coding agents that need to create or modernize engineering projects with a clear structure, explicit toolchains, editor integration, and repeatable validation steps.

This README is a catalog of the available skills. Each skill is designed to help an agent decide whether it is working in a new or existing project, choose the right platform profile, apply a conservative scaffold or modernization path, and report what was validated locally.

## Available Skills

| Skill | Use It For | What It Sets Up |
| --- | --- | --- |
| `cpp-project-setup` | Host-side C++ applications and libraries on macOS, Linux, or Windows. Use it for new C++ projects, existing CMake modernization, VS Code setup, vcpkg/CMake presets, testing, formatting, linting, documentation, and reproducible developer workflows. | CMake, CMake Presets, vcpkg manifest mode, Ninja, Clang/GCC/MSVC profiles, GoogleTest, clangd, clang-format, clang-tidy, Doxygen, VS Code debug settings, and CI-ready structure. |
| `embedded-project-setup` | STM32/Cortex-M embedded C firmware projects. Use it for new firmware scaffolds, existing firmware modernization, cross CMake toolchains, linker/startup files, OpenOCD flashing, Cortex-Debug setup, and embedded CI. | CMake, Ninja, `arm-none-eabi-gcc/gdb`, STM32 firmware outputs, linker scripts, startup code, OpenOCD, ST-Link/J-Link workflows, Cortex-Debug, clangd, clang-format, clang-tidy, Docker/GitHub Actions-ready structure, and layered CMSIS/HAL/LL or bare-metal organization. |
| `python-fastapi-setup` | Python FastAPI services and APIs. Use it for new FastAPI scaffolds, existing single-file or wrapper-launched app modernization, typed settings, lifespan-managed resources, middleware, routers, tests, and deployment commands. | `app/main.py`, versioned API routers, pydantic-settings, lifespan plus `app.state` dependency accessors, request ID/CORS middleware, `/health`, pytest/TestClient, Uvicorn/FastAPI CLI, optional Docker/Compose, and optional Gunicorn via `uvicorn-worker`. |

## What The Skills Do

These skills are meant for agents, not just humans reading setup notes. They guide an agent to:

- Inspect the current working directory before writing files.
- Distinguish greenfield scaffolding from existing-project modernization.
- Detect or ask for the target host platform when toolchain choices depend on OS and CPU architecture.
- Prefer repeatable, project-local configuration over hidden global assumptions.
- Generate conservative starter projects only when appropriate.
- Preserve existing user work when modernizing a repository.
- Run the strongest available validation commands and clearly report skipped checks when local tools or hardware are missing.

## Installation

List installable skills from this repository:

```bash
npx skills add https://github.com/Victory-7291/project-scaffold-setup-skills --list
```

Install every skill:

```bash
npx skills add https://github.com/Victory-7291/project-scaffold-setup-skills 
```

Install only the C++ project setup skill:

```bash
npx skills add https://github.com/Victory-7291/project-scaffold-setup-skills --skill cpp-project-setup
```

Install only the embedded firmware setup skill:

```bash
npx skills add https://github.com/Victory-7291/project-scaffold-setup-skills --skill embedded-project-setup
```

Install only the Python FastAPI setup skill:

```bash
npx skills add https://github.com/Victory-7291/project-scaffold-setup-skills --skill python-fastapi-setup
```

## Example Prompts

Use `cpp-project-setup` when asking an agent for host-side C++ work:

```text
Use $cpp-project-setup to create a new C++20 command line app named telemetry_tool with CMake, vcpkg, GoogleTest, clang-format, clang-tidy, Doxygen, and VS Code debug support.
```

Use `embedded-project-setup` when asking an agent for MCU firmware work:

```text
Use $embedded-project-setup to scaffold STM32 firmware for an STM32G030C8T6 board with CMake, arm-none-eabi-gcc, OpenOCD, Cortex-Debug, clangd, formatting, analysis, and flash scripts.
```

Use `python-fastapi-setup` when asking an agent for FastAPI service work:

```text
Use $python-fastapi-setup to scaffold a FastAPI service named inventory_api with typed settings, lifespan-managed resources, request ID middleware, /health, tests, and Docker Compose.
```

## Skill Behavior At A Glance

| Skill | Greenfield Default | Existing Project Behavior | Validation Focus |
| --- | --- | --- | --- |
| `cpp-project-setup` | App plus reusable library target, C++20, vcpkg, GoogleTest, format/lint/docs, VS Code integration. | Inventory the current build, dependency, editor, test, lint, docs, CI, and packaging setup before making scoped changes. | CMake presets, vcpkg bootstrap, build, `ctest`, formatting, clang-tidy, and docs generation when tools are available. |
| `embedded-project-setup` | Minimal STM32/Cortex-M firmware scaffold with CMake presets, cross toolchain, startup/linker files, smoke code, flash/debug entry points. | Inspect existing firmware layers, build scripts, toolchain files, linker/startup flow, vendor model, debug scripts, editor settings, and CI before editing. | Configure/build, firmware artifacts, formatting, static analysis, and optional hardware flashing/debug validation when hardware is attached. |
| `python-fastapi-setup` | Minimal FastAPI service with app factory, versioned routers, typed settings, request ID middleware, health check, tests, and optional Docker files. | Inspect existing ASGI entrypoints, route contracts, settings, middleware, dependency manager, tests, and startup commands before preserving behavior in a standard layout. | Python compile/import checks, pytest, Uvicorn health smoke, optional Gunicorn smoke, and optional Docker build/run health checks. |

## License

MIT License.
