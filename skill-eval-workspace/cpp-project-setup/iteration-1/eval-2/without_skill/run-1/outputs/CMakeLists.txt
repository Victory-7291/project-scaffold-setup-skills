cmake_minimum_required(VERSION 3.21)

project(math_utils
    VERSION 0.1.0
    DESCRIPTION "Cross-platform C++20 math utilities static library"
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(MATH_UTILS_BUILD_TESTS "Build math_utils unit tests" ON)
option(MATH_UTILS_ENABLE_CLANG_TIDY "Enable clang-tidy analysis" ON)

include(cmake/tools.cmake)

add_library(math_utils STATIC)
add_library(math_utils::math_utils ALIAS math_utils)

target_sources(math_utils
    PRIVATE
        src/arithmetic.cpp
        src/constants.cpp
    PUBLIC
        FILE_SET HEADERS
        BASE_DIRS include
        FILES
            include/math_utils/math_utils.hpp
            include/math_utils/math_utils/arithmetic.hpp
            include/math_utils/math_utils/constants.hpp
)

target_include_directories(math_utils
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_compile_features(math_utils PUBLIC cxx_std_20)

if(MSVC)
    target_compile_options(math_utils PRIVATE /W4 /WX- /permissive- /Zc:__cplusplus)
else()
    target_compile_options(math_utils PRIVATE -Wall -Wextra -Wpedantic)
endif()

if(MATH_UTILS_ENABLE_CLANG_TIDY)
    enable_clang_tidy(math_utils)
endif()

include(GNUInstallDirs)

install(TARGETS math_utils
    EXPORT math_utils-targets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    FILE_SET HEADERS DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(EXPORT math_utils-targets
    FILE math_utils-targets.cmake
    NAMESPACE math_utils::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/math_utils
)

include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/math_utils-config-version.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/math_utils-config.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/math_utils-config.cmake
    @ONLY
)

install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/math_utils-config.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/math_utils-config-version.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/math_utils
)

if(MATH_UTILS_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()
