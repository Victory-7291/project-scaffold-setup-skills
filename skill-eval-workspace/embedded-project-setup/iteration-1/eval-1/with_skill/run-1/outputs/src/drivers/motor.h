#pragma once

/**
 * @file motor.h
 * @brief Motor driver placeholder for the NUCLEO-F446RE motor-control project.
 *
 * This is a minimal placeholder. In a real project, replace it with hardware-
 * specific PWM/timer driver code, or wire it to STM32 HAL/LL timer APIs once
 * the HAL sources are vendored or otherwise provided.
 */

void motor_init(void);
void motor_set_speed(int percent);
void motor_stop(void);
