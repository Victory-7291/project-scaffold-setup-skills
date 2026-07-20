#pragma once

#include <stdint.h>

#define __CM4_REV 0x0001U
#define __FPU_PRESENT 1U
#define __NVIC_PRIO_BITS 4U
#define __Vendor_SysTickConfig 0U

#define __I volatile const
#define __O volatile
#define __IO volatile

#define __DSB() __asm__ volatile("dsb" ::: "memory")
#define __ISB() __asm__ volatile("isb" ::: "memory")
#define __DMB() __asm__ volatile("dmb" ::: "memory")
#define __WFI() __asm__ volatile("wfi")
#define __WFE() __asm__ volatile("wfe")

static inline uint32_t __get_PSP(void) {
    uint32_t result;
    __asm__ volatile("mrs %0, psp" : "=r"(result));
    return result;
}

static inline void __set_PSP(uint32_t topOfProcStack) {
    __asm__ volatile("msr psp, %0" ::"r"(topOfProcStack));
}

static inline uint32_t __get_MSP(void) {
    uint32_t result;
    __asm__ volatile("mrs %0, msp" : "=r"(result));
    return result;
}

static inline void __set_MSP(uint32_t topOfMainStack) {
    __asm__ volatile("msr msp, %0" ::"r"(topOfMainStack));
}

static inline uint32_t __get_PRIMASK(void) {
    uint32_t result;
    __asm__ volatile("mrs %0, primask" : "=r"(result));
    return result;
}

static inline void __set_PRIMASK(uint32_t priMask) {
    __asm__ volatile("msr primask, %0" ::"r"(priMask));
}
