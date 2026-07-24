#!/usr/bin/env python3
"""
Resource Analyzer Plugin for ELF binaries.

Detects embedded resources (images, UI files, database files) from strings.

Usage:
    analyzer.register_plugin(ResourceAnalyzer(reports_dir))
    # Or run standalone: python3 plugins/resource_analyzer.py
"""

import re
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ResourceInfo:
    """Extracted resource information."""
    images: list[str] = field(default_factory=list)
    qml_files: list[str] = field(default_factory=list)
    ui_files: list[str] = field(default_factory=list)
    database_files: list[str] = field(default_factory=list)


class ResourceAnalyzer:
    """Extract embedded resources from ELF strings.
    
    This plugin looks for embedded resource file references in the binary.
    Compatible with the AnalyzerPlugin interface (duck typing).
    """
    
    OUTPUT_FILES = ["13-resources.md", "resources.json"]
    
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.resource_info = ResourceInfo()
        # Provide plugin interface for compatibility
        self.name = "resource-analyzer"
        self.output_files = self.OUTPUT_FILES
    
    def analyze(self, result: Optional[dict] = None, elf_path: Optional[Path] = None) -> Optional[ResourceInfo]:
        """Extract resource information from strings."""
        strings_file = self.reports_dir / "10-strings.txt"
        if not strings_file.exists():
            logger.warning("Strings file not found")
            return None
        
        content = strings_file.read_text()
        
        # Image files - match full filenames with extensions (may have " prefix)
        self.resource_info.images.extend(re.findall(r'([\w-]+\.(?:png|jpg|jpeg|svg|gif|bmp))', content, re.I))
        
        # QML files
        self.resource_info.qml_files.extend(re.findall(r'([\w-]+\.qml)', content, re.I))
        
        # UI files
        self.resource_info.ui_files.extend(re.findall(r'([\w-]+\.ui)', content, re.I))
        
        # Database files
        self.resource_info.database_files.extend(re.findall(r'([\w-]+\.(?:db|sqlite|sqlite3))', content, re.I))
        
        logger.info(f"Found {len(self.resource_info.images)} images, "
                   f"{len(self.resource_info.qml_files)} QML files")
        return self.resource_info
    
    def generate_report(self) -> None:
        """Generate resource analysis report."""
        report = f"""# Resource Analysis

## Images
Found {len(self.resource_info.images)} image references.
"""
        for img in sorted(set(self.resource_info.images))[:30]:
            report += f"- {img}\n"
        
        report += f"""
## QML Files
Found {len(self.resource_info.qml_files)} QML file references.
"""
        for qml in sorted(set(self.resource_info.qml_files))[:30]:
            report += f"- {qml}\n"
        
        report += f"""
## UI Files
Found {len(self.resource_info.ui_files)} UI file references.
"""
        for ui in sorted(set(self.resource_info.ui_files))[:30]:
            report += f"- {ui}\n"
        
        report += f"""
## Database Files
Found {len(self.resource_info.database_files)} database references.
"""
        for db in sorted(set(self.resource_info.database_files))[:30]:
            report += f"- {db}\n"
        
        output_path = self.reports_dir / "13-resources.md"
        if not output_path.exists():
            output_path.write_text(report)
            logger.info(f"Generated {output_path}")
        else:
            logger.info(f"Skipping {output_path} (exists)")
        
        json_path = self.reports_dir / "resources.json"
        if not json_path.exists():
            json_path.write_text(json.dumps({
                "images": self.resource_info.images,
                "qml_files": self.resource_info.qml_files,
                "ui_files": self.resource_info.ui_files,
                "database_files": self.resource_info.database_files,
            }, indent=2))


def main() -> None:
    """Run standalone resource analysis."""
    logging.basicConfig(level=logging.INFO)
    
    reports_dir = Path(__file__).parent.parent.parent / "reports"
    
    analyzer = ResourceAnalyzer(reports_dir)
    analyzer.analyze()
    analyzer.generate_report()


if __name__ == "__main__":
    main()