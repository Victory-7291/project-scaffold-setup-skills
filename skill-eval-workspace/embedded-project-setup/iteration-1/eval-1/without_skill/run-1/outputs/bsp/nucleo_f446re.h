#ifndef NUCLEO_F446RE_H
#define NUCLEO_F446RE_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include "gpio_driver.h"

/* PA5 = Arduino D13 / green user LED */
#define NUCLEO_USER_LED_PORT    GPIO_PORT_A
#define NUCLEO_USER_LED_PIN     5

/* PC13 = blue user button */
#define NUCLEO_USER_BUTTON_PORT GPIO_PORT_C
#define NUCLEO_USER_BUTTON_PIN  13

void nucleo_f446re_init(void);

#ifdef __cplusplus
}
#endif

#endif /* NUCLEO_F446RE_H */
