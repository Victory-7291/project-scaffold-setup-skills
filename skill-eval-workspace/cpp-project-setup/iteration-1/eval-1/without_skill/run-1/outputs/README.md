Legacy C++ project (modernized)
================================

This project has been modernized from a hand-written Makefile to CMake + vcpkg.

Build
-----

Requires CMake 3.20+, a C++17 compiler, and vcpkg (with `VCPKG_ROOT` set).

```bash
cmake --preset vcpkg
cmake --build build
./build/hello
```

Run tests
---------

```bash
ctest --test-dir build --output-on-failure
```

The original behavior is preserved: `./build/hello` prints
`Hello, legacy C++ project!`.

Tooling
-------

- `.clang-format` / `.clang-tidy` — code style and static analysis
- `.vscode/` — VS Code settings, build tasks, and debug launch config
- `CMakePresets.json` — reusable CMake configure/build/test presets
