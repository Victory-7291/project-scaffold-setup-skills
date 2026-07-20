.syntax unified
.arch armv7e-m

.section .isr_vector,"a",%progbits
.type g_pfnVectors, %object
.size g_pfnVectors, .-g_pfnVectors

g_pfnVectors:
    .word _estack
    .word Reset_Handler
    .word NMI_Handler
    .word HardFault_Handler
    .word MemManage_Handler
    .word BusFault_Handler
    .word UsageFault_Handler
    .word 0
    .word 0
    .word 0
    .word 0
    .word SVC_Handler
    .word DebugMon_Handler
    .word 0
    .word PendSV_Handler
    .word SysTick_Handler
    .word WWDG_IRQHandler
    /* Additional IRQs omitted for brevity; fill with Default_Handler */

.section .text.Reset_Handler,"ax",%progbits
.weak Reset_Handler
.type Reset_Handler, %function
Reset_Handler:
    ldr sp, =_estack
    bl SystemInit
    /* Zero .bss */
    ldr r1, =_sbss
    ldr r2, =_ebss
    movs r0, #0
bss_loop:
    cmp r1, r2
    it lt
    strlt r0, [r1], #4
    blt bss_loop
    /* Copy .data */
    ldr r1, =_sidata
    ldr r2, =_sdata
    ldr r3, =_edata
data_loop:
    cmp r2, r3
    itt lt
    ldrlt r0, [r1], #4
    strlt r0, [r2], #4
    blt data_loop
    bl main
    b .
.size Reset_Handler, .-Reset_Handler

.section .text.Default_Handler,"ax",%progbits
.weak NMI_Handler
.weak HardFault_Handler
.weak MemManage_Handler
.weak BusFault_Handler
.weak UsageFault_Handler
.weak SVC_Handler
.weak DebugMon_Handler
.weak PendSV_Handler
.weak SysTick_Handler
.weak WWDG_IRQHandler

Default_Handler:
    b Default_Handler

.thumb_set NMI_Handler, Default_Handler
.thumb_set HardFault_Handler, Default_Handler
.thumb_set MemManage_Handler, Default_Handler
.thumb_set BusFault_Handler, Default_Handler
.thumb_set UsageFault_Handler, Default_Handler
.thumb_set SVC_Handler, Default_Handler
.thumb_set DebugMon_Handler, Default_Handler
.thumb_set PendSV_Handler, Default_Handler
.thumb_set SysTick_Handler, Default_Handler
.thumb_set WWDG_IRQHandler, Default_Handler
