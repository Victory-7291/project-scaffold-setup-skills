#include "gpio_driver.h"
#include "cmsis_stub.h"

/* GPIO register block base addresses */
static uint32_t gpio_bases[] = {
    0x40020000UL, /* GPIOA */
    0x40020400UL, /* GPIOB */
    0x40020800UL, /* GPIOC */
    0x40020C00UL, /* GPIOD */
    0x40021000UL, /* GPIOE */
    0x40021400UL, /* GPIOF */
    0x40021800UL, /* GPIOG */
    0x40021C00UL  /* GPIOH */
};

void gpio_driver_init(gpio_port_t port, uint32_t pin, gpio_mode_t mode)
{
    (void)port;
    (void)pin;
    (void)mode;
    /* Stub: enable peripheral clock and configure MODER register */
}

void gpio_driver_set(gpio_port_t port, uint32_t pin)
{
    (void)port;
    (void)pin;
}

void gpio_driver_clear(gpio_port_t port, uint32_t pin)
{
    (void)port;
    (void)pin;
}

void gpio_driver_toggle(gpio_port_t port, uint32_t pin)
{
    (void)port;
    (void)pin;
}

uint32_t gpio_driver_read(gpio_port_t port, uint32_t pin)
{
    (void)port;
    (void)pin;
    return 0;
}
