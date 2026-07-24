#!/usr/bin/env python3
"""
Firmware Analyzer Plugin for ELF binaries.

Detects firmware update patterns and bootloader references from strings.

Usage:
    analyzer.register_plugin(FirmwareAnalyzer(reports_dir))
    # Or run standalone: python3 plugins/firmware_analyzer.py
"""

import re
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class FirmwareInfo:
    """Firmware update detection results."""
    update_strings: list[str] = field(default_factory=list)
    bootloader_refs: list[str] = field(default_factory=list)
    version_strings: list[str] = field(default_factory=list)
    download_urls: list[str] = field(default_factory=list)


class FirmwareAnalyzer:
    """Detect firmware-related patterns in ELF binaries.
    
    Looks for:
    - Firmware update strings (firmware, fw_update, ota_update)
    - Bootloader references (u-boot, SPL, fastboot, recovery)
    - Version identifiers (firmware version, build version)
    - Download URLs
    - OTA (over-the-air) update indicators
    
    Compatible with AnalyzerPlugin interface via duck typing.
    """
    
    OUTPUT_FILES = ["14-firmware.md", "firmware.json"]
    
    # More specific patterns for firmware detection
    FIRMWARE_PATTERNS = [
        r'firmware[_\s-]*update',  # firmware_update, firmware update
        r'fw[_\s-]*update',        # fw_update, fw update
        r'ota[_\s-]*update',        # ota_update, ota update
        r'flash[_\s-]*firmware',    # flash_firmware
        r'upgrade[_\s-]*firmware',  # firmware upgrade
        r'firmware[_\s-]*version', # firmware version
        r'build[_\s-]*version',   # build version
    ]
    
    BOOTLOADER_PATTERNS = [
        r'u[-\s]?boot',            # u-boot, uboot
        r'spl\s',                 # SPL bootloader (word boundary)
        r'/boot/',                 # boot partition paths
        r'bootloader',            # bootloader
        r'recovery[_\s]',        # recovery partition/command
    ]
    
    VERSION_PATTERNS = [
        r'version[_\s:]?\s*\d+\.\d+',
        r'build[_\s]?(v\d+|\d+)',
    ]
    
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.firmware_info = FirmwareInfo()
        self.name = "firmware-analyzer"
        self.output_files = self.OUTPUT_FILES
    
    def analyze(self, result: Optional[dict] = None, elf_path: Optional[Path] = None) -> FirmwareInfo:
        """Extract firmware-related patterns from strings."""
        strings_file = self.reports_dir / "10-strings.txt"
        if not strings_file.exists():
            return self.firmware_info
        
        content = strings_file.read_text()
        
        # Update/firmware strings
        for pattern in self.FIRMWARE_PATTERNS:
            matches = re.findall(pattern, content, re.I)
            self.firmware_info.update_strings.extend(matches)
        
        # URLs
        self.firmware_info.download_urls.extend(
            re.findall(r'https?://[^\s<>"\']+', content)
        )
        
        # Version strings
        self.firmware_info.version_strings.extend(
            re.findall(r'version\s*[:\\s]?\s*\d+\.\d+', content, re.I)
        )
        
        return self.firmware_info
    
    def generate_report(self) -> None:
        """Generate firmware analysis report."""
        report = f"""# Firmware Analysis

## Detected Update/Firmware Strings
Found {len(self.firmware_info.update_strings)} occurrences.
"""
        for s in sorted(set(self.firmware_info.update_strings))[:50]:
            report += f"- {s}\n"
        
        report += f"""
## URLs for Potential Downloads
Found {len(self.firmware_info.download_urls)} URLs.
"""
        for url in sorted(set(self.firmware_info.download_urls))[:30]:
            report += f"- {url}\n"
        
        report += f"""
## Version Strings
Found {len(self.firmware_info.version_strings)} version references.
"""
        for v in sorted(set(self.firmware_info.version_strings))[:20]:
            report += f"- {v}\n"
        
        output_path = self.reports_dir / "14-firmware.md"
        if not output_path.exists():
            output_path.write_text(report)
            logger.info(f"Generated {output_path}")
        else:
            logger.info(f"Skipping {output_path} (exists)")
        
        json_path = self.reports_dir / "firmware.json"
        if not json_path.exists():
            json_path.write_text(json.dumps({
                "update_strings": self.firmware_info.update_strings,
                "download_urls": self.firmware_info.download_urls,
                "version_strings": self.firmware_info.version_strings,
            }, indent=2))


def main() -> None:
    """Run standalone firmware analysis."""
    logging.basicConfig(level=logging.INFO)
    
    reports_dir = Path(__file__).parent.parent.parent / "reports"
    
    analyzer = FirmwareAnalyzer(reports_dir)
    analyzer.analyze()
    analyzer.generate_report()


if __name__ == "__main__":
    main()