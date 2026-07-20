#include <stdint.h>

extern uint32_t _estack;

void SystemInit(void)
{
    /* Enable FPU (CP10/CP11 full access) */
    uint32_t cpacr = *(volatile uint32_t *)0xE000ED88UL;
    cpacr |= (0xFUL << 20);
    *(volatile uint32_t *)0xE000ED88UL = cpacr;

    /* Reset clock configuration could be placed here.
       For the scaffold, the default reset clock is acceptable. */
}
