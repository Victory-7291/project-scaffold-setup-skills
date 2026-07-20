#include <stdint.h>
#include "app_main.h"

int main(void)
{
    app_init();

    while (1) {
        app_run();
    }

    return 0;
}
