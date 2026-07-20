#include "stm32f4xx_hal.h"

static uint32_t uwTick;

HAL_StatusTypeDef HAL_Init(void) {
    uwTick = 0U;
    return HAL_OK;
}

void HAL_IncTick(void) {
    uwTick++;
}

uint32_t HAL_GetTick(void) {
    return uwTick;
}

void HAL_Delay(uint32_t Delay) {
    uint32_t tickstart = HAL_GetTick();
    while ((HAL_GetTick() - tickstart) < Delay) {
    }
}
