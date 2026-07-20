cmake_minimum_required(VERSION 3.20)

set(CMAKE_TOOLCHAIN_FILE ${CMAKE_SOURCE_DIR}/cmake/toolchain-arm-none-eabi.cmake CACHE STRING "Toolchain file")

project(cubemx_legacy_fw
    VERSION 1.0.0
    LANGUAGES C CXX ASM
)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Target MCU
set(MCU_FAMILY STM32F4xx)
set(MCU_MODEL STM32F446xx)
set(CPU_FLAGS -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard)

add_compile_options(
    ${CPU_FLAGS}
    -ffunction-sections
    -fdata-sections
    -fno-builtin
    -Wall
    -Wextra
    -Wpedantic
    -Og
    -g3
)

add_link_options(
    ${CPU_FLAGS}
    -T${CMAKE_SOURCE_DIR}/linker/STM32F446RETx_FLASH.ld
    -Wl,--gc-sections
    -Wl,-Map=${PROJECT_NAME}.map
    -nostartfiles
    -nodefaultlibs
    -lgcc
)

add_definitions(
    -D${MCU_MODEL}
    -DUSE_HAL_DRIVER
)

# HAL sources (minimal set for demonstration; expand with full CubeMX HAL as needed)
set(HAL_SRC
    ${CMAKE_SOURCE_DIR}/Drivers/${MCU_FAMILY}_HAL_Driver/Src/stm32f4xx_hal.c
    ${CMAKE_SOURCE_DIR}/Drivers/${MCU_FAMILY}_HAL_Driver/Src/stm32f4xx_hal_cortex.c
    ${CMAKE_SOURCE_DIR}/Drivers/${MCU_FAMILY}_HAL_Driver/Src/stm32f4xx_hal_gpio.c
    ${CMAKE_SOURCE_DIR}/Drivers/${MCU_FAMILY}_HAL_Driver/Src/stm32f4xx_hal_rcc.c
)

set(STARTUP_SRC
    ${CMAKE_SOURCE_DIR}/startup/startup_stm32f446xx.s
)

set(SYSTEM_SRC
    ${CMAKE_SOURCE_DIR}/Drivers/CMSIS/Device/ST/${MCU_FAMILY}/Include/system_${MCU_FAMILY}.c
)

set(APP_SRC
    ${CMAKE_SOURCE_DIR}/Src/main.c
)

include_directories(
    ${CMAKE_SOURCE_DIR}/Inc
    ${CMAKE_SOURCE_DIR}/Drivers/${MCU_FAMILY}_HAL_Driver/Inc
    ${CMAKE_SOURCE_DIR}/Drivers/CMSIS/Device/ST/${MCU_FAMILY}/Include
    ${CMAKE_SOURCE_DIR}/Drivers/CMSIS/Include
)

add_executable(${PROJECT_NAME}.elf
    ${APP_SRC}
    ${HAL_SRC}
    ${SYSTEM_SRC}
    ${STARTUP_SRC}
)

set_target_properties(${PROJECT_NAME}.elf PROPERTIES
    LINKER_LANGUAGE C
)

add_custom_command(TARGET ${PROJECT_NAME}.elf POST_BUILD
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${PROJECT_NAME}.elf>
)

add_custom_target(${PROJECT_NAME}.bin ALL
    DEPENDS ${PROJECT_NAME}.elf
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}.elf> ${PROJECT_NAME}.bin
    COMMENT "Generating binary"
)

add_custom_target(${PROJECT_NAME}.hex ALL
    DEPENDS ${PROJECT_NAME}.elf
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${PROJECT_NAME}.elf> ${PROJECT_NAME}.hex
    COMMENT "Generating hex"
)
