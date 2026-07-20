#include "stm32g030xx.h"
#include <stdint.h>

static void delay(volatile uint32_t count)
{
    while (count--)
    {
        __asm__ volatile("nop");
    }
}

int main(void)
{
    /* Enable GPIOA clock. */
    RCC->IOPENR |= RCC_IOPENR_GPIOAEN;

    /* Configure PA5 as push-pull output (LED on many Nucleo-64 boards). */
    GPIOA->MODER &= ~(3U << (5U * 2U));
    GPIOA->MODER |= (1U << (5U * 2U));

    while (1)
    {
        GPIOA->ODR ^= (1U << 5U);
        delay(200000U);
    }
}

/* Core exception handlers - these override the weak defaults in the startup file. */
void NMI_Handler(void) { while (1) {} }
void HardFault_Handler(void) { while (1) {} }
void SVC_Handler(void) { while (1) {} }
void PendSV_Handler(void) { while (1) {} }
void SysTick_Handler(void) { while (1) {} }
