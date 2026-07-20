cmake_minimum_required(VERSION 3.20)

project(legacy_greeter
    VERSION 1.0.0
    DESCRIPTION "Modernized legacy C++ greeting project"
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Export compile_commands.json for tooling
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# --- vcpkg integration ---
if(DEFINED ENV{VCPKG_ROOT})
    set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
        CACHE STRING "vcpkg toolchain")
endif()

# --- Library ---
add_library(greeter STATIC
    src/greeter.cpp
    include/greeter/greeter.hpp
)
add_library(legacy_greeter::greeter ALIAS greeter)

target_include_directories(greeter
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_compile_features(greeter PUBLIC cxx_std_17)

# --- Executable ---
add_executable(hello src/main.cpp)
target_link_libraries(hello PRIVATE legacy_greeter::greeter)

# --- Tests ---
enable_testing()
add_subdirectory(tests)

# --- Optional clang-tidy ---
find_program(CLANG_TIDY_EXE NAMES clang-tidy)
if(CLANG_TIDY_EXE)
    set(CMAKE_CXX_CLANG_TIDY ${CLANG_TIDY_EXE})
endif()
