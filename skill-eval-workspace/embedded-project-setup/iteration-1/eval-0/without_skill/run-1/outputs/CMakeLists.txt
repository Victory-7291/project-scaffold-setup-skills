cmake_minimum_required(VERSION 3.20)

# Use the ARM GCC toolchain for this project.
set(CMAKE_TOOLCHAIN_FILE ${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchain-arm-none-eabi.cmake
    CACHE FILEPATH "ARM GCC toolchain file")

project(smart_sensor_node C ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(TARGET_MCU STM32G030C8T6)
set(LINKER_SCRIPT ${CMAKE_SOURCE_DIR}/linker/STM32G030C8Tx_FLASH.ld)

# Common compile flags for Cortex-M0+.
add_compile_options(
    -mcpu=cortex-m0plus
    -mthumb
    -mfloat-abi=soft
    -ffunction-sections
    -fdata-sections
    -Wall
    -Wextra
    -g
    -O0
)

# Linker flags.
add_link_options(
    -T${LINKER_SCRIPT}
    -mcpu=cortex-m0plus
    -mthumb
    -mfloat-abi=soft
    -specs=nano.specs
    -lc -lm -lnosys
    -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.map,--cref
    -Wl,--gc-sections
)

include_directories(
    ${CMAKE_SOURCE_DIR}/include
)

add_executable(${PROJECT_NAME}.elf
    src/startup_stm32g030xx.s
    src/system_stm32g0xx.c
    src/main.c
)

# Generate HEX/BIN artifacts and print ELF size after each build.
add_custom_command(TARGET ${PROJECT_NAME}.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${PROJECT_NAME}.elf>
            ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}.elf>
            ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.bin
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${PROJECT_NAME}.elf>
    COMMENT "Generating HEX/BIN artifacts and printing size"
)
