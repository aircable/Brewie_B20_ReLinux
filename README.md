# ReLinux: Brewie B20 BSP Migration

A Buildroot-based Linux BSP migration project for the Brewie B20 (Allwinner A13) from legacy vendor BSP to modern upstream Linux.

## Project Overview

This repository documents the complete workflow of migrating a legacy embedded Linux system to modern mainline kernel support. The Brewie B20 uses an Allwinner A13 SoC and legacy FEX configuration.

## Repository Structure

```
├── board/
│   └── brewie/
│       ├── sun5i-brewie.dts      # Main device tree (mainline)
├── configs/
│   └── brewie_b20_defconfig      # Buildroot configuration
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
  - board/brewie/B20/rootfs-overlay/.gitkeep is only there so the overlay path exists in git; it is not a meaningful runtime file.


## Quick Start

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
cp configs/brewie_b20_defconfig configs/
make brewie_b20_defconfig
make
```

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
