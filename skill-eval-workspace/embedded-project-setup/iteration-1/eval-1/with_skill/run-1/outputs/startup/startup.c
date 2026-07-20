typedef unsigned int uint32_t;
typedef unsigned long uintptr_t;

extern uint32_t _estack;
extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;

extern int main(void);

void Reset_Handler(void);
void Default_Handler(void);
void SystemInit(void);

void NMI_Handler(void) __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SVC_Handler(void) __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void) __attribute__((weak, alias("Default_Handler")));

void SystemInit(void) {}

__attribute__((section(".isr_vector"), used)) const uintptr_t g_pfnVectors[] = {
    (uintptr_t)&_estack,
    (uintptr_t)Reset_Handler,
    (uintptr_t)NMI_Handler,
    (uintptr_t)HardFault_Handler,
    0u,
    0u,
    0u,
    0u,
    0u,
    0u,
    0u,
    (uintptr_t)SVC_Handler,
    0u,
    0u,
    (uintptr_t)PendSV_Handler,
    (uintptr_t)SysTick_Handler,
};

void Reset_Handler(void) {
  uint32_t *src = &_sidata;
  for (uint32_t *dst = &_sdata; dst < &_edata; ++dst) {
    *dst = *src;
    ++src;
  }

  for (uint32_t *dst = &_sbss; dst < &_ebss; ++dst) {
    *dst = 0u;
  }

  SystemInit();
  (void)main();

  while (1) {
  }
}

void Default_Handler(void) {
  while (1) {
  }
}
