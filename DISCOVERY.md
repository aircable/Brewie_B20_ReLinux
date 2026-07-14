# Discovery Log - Brewie B20 Migration

## Hardware Identification

### SoC Platform
- Architecture: ARM (ARMv7-A)
- Platform: Allwinner A13 (sun5i) - single-core Cortex-A8
- Core: ARM Cortex-A8 single-core
- Clock: 1008 MHz CPU (from FEX target/boot_clock)

### Board Model
- Model: A13-EVB-V1.0 (from script.fex [product] section)
- 512 MB RAM (from dram parameters)
- NAND flash present (from nand_para)

### PMIC
- AXP209 detected from voltage settings:
  - dcdc2_vol = 1400 (core voltage)
  - dcdc3_vol = 1200 (DDR voltage)
  - ldo2_vol = 3000 (AVCC)
  - ldo3_vol = 3300 (DC5V)
  - ldo4_vol = 3300 (DC3V3)

## Peripherals Discovered via FEX Analysis

### Memory
- DRAM: 408 MHz, 16-bit I/O width, 16-bit bus width, 512 MB size
- Type: DDR3 (dram_type=3)

### Storage
- MMC/SD: eMMC on PF00-PF05 (card_boot0_para, mmc0_para, 4-bit bus)
- NAND Flash: PC00-PC15 with NAND controller (nand_used=1)

### Display
- LCD: 480x272 resolution, 9 MHz pixel clock
- Timing: HT=525, HBP=40, HSPW=30, VT=576, VBP=8, VSPW=5
- Backlight PWM on PB02 (channel 0, 10000 Hz, active high)
- Backlight enable: AXP209 GPIO1 (from FEX: `lcd_bl_en = port:power1`)
- Data bus: PD00-PD27 (24-bit RGB666)
- Framebuffer: U:480x272p-59 mode confirmed from dmesg

### Touch
- CTP: ft5x_ts on I2C bus 2, address 0x38
- Screen: 480x272
- Interrupt: PG11 (function 6 - input)
- Reset: PC03 (function 1 - output, active low)

### USB
- 2 USB host ports (usbc0, usbc1)
- USB WiFi via usbc1

### Audio
- I2S audio with capture and playback enabled
- External codec (not SoC internal)

### Debug Console
- UART1: PG03 (TX), PG04 (RX), 115200n8
- Also UART2 on PG09/PG10 (application UART)

### I2C Buses
- TWI0: PB00/PB01 (RTC pcf8563 at addr 0x51)
- TWI1: PB15/PB16 (disabled)
- TWI2: PB17/PB18 (CTP, CSI camera)

### SPI Buses
- SPI1: Disabled
- SPI2: PE00-PE03 (spidev, mode 3, 1MHz max)

### GPIO
- 9 GPIO pins configured in gpio_para
- Several power control pins (power1, power3)
- GPIO 3, 7, 8 initialized high at boot

## Backlight Control Methods

Two configurations discovered:

1. **FEX Configuration** (script.fex):
   - PWM channel 0 on PB02 (10kHz, active high)
   - Backlight enable via AXP209 GPIO1 (`power1` in FEX)

2. **Olimex Reference** (OlimexOrig.txt):
   - Simple GPIO control on PB3 (Linux GPIO 35)
   - Command: `echo 35 > /sys/class/gpio/export`
   - Command: `echo out > /sys/class/gpio/gpio35/direction`
   - Command: `echo 5 > /sys/class/gpio/gpio35/value` (5 = brightness level)
   - Note: This suggests the LCD panel may use simple GPIO backlight instead of PWM
   - The FEX uses a hybrid approach: PWM for brightness + AXP GPIO for enable

## Touch Panel Address Variants

Per OlimexOrig.txt, the ft5x06 touch panel can use two I2C addresses:
- 0x38 (standard, decimal 56 as in FEX)
- 0x14 (alternative)
- 0x5d (alternative)

The default in our FEX is 0x38. If touch is not detected, try 0x14.

## Boot Configuration
- Boot from SD/MMC card (card_boot section)
- Logical start sector: 40960 (0x0A000)

## LCD Timing Analysis (from fbset)

```
mode "480x272-60"
    # D: 9.000 MHz, H: 17.143 kHz, V: 59.524 Hz
    geometry 480 272 480 544 32
    timings 111111 10 5 3 8 30 5
    rgba 8/16,8/8,8/0,8/24
endmode
```

From FEX lcd0_para:
- lcd_x = 480, lcd_y = 272
- lcd_ht = 525 (horizontal total)
- lcd_hbp = 40 (horizontal back porch)
- lcd_hv_hspw = 30 (horizontal sync pulse width)
- lcd_vt = 576 (vertical total)
- lcd_vbp = 8 (vertical back porch)
- lcd_hv_vspw = 5 (vertical sync pulse width)

The fbset timings (hfp=10, hbp=5, vfp=3, vbp=8, hspw=30, vspw=5) are verified correct and match the running system.

## Upstream DTS Comparison

Recommended base: sun5i-a13-q8-tablet.dts
- Similar tablet form factor
- LCD panel support (480x272 common)
- I2C touchscreens supported
- USB host support
- AXP209 PMIC support available in sunxi-common-regulators.dtsi

## Generated Files

- scripts/fex-report.py - FEX parsing and reporting tool
- scripts/fex2dts.py - FEX to Device Tree converter
- board/brewie/sun5i-brewie.dts - Generated Device Tree

Last updated: 2026-07-13