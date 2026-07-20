.syntax unified
.cpu cortex-m0plus
.fpu softvfp
.thumb

.global __stack_bottom
.global Reset_Handler
.global Default_Handler

/* Minimal vector table (core vectors only). */
.section .isr_vector, "a", %progbits
.type __isr_vector, %object
__isr_vector:
    .word __stack_bottom
    .word Reset_Handler
    .word NMI_Handler
    .word HardFault_Handler
    .word 0
    .word 0
    .word 0
    .word 0
    .word 0
    .word 0
    .word 0
    .word SVC_Handler
    .word 0
    .word 0
    .word PendSV_Handler
    .word SysTick_Handler
.size __isr_vector, . - __isr_vector

.section .text.Reset_Handler, "ax", %progbits
.type Reset_Handler, %function
Reset_Handler:
    ldr r0, =__stack_bottom
    mov sp, r0
    bl  SystemInit
    bl  main
    b   .

.type Default_Handler, %function
Default_Handler:
    b   Default_Handler

.macro weak_handler name
    .weak \name
    .thumb_set \name, Default_Handler
.endm

weak_handler NMI_Handler
weak_handler HardFault_Handler
weak_handler SVC_Handler
weak_handler PendSV_Handler
weak_handler SysTick_Handler
