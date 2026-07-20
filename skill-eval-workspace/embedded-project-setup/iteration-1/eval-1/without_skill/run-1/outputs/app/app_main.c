#include "app_main.h"
#include "motor_control.h"
#include "bsp.h"

void app_init(void)
{
    bsp_init();
    motor_control_init();
}

void app_run(void)
{
    motor_control_tick();
    bsp_led_toggle();
    bsp_delay_ms(1);
}
