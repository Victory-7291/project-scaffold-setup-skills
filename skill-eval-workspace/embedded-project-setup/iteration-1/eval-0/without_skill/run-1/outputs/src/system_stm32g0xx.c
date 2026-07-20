#include "system_stm32g0xx.h"
#include <stdint.h>

uint32_t SystemCoreClock = 16000000U;

void SystemInit(void)
{
    /* HSI is the default clock source at 16 MHz after reset. */
    SystemCoreClock = 16000000U;
}

void SystemCoreClockUpdate(void)
{
    SystemCoreClock = 16000000U;
}
