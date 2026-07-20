#include "motor_control.h"
#include "tim_driver.h"
#include <stdint.h>

static int32_t g_motor_speed_rpm;
static uint32_t g_pwm_duty;

void motor_control_init(void)
{
    g_motor_speed_rpm = 0;
    g_pwm_duty = 0;
    tim_driver_init(20000); /* 20 kHz PWM frequency */
}

void motor_control_tick(void)
{
    /* Stub: read encoder/sensor and update PWM */
    g_motor_speed_rpm = (int32_t)tim_driver_capture_count();
    g_pwm_duty += 1;
    if (g_pwm_duty >= 1000) {
        g_pwm_duty = 0;
    }
    tim_driver_set_duty(g_pwm_duty);
}
