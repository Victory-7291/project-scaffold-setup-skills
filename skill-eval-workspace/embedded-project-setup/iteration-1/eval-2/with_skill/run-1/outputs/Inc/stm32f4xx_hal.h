#pragma once

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Minimal HAL initialization stub.
 *
 * The legacy application expects the STM32F4xx HAL. In a real project this
 * header is provided by the STM32CubeF4 HAL package and the implementation
 * is built from the HAL source tree. A stub is included here so the
 * modernized CMake build can compile the existing application code.
 */
void HAL_Init(void);

#ifdef __cplusplus
}
#endif
