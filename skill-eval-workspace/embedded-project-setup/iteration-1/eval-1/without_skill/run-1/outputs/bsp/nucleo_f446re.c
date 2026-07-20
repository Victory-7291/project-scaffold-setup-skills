#include "nucleo_f446re.h"
#include "gpio_driver.h"

void nucleo_f446re_init(void)
{
    gpio_driver_init(NUCLEO_USER_LED_PORT, NUCLEO_USER_LED_PIN, GPIO_MODE_OUTPUT);
    gpio_driver_init(NUCLEO_USER_BUTTON_PORT, NUCLEO_USER_BUTTON_PIN, GPIO_MODE_INPUT);
}
