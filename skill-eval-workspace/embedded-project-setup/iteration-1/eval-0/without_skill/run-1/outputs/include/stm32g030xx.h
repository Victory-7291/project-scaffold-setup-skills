#ifndef STM32G030XX_H
#define STM32G030XX_H

#include <stdint.h>

#define __IO volatile
#define __I  volatile const

typedef struct
{
    __IO uint32_t MODER;
    __IO uint32_t OTYPER;
    __IO uint32_t OSPEEDR;
    __IO uint32_t PUPDR;
    __IO uint32_t IDR;
    __IO uint32_t ODR;
    __IO uint32_t BSRR;
    __IO uint32_t LCKR;
    __IO uint32_t AFR[2];
} GPIO_TypeDef;

#define GPIOA_BASE 0x50000000UL
#define GPIOB_BASE 0x50000400UL
#define GPIOC_BASE 0x50000800UL

#define GPIOA ((GPIO_TypeDef *)GPIOA_BASE)
#define GPIOB ((GPIO_TypeDef *)GPIOB_BASE)
#define GPIOC ((GPIO_TypeDef *)GPIOC_BASE)

typedef struct
{
    __IO uint32_t CR;
    __IO uint32_t ICSCR;
    __IO uint32_t CFGR;
    uint32_t RESERVED0;
    __IO uint32_t CRRCR;
    __IO uint32_t CIER;
    __IO uint32_t CIFR;
    __IO uint32_t CICR;
    __IO uint32_t IOPRSTR;
    __IO uint32_t AHBRSTR;
    __IO uint32_t APBRSTR1;
    __IO uint32_t APBRSTR2;
    __IO uint32_t IOPENR;
    __IO uint32_t AHBENR;
    __IO uint32_t APBENR1;
    __IO uint32_t APBENR2;
    __IO uint32_t IOPSMENR;
    __IO uint32_t AHBSMENR;
    __IO uint32_t APBSMENR1;
    __IO uint32_t APBSMENR2;
    __IO uint32_t CCIPR;
    uint32_t RESERVED1;
    __IO uint32_t BDCR;
    __IO uint32_t CSR;
} RCC_TypeDef;

#define RCC_BASE 0x40021000UL
#define RCC ((RCC_TypeDef *)RCC_BASE)

#define RCC_IOPENR_GPIOAEN (1U << 0U)
#define RCC_IOPENR_GPIOBEN (1U << 1U)
#define RCC_IOPENR_GPIOCEN (1U << 2U)

#endif /* STM32G030XX_H */
