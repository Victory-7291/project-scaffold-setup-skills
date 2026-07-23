cmake_minimum_required(VERSION 3.24)

project(@CMAKE_PROJECT@ VERSION 0.1.0 LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_EXECUTABLE_SUFFIX ".elf")

set(FIRMWARE_TARGET @TARGET@)
set(MCU_FLAGS
@CPU_FLAGS@
)

option(@UPPER@_ENABLE_CLANG_TIDY "Enable clang-tidy during firmware builds" OFF)

if(@UPPER@_ENABLE_CLANG_TIDY)
  find_program(CLANG_TIDY_EXE NAMES clang-tidy REQUIRED)
  set(CMAKE_C_CLANG_TIDY
    "${CLANG_TIDY_EXE}"
    "--extra-arg-before=--target=@CLANG_TARGET@"
  )
endif()

add_executable(${FIRMWARE_TARGET})

target_sources(${FIRMWARE_TARGET}
  PRIVATE
    startup/startup.c
    src/main.c
    src/app/app.c
    src/bsp/board.c
)

target_include_directories(${FIRMWARE_TARGET}
  PRIVATE
    include
    src
)

target_compile_definitions(${FIRMWARE_TARGET}
  PRIVATE
    @DEVICE_DEFINE@
)

target_compile_options(${FIRMWARE_TARGET}
  PRIVATE
    ${MCU_FLAGS}
    -ffunction-sections
    -fdata-sections
    -Wall
    -Wextra
    -Wpedantic
    -Wconversion
    -Wshadow
    -g
)

target_link_options(${FIRMWARE_TARGET}
  PRIVATE
    ${MCU_FLAGS}
    -T${CMAKE_CURRENT_SOURCE_DIR}/ldscripts/@TARGET@_flash.ld
    -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/${FIRMWARE_TARGET}.map
    -Wl,--gc-sections
    -Wl,--print-memory-usage
    -nostdlib
)

add_custom_command(TARGET ${FIRMWARE_TARGET} POST_BUILD
  COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${FIRMWARE_TARGET}> ${CMAKE_CURRENT_BINARY_DIR}/${FIRMWARE_TARGET}.hex
  COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${FIRMWARE_TARGET}> ${CMAKE_CURRENT_BINARY_DIR}/${FIRMWARE_TARGET}.bin
  COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${FIRMWARE_TARGET}>
  COMMENT "Generating HEX/BIN and printing firmware size"
  VERBATIM
)
