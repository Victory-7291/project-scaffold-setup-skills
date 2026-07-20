# Makefile for NUCLEO-F446RE motor-control firmware

PREFIX  ?= arm-none-eabi-
CC      := $(PREFIX)gcc
LD      := $(PREFIX)gcc
OBJCOPY := $(PREFIX)objcopy
OBJDUMP := $(PREFIX)objdump
SIZE    := $(PREFIX)size

PROJECT := firmware
BUILD   := build

# MCU flags
CPU     := -mcpu=cortex-m4
THUMB   := -mthumb
FPU     := -mfpu=fpv4-sp-d16
FLOAT   := -mfloat-abi=hard
MCU     := $(CPU) $(THUMB) $(FPU) $(FLOAT)

# Directories
SRC_DIRS := src app bsp drivers/cmsis drivers/hal startup
INC_DIRS := $(SRC_DIRS)

# Source files
C_SRC   := $(foreach dir,$(SRC_DIRS),$(wildcard $(dir)/*.c))
ASM_SRC := $(wildcard startup/*.s) $(wildcard startup/*.S)
OBJS    := $(addprefix $(BUILD)/,$(notdir $(C_SRC:.c=.o)))
OBJS    += $(addprefix $(BUILD)/,$(notdir $(ASM_SRC:.s=.o)))
OBJS    := $(OBJS:.S=.o)

# VPATH so make can find sources under multiple directories
VPATH := $(SRC_DIRS)

# Compiler / assembler flags
DEFS    := -DSTM32F446xx -DUSE_FULL_LL_DRIVER -DUSE_HAL_DRIVER
CFLAGS  := $(MCU) $(DEFS) -O2 -g3 -Wall -Wextra -ffunction-sections -fdata-sections
CFLAGS  += $(foreach dir,$(INC_DIRS),-I$(dir))

ASMFLAGS := $(MCU) -x assembler-with-cpp

LDFLAGS := $(MCU) -Tlinker/STM32F446RETx_FLASH.ld
LDFLAGS += -specs=nano.specs -specs=nosys.specs
LDFLAGS += -Wl,--gc-sections -Wl,-Map=$(BUILD)/$(PROJECT).map

.PHONY: all clean flash size

all: $(BUILD)/$(PROJECT).elf $(BUILD)/$(PROJECT).bin $(BUILD)/$(PROJECT).hex size

$(BUILD)/%.o: %.c | $(BUILD)
	$(CC) -c $(CFLAGS) $< -o $@

$(BUILD)/%.o: %.s | $(BUILD)
	$(CC) -c $(ASMFLAGS) $< -o $@

$(BUILD)/%.o: %.S | $(BUILD)
	$(CC) -c $(ASMFLAGS) $< -o $@

$(BUILD)/$(PROJECT).elf: $(OBJS) linker/STM32F446RETx_FLASH.ld
	$(LD) $(OBJS) $(LDFLAGS) -o $@

$(BUILD)/$(PROJECT).bin: $(BUILD)/$(PROJECT).elf
	$(OBJCOPY) -O binary $< $@

$(BUILD)/$(PROJECT).hex: $(BUILD)/$(PROJECT).elf
	$(OBJCOPY) -O ihex $< $@

$(BUILD):
	mkdir -p $@

size: $(BUILD)/$(PROJECT).elf
	$(SIZE) $<

flash: $(BUILD)/$(PROJECT).elf
	openocd -f openocd.cfg -c "program $(BUILD)/$(PROJECT).elf verify reset exit"

clean:
	rm -rf $(BUILD)
