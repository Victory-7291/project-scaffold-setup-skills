#include "bsp.h"
#include "gpio_driver.h"
#include "nucleo_f446re.h"

void bsp_init(void)
{
    nucleo_f446re_init();
}

void bsp_led_on(void)
{
    gpio_driver_set(NUCLEO_USER_LED_PORT, NUCLEO_USER_LED_PIN);
}

void bsp_led_off(void)
{
    gpio_driver_clear(NUCLEO_USER_LED_PORT, NUCLEO_USER_LED_PIN);
}

void bsp_led_toggle(void)
{
    gpio_driver_toggle(NUCLEO_USER_LED_PORT, NUCLEO_USER_LED_PIN);
}

void bsp_delay_ms(uint32_t ms)
{
    /* Simple busy-loop stub assuming ~180 MHz system clock */
    for (uint32_t i = 0; i < ms; ++i) {
        for (volatile uint32_t j = 0; j < 40000; ++j) {
            __asm__ volatile("nop");
        }
    }
}
