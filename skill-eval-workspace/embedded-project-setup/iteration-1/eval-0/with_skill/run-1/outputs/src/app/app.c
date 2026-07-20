#include "app/app.h"

#include "bsp/board.h"
#include "project_config.h"

static unsigned int led_on;

void app_init(void) {
  board_init();
  led_on = 0u;
  board_led_set(led_on);
}

void app_tick(void) {
  led_on = (led_on == 0u) ? 1u : 0u;
  board_led_set(led_on);
  board_delay(PROJECT_HEARTBEAT_DELAY_CYCLES);
}
