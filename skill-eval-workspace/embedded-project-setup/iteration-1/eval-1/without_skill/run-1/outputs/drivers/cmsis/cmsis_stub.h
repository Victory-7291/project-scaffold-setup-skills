#ifndef CMSIS_STUB_H
#define CMSIS_STUB_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

/* Minimal CMSIS-Core-M register access stubs used by this scaffold.
   Replace these with the real CMSIS headers when integrating the
   STMicroelectronics device support package. */

#define __I     volatile const
#define __O     volatile
#define __IO    volatile

#define __STATIC_INLINE static inline

static inline void __enable_irq(void)  { __asm__ volatile("cpsie i"); }
static inline void __disable_irq(void) { __asm__ volatile("cpsid i"); }
static inline void __NOP(void)         { __asm__ volatile("nop"); }

#ifdef __cplusplus
}
#endif

#endif /* CMSIS_STUB_H */
