#ifndef TIM_DRIVER_H
#define TIM_DRIVER_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

void tim_driver_init(uint32_t pwm_freq_hz);
void tim_driver_set_duty(uint32_t duty);
uint32_t tim_driver_capture_count(void);

#ifdef __cplusplus
}
#endif

#endif /* TIM_DRIVER_H */
