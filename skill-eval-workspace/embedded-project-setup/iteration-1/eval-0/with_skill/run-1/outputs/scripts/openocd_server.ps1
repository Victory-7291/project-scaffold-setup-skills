$ErrorActionPreference = "Stop"

openocd `
  -f "interface/stlink.cfg" `
  -f "target/stm32g0x.cfg"
