.syntax unified
.cpu cortex-m4
.fpu fpv4-sp-d16
.thumb

.global Default_Handler
.global Reset_Handler
.global _sidata
.global _sdata
.global _edata
.global _sbss
.global _ebss
.global _estack

/* Stack top end of 128 KiB RAM at 0x20000000 */
.word _estack

/* Vector table */
.word Reset_Handler      /* 1 Reset */
.word Default_Handler    /* 2 NMI */
.word Default_Handler    /* 3 HardFault */
.word Default_Handler    /* 4 MemManage */
.word Default_Handler    /* 5 BusFault */
.word Default_Handler    /* 6 UsageFault */
.word 0                  /* 7 Reserved */
.word 0                  /* 8 Reserved */
.word 0                  /* 9 Reserved */
.word 0                  /* 10 Reserved */
.word Default_Handler    /* 11 SVCall */
.word Default_Handler    /* 12 Debug Monitor */
.word 0                  /* 13 Reserved */
.word Default_Handler    /* 14 PendSV */
.word Default_Handler    /* 15 SysTick */

/* IRQs 0..96 (STM32F446) - all default */
.rept 97
.word Default_Handler
.endr

.section .text.Reset_Handler
.type Reset_Handler, %function
Reset_Handler:
    /* Load data section from flash to RAM */
    ldr r0, =_sidata
    ldr r1, =_sdata
    ldr r2, =_edata
    b 2f
1:
    ldr r3, [r0], #4
    str r3, [r1], #4
2:
    cmp r1, r2
    bne 1b

    /* Zero BSS */
    ldr r1, =_sbss
    ldr r2, =_ebss
    movs r3, #0
    b 4f
3:
    str r3, [r1], #4
4:
    cmp r1, r2
    bne 3b

    /* Call system init and main */
    bl SystemInit
    bl main

    /* Loop forever if main returns */
    b .

.section .text.Default_Handler
.type Default_Handler, %function
Default_Handler:
    b .

.end
