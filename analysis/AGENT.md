# AGENT.md

# Embedded ELF Analysis Toolkit

## Purpose

This repository develops reusable tooling for analyzing embedded Linux ELF executables.

The initial target is the BrewieApplication (Qt5 ARM executable), but the tooling should work with any ELF executable generated for embedded Linux.

The project is NOT a reverse engineering project.

The goal is to document the executable, discover its architecture, dependencies and build requirements.

Whenever possible, automate the analysis.

---

# Current Repository

Already available

- fish_env
- BrewieApplication
- previously generated reports

The Buildroot cross toolchain has already been built.

The environment file

    fish_env

contains TOOLPREFIX.

Always source it before executing external tools.

---

# Engineering Goals

Primary

✔ Generate complete ELF reports

✔ Recover Qt architecture

✔ Recover DWARF information

✔ Recover source tree

✔ Recover dependency graph

✔ Generate Buildroot package recommendations

Secondary

Generate Ghidra automation.

---

# Analysis Order

Always follow this order.

1.

ELF Header

↓

2.

Sections

↓

3.

Dynamic Libraries

↓

4.

Debug Information

↓

5.

Symbols

↓

6.

Source Files

↓

7.

Qt Analysis

↓

8.

Serial / Network Analysis

↓

9.

Resources

↓

10.

Ghidra

Do not begin Ghidra analysis before the ELF reports are complete.

---

# Scripts

Create

scripts/

elf-report.py

qt-report.py

ghidra-report.py

Do not create shell scripts unless they simply wrap Python.

Python is preferred.

---

# Reports

Generated reports belong in

reports/

Every report should be both

Markdown

and

JSON

whenever practical.

---

# Ghidra

Ghidra is installed.

Prefer using

analyzeHeadless

instead of GUI automation.

Headless analysis should be reproducible.

Generate reusable scripts.

Do not require manual clicking.

---

# Coding Standards

Python 3.11+

argparse

pathlib

dataclasses

logging

typing

subprocess

Avoid third-party modules.

---

# Repository Philosophy

Everything should be generic.

Avoid Brewie-specific assumptions.

Support

ARM

ARM64

x86

MIPS

PowerPC

when practical.

---

# Deliverables

The repository should eventually be capable of producing

• ELF summary

• dependency graph

• class hierarchy

• source tree

• Qt module report

• Buildroot package recommendations

• Ghidra project

• UML diagrams

from a single executable.

