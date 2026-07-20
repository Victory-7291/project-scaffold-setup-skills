#include "tim_driver.h"
#include "cmsis_stub.h"

static uint32_t g_pwm_freq;
static uint32_t g_duty;

void tim_driver_init(uint32_t pwm_freq_hz)
{
    g_pwm_freq = pwm_freq_hz;
    g_duty = 0;
    /* Stub: enable TIM clock, configure period, prescaler, PWM channel */
}

void tim_driver_set_duty(uint32_t duty)
{
    g_duty = duty;
    /* Stub: update CCRx register */
}

uint32_t tim_driver_capture_count(void)
{
    /* Stub: return encoder capture value */
    return g_duty;
}
