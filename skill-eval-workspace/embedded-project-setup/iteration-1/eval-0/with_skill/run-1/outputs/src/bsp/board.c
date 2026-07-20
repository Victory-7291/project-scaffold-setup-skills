#include "bsp/board.h"

#define REG32(address) (*(volatile unsigned int *)(address))

#define RCC_IOPENR REG32(0x40021034u)
#define RCC_IOPENR_GPIOAEN (1u << 0u)

#define GPIOA_BASE (0x50000000u)
#define GPIOA_MODER REG32(GPIOA_BASE + 0x00u)
#define GPIOA_BSRR REG32(GPIOA_BASE + 0x18u)

#define LED_PIN (5u)
#define MODER_BITS_PER_PIN (2u)
#define GPIO_MODER_MASK (0x3u)
#define GPIO_MODER_OUTPUT (0x1u)

void board_init(void) {
  RCC_IOPENR |= RCC_IOPENR_GPIOAEN;

  const unsigned int shift = LED_PIN * MODER_BITS_PER_PIN;
  unsigned int moder = GPIOA_MODER;
  moder &= (unsigned int)~(GPIO_MODER_MASK << shift);
  moder |= (GPIO_MODER_OUTPUT << shift);
  GPIOA_MODER = moder;
}

void board_led_set(unsigned int enabled) {
  if (enabled) {
    GPIOA_BSRR = (1u << LED_PIN);
  } else {
    GPIOA_BSRR = (1u << (LED_PIN + 16u));
  }
}

void board_delay(unsigned int cycles) {
  volatile unsigned int remaining = cycles;
  while (remaining > 0u) {
    __asm volatile("nop");
    --remaining;
  }
}
