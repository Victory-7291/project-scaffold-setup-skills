#include "app/app.h"

int main(void) {
  app_init();

  while (1) {
    app_tick();
  }
}
