# ReLinux: Brewie B20 BSP Migration

A Buildroot-based Linux BSP migration project for the Brewie B20 (Allwinner A13) from legacy vendor BSP to modern upstream Linux.

## Project Overview

This repository documents the complete workflow of migrating a legacy embedded Linux system to modern mainline kernel support. The Brewie B20 uses an Allwinner A13 SoC and legacy FEX configuration.

## Repository Structure

```
├── board/
│   └── brewie/
│       ├── sun5i-brewie.dts      # Main device tree (mainline)
│       └── sun5i-brewie.dtb      # Compiled device tree
├── configs/
│   └── brewie_b20_defconfig      # Buildroot configuration
├── include/
│   ├── allwinner/                 # Upstream Allwinner DTSI files
│   └── dt-bindings/              # Device tree binding headers
├── scripts/
│   ├── fex-report.py             # FEX analysis tool
│   ├── fex2dts.py                # FEX to DTS converter
│   └── report.md                 # Hardware analysis report
├── SDcard/                       # Recovered firmware artifacts
├── ARCHITECTURE.md               # Hardware architecture documentation
├── DISCOVERY.md                  # Hardware discovery notes
├── PLAN.md                       # Project milestones and status
└── AGENT.md                      # Engineering guidelines
```

## Quick Start

### Analysis
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
- [ ] Kernel compilation (Buildroot)
- [ ] QEMU validation
- [ ] Hardware testing

## License

Documentation: CC-BY-SA 4.0
Scripts: MIT
Device Tree: GPL-2.0
