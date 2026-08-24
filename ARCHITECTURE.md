# Architecture

## Project

**Brewie B20 BSP Modernization**

This document captures the known hardware architecture of the Brewie B20 and serves as the primary hardware reference for BSP development.

**Last Updated**: 2026-07-27

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

## Verified current BSP

```
U-Boot 2026.01
↓
Linux 6.6.27
↓
Device Tree
↓
Buildroot root filesystem
↓
Board services and hardware tests
        ┌────────────────────────────┐
        │ DRM/fbdev LCD + Qt5 test   │
        │ FT5x06 touchscreen         │
        │ PCF8563 RTC                │
        │ USB WiFi                   │
        │ GPIO power key/LEDs        │
        └────────────────────────────┘
```

The LCD, backlight, touchscreen, RTC, USB host, WiFi, power key, AVR UART, and
bootable SD-card image have been verified on the hardware.  The original B20
AVR command protocol and valve operation were also verified.  Final Brewie
application integration remains to be tested.

## Boot and power control

- The power button is PB3 / GPIO35.  It is described by the Device Tree as a
  `gpio-keys` input generating `KEY_POWER`.
- The hardware requires the button to be held during startup.  Release it
  after the board's power indication appears.
- PC7 / GPIO71 was investigated as a possible software power-hold signal.
  A Device Tree GPIO hog on that pin prevented Linux from booting, so it is
  intentionally left unclaimed.  The hardware latch, not Linux, maintains
  power after startup.
- PB4 / GPIO36 is the power LED.  `S01brewie-init` drives it high after Linux
  has booted, providing the normal boot indication.
- The same init script configures the known board controls: PB16 / GPIO48
  drain LED low, PG12 / GPIO204 USB control low, and PE9 / GPIO137 high to
  release the AVR reset line.

## AVR controller

The AVR controller is connected to UART3, exposed by Linux as `/dev/ttyS1`,
using 115200 8N1.  The B20 command frame is:

```text
$ <sequence> <payload-length> <ASCII-payload> <CRC-8> *
```

The original B20 CRC is calculated over the ASCII payload using CRC-8
polynomial `0x5e`. ReBrewie preserves the checksum byte for compatibility but
does not validate it. For example, the MeshIn valve commands are `P112` (open)
and `P113` (close). Transport diagnostics are documented in `AVR_commands.md`;
the canonical command reference is maintained in the ReBrewieAVR repository.

The image includes avrdude 8.1 using the `wiring` programmer and the
ATmega2560 part definition.  `/usr/bin/brewie-upload-fw` resets the AVR via
GPIO137 and supports both safe flash read-back and firmware upload:

```sh
brewie-upload-fw read /tmp/b20-existing.hex
brewie-upload-fw write /tmp/firmware.hex
```

The read operation does not erase or write flash.  The ReBrewieAVR source
currently selects B20 Plus definitions by default, so it must not be flashed
to B20 hardware until its pin mapping and actuator behavior have been
validated.

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
RGB parallel TFT driven by the A13 display engine and TCON

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

## Verified Linux path

The upstream display stack is `sun4i-drm`, with the display connector exposed
as `/sys/class/drm/card1-Unknown-1`.  DRM fbdev emulation creates `/dev/fb0`.
The board test `/usr/bin/qt-screen-test` runs the Qt5 QML test fullscreen on
that framebuffer and was verified to display six colored squares.

The non-Qt test `/etc/init.d/S70display-test` writes color bars directly to
`/dev/fb0` and sets the backlight.  The backlight can be tested manually with:

    echo 9 > /sys/class/backlight/backlight/brightness

---

# Backlight

## Control
PWM0 on PB02 / GPIO34, with PB10 / GPIO42 as the active-high panel-enable
GPIO.  The enable GPIO is owned by the `pwm-backlight` driver.

## Configuration
- Channel: 0
- PWM period: 9000 ns, as described in the Device Tree
- Brightness levels: 0 through 10
- Observed hardware behavior: 0 and 10 are off; values 1 through 9 turn the
  backlight on.  `echo 9 .../brightness` is the known working setting.

---

# Touchscreen

## Controller
EDT FT5x06-compatible capacitive touch controller

## Bus
I²C2 (PB17/PB18), address 0x38

## Interrupt
PG11 (falling edge, IRQ_TYPE_EDGE_FALLING)

## Reset
PC03 (active low, GPIO_ACTIVE_LOW)

The Device Tree binding is `edt,edt-ft5x06`.  Touch input was verified with
`evtest`; Linux creates an input device and reports touch events.

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
UART1: PG03 (TX), PG04 (RX) at 115200n8, exposed as the boot console.

## Application UART
UART3: PG09 (TX), PG10 (RX), enabled in the Device Tree for the AVR link.
The AVR UART, command acknowledgement, status stream, and firmware upload path
have been validated on the B20 hardware.

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

The legacy beeper/audio path was investigated but was not included in the
current Buildroot image.  It is not required for system operation; the power
LED provides the boot indication.

---

# GPIO

## Configured GPIOs (verified board mapping)

| Pin | Function | Pull | Level |
|-----|----------|------|-------|
| PB03 / GPIO35 | Power button input, `KEY_POWER` | default | active high |
| PB15 / GPIO47 | Drain button input | default | input |
| PB04 / GPIO36 | Power LED | default | high after init |
| PB16 / GPIO48 | Drain LED | default | low after init |
| PB02 / GPIO34 | LCD PWM0 | PWM peripheral | backlight |
| PB10 / GPIO42 | LCD enable | output, driver-owned | high when enabled |
| PE09 / GPIO137 | AVR reset release | output | high after init |
| PC07 / GPIO71 | Candidate power hold | intentionally unclaimed | hardware-controlled |
| PG12 / GPIO204 | USB control | output | low after init |

## GPIO Initialization
- PB04: High after `S01brewie-init` (power LED)
- PB10: Controlled by `pwm-backlight` (LCD enable)
- PC07: Not claimed; a DT GPIO hog caused a boot failure

---

# Migration Status

| Phase | Status |
|-------|--------|
| Firmware Preservation | ✅ |
| Hardware Discovery | ✅ |
| Hardware Documentation | ✅ |
| Device Tree Creation | ✅ |
| Mainline Kernel | ✅ |
| LCD/DRM and Qt5 test | ✅ |
| Touchscreen and evtest | ✅ |
| Buildroot BSP | ✅ |
| Bootable SD Image | ✅ |
| AVR UART protocol | ✅ |

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

- Validate the AVR UART protocol and application-level serial exchange.
- Which SPI device is attached?
