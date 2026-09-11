# ReLinux: Brewie B20 BSP Migration

A Buildroot-based Linux BSP migration project for the Brewie B20 (Allwinner A13) from legacy vendor BSP to modern upstream Linux.

## Project Overview

This repository documents the complete workflow of migrating a legacy embedded Linux system to modern mainline kernel support. The Brewie B20 uses an Allwinner A13 SoC and legacy FEX configuration.

## Presentation and Lecture

I teach Embedded Linux Design at UCSC Extensions and use this an example of Device Tree and Board Support Package Engineering. This is a target for teaching since the A13-SOM sits in a sweet spot: it's old enough that students can understand the entire boot process, but modern enough to run Buildroot and even mainline Linux. This would make an excellent course example because it shows how to create a custom board support package rather than relying on a standard Raspberry Pi configuration. This is what embedded Linux engineers actually do in industry. Buildroot, Yocto, Device Trees, and bootloaders become tools in a larger workflow.

[Embedded Linux Course Description](https://www.ucsc-extension.edu/courses/embedded-linux-design-and-programming)
[BSP-Engineering Presentation](https://docs.google.com/presentation/d/1sq7ynd03yNYqLOmTWfzNwtD_2XBLVE_6/edit?usp=sharing&ouid=102670391106971867939&rtpof=true&sd=true)

### Because you have a working machine, we can proceed methodically:

- Extract everything from the original firmware.
- Identify every peripheral (LCD, touch, EEPROM, GPIOs, etc.).
- Create a modern Buildroot board support package.
- Boot a current mainline Linux kernel.
- Incrementally enable each peripheral until the Brewie hardware is fully functional.

That mirrors what an embedded Linux engineer does when bringing up a new board.

There are probably very few Brewie machines left in use, and I doubt anyone has ever ported them to a current mainline Linux kernel. By documenting the hardware and replacing the aging 2016 software stack with a modern Buildroot-based system, you'd not only have a great teaching example but also preserve an interesting piece of embedded hardware.

## Repository Structure

Note: we do not publish either buildroot or the kernel code here, just the files added to the build environment to get you going.

```
├── board/
│   └── brewie/
│       ├── sun5i-brewie.dts      # Main device tree (mainline)
├── configs/
│   └── brewie_b20_defconfig      # Buildroot configuration
├── package/
│   └── avrdude/                  # Brewie native-UART fixes
├── patches/
│   └── buildroot/                # Changes to upstream Buildroot files
├── scripts/
│   ├── fex-report.py             # FEX analysis tool
│   ├── fex2dts.py                # FEX to DTS converter
│   └── report.md                 # Hardware analysis report
├── SDcard/                       # Recovered boot partition from the original Linux
├── ARCHITECTURE.md               # Hardware architecture documentation
├── DISCOVERY.md                  # Hardware discovery notes
├── PLAN.md                       # Project milestones and status
├── AGENT.md                      # Engineering guidelines
└── several text files with discovery commands and logs
```

## Files in this repo, what matters

  - brewie_b20_defconfig selects kernel, U-Boot, ext4 rootfs, and the genimage flow.
  - sun5i-brewie.dts is the board hardware description.
  - genimage.cfg defines sdcard.img.
  - post-image.sh runs genimage.
  - The root README now identifies the repo as the Brewie BSP toolkit instead of only generic Buildroot.
  - board/brewie/B20/rootfs-overlay contains board initialization, networking,
    AVR maintenance, Qt display diagnostics, and generic BrewieNext web,
    backend, kiosk, and release-installation services.
  - brewie_b20_defconfig includes Python 3, Flask, Flask-CORS, PyYAML, and
    jsonschema for the BrewieNext runtime API.
  - package/avrdude contains additional Buildroot package patches for reliable
    programming through the B20 native UART.
  - patches/buildroot contains changes that must be applied to upstream
    Buildroot source, including the QtWebKit qmake metadata fix.


## Quick Start

### Current SD image release

ReLinux v0.8.0 is built with Buildroot 2026.02 and Linux 6.6.156.  Its 14 GiB
root filesystem is sized to fit nominal 16 GB or larger SD cards.  It includes
persistent kernel crash capture, periodic memory diagnostics, and memtester.

To write the compressed release image on Linux (replace `/dev/sdX` with the
whole SD-card device, not a partition):

```bash
xzcat BrewieNext-ReLinux-v0.8.0-sdcard.img.xz | sudo dd of=/dev/sdX bs=4M status=progress conv=fsync
```

Verify the downloaded archive against the accompanying SHA-256 file before
flashing.  Selecting the wrong output device will overwrite it.

### Analysis
The analysis of the original 2014 Linux is already done. But the tools used are published here for similar projects.
```bash
cd scripts
python3 fex-report.py SDcard/script.fex
python3 fex2dts.py SDcard/script.fex > board/brewie/sun5i-brewie.dts
```

### Buildroot Integration
```bash
# In buildroot directory
cp -a /path/to/legacy-bsp-toolkit/board/brewie board/
cp /path/to/legacy-bsp-toolkit/configs/brewie_b20_defconfig configs/
cp /path/to/legacy-bsp-toolkit/package/avrdude/*.patch package/avrdude/
git apply /path/to/legacy-bsp-toolkit/patches/buildroot/qt5webkit-qmake-metadata.patch
make brewie_b20_defconfig
make -j4
```

Before building, edit
`board/brewie/B20/rootfs-overlay/etc/wpa_supplicant.conf` and replace the
placeholder network credentials. Do not commit real Wi-Fi credentials.

## Hardware Summary

| Component | Details |
|-----------|---------|
| SoC | Allwinner A13 (sun5i), ARM Cortex-A8 |
| RAM | 512 MB DDR3 |
| PMIC | AXP209 |
| LCD | 480x272 RGB parallel |
| Touch | ft5x06 (I2C) |
| RTC | PCF8563 (I2C) |
| UART | UART1 console (115200n8) |

## Milestones

- [x] FEX recovery and analysis
- [x] Device tree generation
- [x] Hardware detection (I2C devices)
- [x] Kernel compilation (Buildroot)
- [ ] Hardware testing

## License

Documentation: CC-BY-SA 4.0
Scripts: MIT
Device Tree: GPL-2.0
