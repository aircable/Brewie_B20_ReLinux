#!/usr/bin/env python3
"""
ELF Analysis Plugins Package.

This package provides modular analyzers that can be registered with the main
ELFAnalyzer for extensible analysis capabilities.

Available Plugins:
- ResourceAnalyzer: Extracts embedded resources from strings
- FirmwareAnalyzer: Detects firmware update patterns
- DatabaseAnalyzer: Identifies database/file references

Plugin Architecture:
------------------
Plugins implement the AnalyzerPlugin interface and can be dynamically loaded.
Each plugin declares its output files and can skip regeneration if reports exist.

Example usage:
```python
from scripts.plugins import ResourceAnalyzer, FirmwareAnalyzer, DatabaseAnalyzer

analyzer = ELFAnalyzer(elf_path, reports_dir)
analyzer.register_plugin(ResourceAnalyzer(reports_dir))
analyzer.register_plugin(FirmwareAnalyzer(reports_dir))
analyzer.register_plugin(DatabaseAnalyzer(reports_dir))
analyzer.run_all()
```
"""

from .resource_analyzer import ResourceAnalyzer
from .firmware_analyzer import FirmwareAnalyzer
from .database_analyzer import DatabaseAnalyzer

__all__ = [
    "ResourceAnalyzer",
    "FirmwareAnalyzer",
    "DatabaseAnalyzer",
]