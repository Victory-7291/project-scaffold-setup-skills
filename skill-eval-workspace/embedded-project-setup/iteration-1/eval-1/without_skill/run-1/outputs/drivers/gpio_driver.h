#ifndef GPIO_DRIVER_H
#define GPIO_DRIVER_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

typedef enum {
    GPIO_PORT_A = 0,
    GPIO_PORT_B,
    GPIO_PORT_C,
    GPIO_PORT_D,
    GPIO_PORT_E,
    GPIO_PORT_F,
    GPIO_PORT_G,
    GPIO_PORT_H
} gpio_port_t;

typedef enum {
    GPIO_MODE_INPUT = 0,
    GPIO_MODE_OUTPUT,
    GPIO_MODE_AF,
    GPIO_MODE_ANALOG
} gpio_mode_t;

void gpio_driver_init(gpio_port_t port, uint32_t pin, gpio_mode_t mode);
void gpio_driver_set(gpio_port_t port, uint32_t pin);
void gpio_driver_clear(gpio_port_t port, uint32_t pin);
void gpio_driver_toggle(gpio_port_t port, uint32_t pin);
uint32_t gpio_driver_read(gpio_port_t port, uint32_t pin);

#ifdef __cplusplus
}
#endif

#endif /* GPIO_DRIVER_H */
