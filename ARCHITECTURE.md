# Architecture

## Project

**Brewie B20 BSP Modernization**

This document captures the known hardware architecture of the Brewie B20 and serves as the primary hardware reference for BSP development.

**Last Updated**: 2026-07-14

---

# Objectives

- Preserve the original hardware functionality
- Replace the vendor BSP with upstream software
- Create a maintainable Buildroot BSP
- Document every hardware component
- Record assumptions and unknowns

---

# System Overview

```
                     Brewie B20

            +------------------------
            |     Allwinner A13      |
            |      ARM Cortex-A8     |
            |                        |
            |   Linux / Buildroot    |
            |                        |
            +-----------+------------+
                        |
          +-------------+--------------+
          |             |              |
        RGB LCD      USB Host       UART
          |             |              |
     FT5x Touch      RTL8188EU     Debug Console
          |
       I²C Bus
          |
      PCF8563 RTC
```

---

# Software Architecture

## Current

```
U-Boot
↓
Linux 3.4 Vendor BSP
↓
script.bin
↓
BusyBox RootFS
↓
                 Brewie Application
        ┌────────────────────────────┐
        │         Qt5 GUI           │
        │    Framebuffer Display     │
        │    FT5x06 Touchscreen      │
        │    I²C RTC                 │
        │    USB WiFi                │
        └────────────────────────────┘
```

## Target

```
Mainline U-Boot
↓
Linux LTS (6.x)
↓
Device Tree
↓
Buildroot RootFS
↓
Brewie Application (or replacement)
```

---

# Processor

| Property | Value |
|----------|-------|
| SoC | Allwinner A13 (sun4i/sun5i) |
| CPU | ARM Cortex-A8 single-core |
| Architecture | ARMv7 |
| RAM | 512 MB DDR3 |
| CPU Clock | 1008 MHz |

---

# Boot Flow

- **ROM**: First stage bootloader in SoC
- **U-Boot**: Second stage bootloader on SD card
- **Kernel**: uImage on SD card partition 1
- **RootFS**: ext4 on mmcblk0p2

---

# Storage

## Boot Medium
- SD Card (eMMC controller)

## Partitions
| Partition | Size | Purpose |
|------------|------|----------|
| p1 | 16 MB | Boot (uImage, script.bin) |
| p2 | 7.5 GB | Root filesystem |

---

# Display

## Type
RGB Parallel TFT (MCU interface)

## Resolution
480 x 272 pixels

## Timing (from FEX, verified by fbset)
| Parameter | Value |
|-----------|-------|
| Pixel clock | 9.000 MHz |
| Horizontal total | 525 |
| Horizontal front porch | 10 |
| Horizontal back porch | 5 |
| Horizontal sync width | 30 |
| Vertical total | 576 |
| Vertical front porch | 3 |
| Vertical back porch | 8 |
| Vertical sync width | 5 |

## Pins
- Data: PD00-PD23 (RGB888, 24-bit)
- Clock: PD24
- DE: PD25
- HSync: PD26
- VSync: PD27

---

# Backlight

## Control
PWM on PB02 (PWM0, channel 0) + AXP209 GPIO1 for enable

## Configuration
- Channel: 0
- Frequency: 10000 Hz
- Polarity: Active high (PWM_POLARITY_INVERTED in DTS)
- Enable GPIO: AXP209 GPIO1 (`port:power1` in FEX maps to AXP GPIO1)
- Initial brightness: 5 (lcd0_backlight = 5)

## Alternative Configuration (from OlimexOrig.txt)
Some A13 boards use simple GPIO on PB3 (Linux GPIO 35) for backlight control:
- `echo 35 > /sys/class/gpio/export`
- `echo out > /sys/class/gpio/gpio35/direction`
- `echo 5 > /sys/class/gpio/gpio35/value` (5 = brightness level)

**Note**: The FEX configuration uses a hybrid approach combining PWM for brightness and AXP GPIO for power switching.

---

# Touchscreen

## Controller
FocalTech FT5x06

## Bus
I²C2 (PB17/PB18)

## Address
0x38 (primary), 0x14 and 0x5d (alternatives per OlimexOrig.txt)

## Interrupt
PG11 (falling edge, IRQ_TYPE_EDGE_FALLING)

## Reset
PC03 (active low, GPIO_ACTIVE_LOW)

---

# RTC

## Device
NXP PCF8563

## Bus
I²C0 (PB00/PB01) - shared with PMIC

## Address
0x51

**Note**: The FEX confirms `rtc_twi_id = 0` (I2C0) and `rtc_twi_addr = 81` (0x51). The user's i2cdetect output from an Olimex A13 board showed the RTC at 0x51 and ft5x06 at 0x38 on I2C2, matching our configuration.

---

# PMIC

## Detected
AXP209

## Address
I2C0 at 0x34 (`pmu_twi_id = 0`, `pmu_twi_addr = 52`)

## Connection
Shared with RTC on I2C0 bus. Both devices coexist on the same I2C bus.

---

# USB

## Host Ports
- EHCI0 + OHCI0: usbc0 (USB host)
- EHCI0/EHCI1: usbc1 (USB WiFi)

## WiFi
RTL8188EU via USB (usbc1)

---

# UART

## Console
UART1: PG03 (TX), PG04 (RX) at 115200n8

## Application UART
UART2: PG09 (TX), PG10 (RX)

---

# SPI

## SPI2 (enabled)
- CS: PE00
- SCLK: PE01
- MOSI: PE02
- MISO: PE03
- Mode: 3
- Max frequency: 1 MHz
- spidev configured

---

# Audio

## Codec
External codec (codec_para)
- Capture enabled
- Playback enabled

---

# GPIO

## Configured GPIOs (from gpio_para)

| Pin | Function | Pull | Level |
|-----|----------|------|-------|
| PB03 | Input | default | 0 |
| PB15 | Input | default | 0 |
| PB04 | Output | default | 1 |
| PB16 | Output | default | 0 |
| PB02 | Output | default | 1 (PWM0) |
| PE09 | Output | default | 1 |
| PB10 | Output | default | 1 |
| PC07 | Output | default | 1 |
| PG12 | Output | default | 0 |

## GPIO Initialization
- PB04: High (power LED?)
- PB10: High (LCD power enable)
- PC07: High (system status?)

---

# Migration Status

| Phase | Status |
|-------|--------|
| Firmware Preservation | ✅ |
| Hardware Discovery | ✅ |
| Hardware Documentation | ✅ |
| Device Tree Creation | ✅ |
| Mainline Kernel | ⏳ |
| LCD Bring-up | ⏳ |
| Touchscreen | ⏳ |
| Buildroot BSP | ⏳ |
| Bootable SD Image | ⏳ |

---

# Design Principles

1. Prefer upstream Linux over vendor BSPs.
2. Preserve original hardware behavior.
3. Automate repetitive engineering tasks.
4. Document every discovery.
5. Keep tooling generic and reusable.
6. Separate board-specific data from generic tooling.
7. Every engineering decision should be reproducible.

---

# Open Questions

- Which GPIOs are application specific?
- Which SPI device is attached?
- Does the LCD panel have an exact model match upstream?
- Any custom U-Boot board initialization needed?
- Verify AXP209 connection on I2C bus