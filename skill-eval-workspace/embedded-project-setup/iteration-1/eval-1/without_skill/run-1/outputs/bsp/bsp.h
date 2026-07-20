#ifndef BSP_H
#define BSP_H

#ifdef __cplusplus
extern "C" {
#endif

void bsp_init(void);
void bsp_led_on(void);
void bsp_led_off(void);
void bsp_led_toggle(void);
void bsp_delay_ms(uint32_t ms);

#ifdef __cplusplus
}
#endif

#endif /* BSP_H */
