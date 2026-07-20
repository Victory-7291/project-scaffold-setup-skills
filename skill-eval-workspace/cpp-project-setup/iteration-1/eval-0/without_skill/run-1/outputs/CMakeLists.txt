cmake_minimum_required(VERSION 3.25)

project(image_tool
    VERSION 0.1.0
    DESCRIPTION "Command-line image metadata and conversion utility"
    LANGUAGES CXX
)

# Global C++ standard and build options
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Export compile commands for IDE integration and clangd
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Include GNUInstallDirs for standardized install paths
include(GNUInstallDirs)

# vcpkg toolchain should already be injected via CMAKE_TOOLCHAIN_FILE.
# When vcpkg is active, find dependencies through config mode packages.
find_package(CLI11 CONFIG REQUIRED)
find_package(fmt CONFIG REQUIRED)
find_package(Catch2 CONFIG REQUIRED)

# Main library: keeps core logic testable and reusable
add_library(image_tool_lib STATIC)
add_library(image_tool::image_tool_lib ALIAS image_tool_lib)

target_sources(image_tool_lib
    PRIVATE
        src/image_tool/image_info.cpp
    PUBLIC
        FILE_SET HEADERS
        BASE_DIRS include
        FILES
            include/image_tool/image_info.hpp
)

target_link_libraries(image_tool_lib
    PUBLIC
        fmt::fmt
)

target_compile_options(image_tool_lib
    PRIVATE
        $<$<CXX_COMPILER_ID:AppleClang,Clang,GNU>:
            -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow
        >
        $<$<CXX_COMPILER_ID:MSVC>:/W4 /permissive->
)

# CLI executable
add_executable(image_tool src/main.cpp)

target_link_libraries(image_tool
    PRIVATE
        image_tool::image_tool_lib
        CLI11::CLI11
)

# Tests
enable_testing()
add_executable(image_tool_tests
    tests/test_image_info.cpp
    tests/test_main.cpp
)

target_link_libraries(image_tool_tests
    PRIVATE
        image_tool::image_tool_lib
        Catch2::Catch2WithMain
)

catch_discover_tests(image_tool_tests)

# Installation rules
install(TARGETS image_tool image_tool_lib
    EXPORT image_toolTargets
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(EXPORT image_toolTargets
    FILE image_toolTargets.cmake
    NAMESPACE image_tool::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/image_tool
)

# Simple packaging support
include(CPack)
