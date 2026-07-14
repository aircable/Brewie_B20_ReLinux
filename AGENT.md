# AGENT.md

## Project Overview

This repository documents the migration of a legacy embedded Linux system to a modern, maintainable Linux BSP.

The initial target is the Brewie B20 brewing machine based on the Allwinner A13 (sun5i), but the tools developed here should be generic enough to support other embedded Linux devices using legacy vendor BSPs.

The project is intended to serve both as:

- an educational example for an Embedded Linux course
- a reusable BSP migration toolkit

---

# Project Goals

1. Preserve the original firmware and hardware description.
2. Document the hardware platform.
3. Convert legacy Allwinner FEX files into modern Linux Device Trees.
4. Create a Buildroot board support package.
5. Boot a modern mainline Linux kernel.
6. Produce a bootable SD card image.
7. Document every engineering step.

The emphasis is on understanding and documenting the board support package rather than simply compiling Linux.

---

# Current Hardware

Target Board

- Brewie B20
- Allwinner A13 (sun5i)
- 512 MB RAM
- SD card boot
- U-Boot
- Linux 3.4 vendor BSP
- Buildroot 2014

Recovered Hardware

- script.bin
- script.fex
- boot.scr
- uEnv.txt
- uImage

Known Peripherals

- 480x272 RGB LCD
- FT5x06 touchscreen (I2C)
- PCF8563 RTC
- RTL8188EU USB WiFi
- UART console
- PWM backlight

---

# Repository Structure

docs/
    Documentation

scripts/
    Generic BSP extraction and analysis tools

board/
    Buildroot board support package

kernel/
    Linux kernel related files

u-boot/
    U-Boot patches or configuration

original/
    Original firmware artifacts

examples/
    Example outputs

---

# Engineering Philosophy

Whenever possible:

- automate repetitive work
- avoid manual editing
- generate reports
- preserve original information
- document assumptions

Every script should work for more than one board.

Avoid hardcoding Brewie-specific values unless absolutely necessary.

---

# Tooling Roadmap

The repository will eventually contain:

extract.sh

Copies firmware artifacts from the original storage.

Already implemented.

---

fex-report.py

Reads a script.fex file.

Produces:

- hardware summary
- peripherals
- GPIO assignments
- display timings
- clocks
- buses
- warnings

Output:

Markdown
JSON

---

fex2dts.py

Converts common FEX sections into a first-pass Device Tree.

Goal:

Generate approximately 70–80% of a DTS automatically.

---

compare.py

Compares

script.fex

against

existing DTS

Reports

missing nodes
GPIO mismatches
unsupported peripherals

---

build-image.sh

Creates a bootable SD card image.

---

# Coding Guidelines

Python

- Python 3.11+
- dataclasses
- pathlib
- argparse
- type hints
- logging

Avoid external dependencies whenever practical.

Scripts should run on Ubuntu without additional packages.

---

# Documentation

Every major engineering decision should be documented.

Assume readers are learning Embedded Linux.

Explain why each step exists.

---

# Definition of Success

A complete Buildroot BSP capable of producing a bootable SD card image for the Brewie B20 using:

- Mainline Linux
- Mainline U-Boot
- Device Tree
- Buildroot

without relying on vendor BSP code.

## Discovery Philosophy

Do not immediately attempt to build a new Linux image.

First preserve and document the original system.

Preferred order:

1. Image the storage device
2. Extract boot artifacts
3. Recover hardware description (DTB/FEX)
4. Document hardware
5. Compare against upstream support
6. Create Device Tree
7. Boot a modern kernel
8. Build Buildroot BSP

The repository prioritizes reproducible engineering over trial-and-error.

# GitHub Workflow

Repository: legacy-bsp-toolkit

Description: Toolkit and methodology for migrating legacy embedded Linux BSPs to modern Buildroot and upstream Linux.

Topics:
embedded-linux
buildroot
yocto
device-tree
linux-kernel
u-boot
allwinner
sunxi
bsp
embedded
bootloader
arm
armv7
fex
legacy
reverse-engineering

## Branch Strategy

main
    Stable and documented milestones.

develop
    Integration branch for completed features.

feature/<name>
    Individual development branches.

Examples

feature/fex-report

feature/fex2dts

feature/compare

feature/buildroot-bsp

feature/device-tree

feature/kernel-boot

# Commit Message Style

Use concise, engineering-focused commit messages.

Format

<type>: <summary>

Examples

feat: add FEX parser

feat: generate initial Device Tree

feat: build first bootable kernel

docs: document LCD timing

docs: update architecture diagram

fix: correct GPIO translation

refactor: separate DTS generator

test: verify framebuffer initialization

Avoid

"misc"

"changes"

"update"

Every commit should describe a measurable engineering milestone.

# Pull Requests

Each Pull Request should answer:

## Objective

What engineering problem is being solved?

## Input

Which firmware artifacts or hardware information are used?

## Output

What new capability does this add?

## Validation

How was it verified?

Examples

Kernel boots

Framebuffer works

Touchscreen detected

Generated DTS compiles

Buildroot image boots

# Repository Documentation

README.md

Project overview.

AGENT.md

Instructions for AI agents and contributors.

PLAN.md

Engineering roadmap.

ARCHITECTURE.md

Hardware documentation.

DISCOVERY.md

Engineering notebook.

CHANGELOG.md

Major milestones.

docs/

Supporting documentation.

scripts/

Engineering tools.

board/

Buildroot BSP.

original/

Recovered firmware.

examples/

Example reports.

# Issue Labels

documentation

device-tree

kernel

u-boot

buildroot

tooling

hardware

good first issue

enhancement

bug

question

# Milestones

M1 Firmware Recovery

M2 Hardware Discovery

M3 Device Tree

M4 Mainline Kernel Boot

M5 LCD Bring-up

M6 Touchscreen

M7 Buildroot BSP

M8 Bootable SD Card

M9 Documentation Complete

# Releases

v0.1

Firmware recovered.

v0.2

Hardware fully documented.

v0.3

Device Tree generated.

v0.4

Mainline kernel boots.

v0.5

LCD operational.

v0.6

Touchscreen operational.

v0.7

Buildroot BSP complete.

v1.0

Bootable SD image.


