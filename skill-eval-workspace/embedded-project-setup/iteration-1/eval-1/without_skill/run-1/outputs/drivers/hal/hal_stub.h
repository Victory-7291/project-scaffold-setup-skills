#ifndef HAL_STUB_H
#define HAL_STUB_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

/* STM32 HAL placeholder.
   Replace this file with the official STM32F4xx HAL headers and source
   files when migrating to the full ST device library. */

#define HAL_OK      0
#define HAL_ERROR   1
#define HAL_BUSY    2
#define HAL_TIMEOUT 3

typedef uint32_t HAL_StatusTypeDef;

typedef struct {
    uint32_t dummy;
} HAL_HandleTypeDef;

#ifdef __cplusplus
}
#endif

#endif /* HAL_STUB_H */
