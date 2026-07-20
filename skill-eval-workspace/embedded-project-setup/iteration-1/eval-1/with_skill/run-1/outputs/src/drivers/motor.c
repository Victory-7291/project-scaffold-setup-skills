#include "drivers/motor.h"

/*
 * Placeholder motor driver implementation.
 *
 * When the STM32 HAL or LL is added to this project, replace these stubs with
 * timer/PWM setup for the NUCLEO-F446RE (TIM1/TIM2/TIM3/etc.) and the actual
 * H-bridge or inverter control logic.
 */

void motor_init(void) {
  /* TODO: enable timer clocks, configure GPIO, set up PWM channels. */
}

void motor_set_speed(int percent) {
  if (percent < 0) {
    percent = 0;
  }
  if (percent > 100) {
    percent = 100;
  }
  /* TODO: update PWM duty cycle. */
  (void)percent;
}

void motor_stop(void) {
  /* TODO: disable PWM outputs / put H-bridge in brake/coast state. */
}
