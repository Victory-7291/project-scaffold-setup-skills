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
