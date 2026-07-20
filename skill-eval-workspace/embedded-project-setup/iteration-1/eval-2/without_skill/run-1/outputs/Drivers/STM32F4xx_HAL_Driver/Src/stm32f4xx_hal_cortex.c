#include "stm32f4xx_hal.h"

void HAL_NVIC_SetPriority(IRQn_Type IRQn, uint32_t PreemptPriority, uint32_t SubPriority) {
    (void)IRQn;
    (void)PreemptPriority;
    (void)SubPriority;
}

void HAL_NVIC_EnableIRQ(IRQn_Type IRQn) {
    (void)IRQn;
}

void HAL_NVIC_DisableIRQ(IRQn_Type IRQn) {
    (void)IRQn;
}
