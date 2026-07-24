#!/usr/bin/env python3
"""
Qt-specific analysis plugin for ELF binaries.

This tool extracts Qt module dependencies, QML types, and QObject subclass information
from existing ELF analysis reports. It can be run standalone or as part of the
elf-report.py analysis pipeline.

Usage:
    python3 qt-report.py --reports-dir /path/to/reports
    
Output:
    - reports/09-qt.md (Markdown report)
    - reports/qt-analysis.json (JSON structured data)
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class QtAnalysis:
    """Qt analysis results."""
    version: str = "5"
    modules: list[str] = field(default_factory=list)
    qml_types: list[str] = field(default_factory=list)
    qobject_classes: list[str] = field(default_factory=list)
    metatypes: list[str] = field(default_factory=list)
    plugins: list[str] = field(default_factory=list)


class QtAnalyzer:
    """Extract Qt-specific information from ELF analysis results."""
    
    QT_MODULES = [
        "Qt5Core", "Qt5Gui", "Qt5Widgets", "Qt5Network", "Qt5SerialPort",
        "Qt5Xml", "Qt5Concurrent", "Qt5Quick", "Qt5Qml", "Qt5Charts",
        "Qt5Svg", "Qt5Sql", "Qt5Bluetooth", "Qt5Multimedia", "Qt5WebEngine",
        "Qt5OpenGL", "Qt5PrintSupport", "Qt5Help", "Qt5Test",
    ]
    
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.analysis = QtAnalysis()

    def analyze_dynamic(self) -> None:
        """Extract Qt modules from dynamic section."""
        dyn_file = self.reports_dir / "05-dynamic.txt"
        if not dyn_file.exists():
            logger.warning("Dynamic section report not found: 05-dynamic.txt")
            return

        content = dyn_file.read_text()
        
        for module in self.QT_MODULES:
            if module in content:
                clean_name = module.replace("Qt5", "Qt5 ")
                if clean_name not in self.analysis.modules:
                    self.analysis.modules.append(clean_name)

        logger.info(f"Found Qt modules: {self.analysis.modules}")

    def analyze_symbols(self) -> None:
        """Extract Qt classes from symbol table."""
        sym_file = self.reports_dir / "04-symbols.txt"
        if not sym_file.exists():
            logger.warning("Symbols report not found: 04-symbols.txt")
            return

        content = sym_file.read_text()

        # Extract QML type registrations
        qml_pattern = r'qmlRegisterType<([^>]+)>'
        self.analysis.qml_types = re.findall(qml_pattern, content)
        
        # Also look for qmlRegisterType calls with string names
        qml_string_pattern = r'qmlRegisterType\s*\(\s*"([^"]+)"'
        self.analysis.qml_types.extend(re.findall(qml_string_pattern, content))

        # Extract QObject-derived classes from qt_meta_data pattern
        metaobj_pattern = r'qt_meta_data_([A-Z][a-zA-Z0-9]+)'
        meta_calls = re.findall(metaobj_pattern, content)
        
        for name in meta_calls:
            if name not in ["QString", "QObject", "QVariant"] and name not in self.analysis.qobject_classes:
                self.analysis.qobject_classes.append(name)

        # Extract metatype registrations with better cleaning
        meta_pattern = r'QMetaTypeFunctionHelper<([^>]+)>'
        raw_metatypes = re.findall(meta_pattern, content)
        for mt in raw_metatypes:
            cleaned = self._clean_metatype(mt)
            if cleaned and cleaned not in self.analysis.metatypes:
                self.analysis.metatypes.append(cleaned)

        # Extract plugin registrations
        plugin_pattern = r'Q_IMPORT_PLUGIN\s*\(\s*(\w+)\s*\)'
        plugins = re.findall(plugin_pattern, content)
        self.analysis.plugins.extend(p for p in plugins if p not in self.analysis.plugins)

        logger.info(f"Found {len(self.analysis.qml_types)} QML types")
        logger.info(f"Found {len(self.analysis.qobject_classes)} QObject classes")

    def _clean_metatype(self, mt: str) -> str:
        """Clean Qt metatype template syntax."""
        # Remove ", true" suffix that appears in Qt5 metatype templates
        mt = re.sub(r', true$', '', mt)
        # Remove trailing incomplete template markers (unclosed angle brackets)
        if '<' in mt and '>' not in mt:
            # Incomplete template like "QQmlListProperty<Recipe" -> extract class name
            match = re.search(r'<([^,>]+)', mt)
            if match:
                return match.group(1)
        return mt

    def analyze_debug_info(self) -> None:
        """Extract Qt source file information from DWARF."""
        debug_file = self.reports_dir / "07-debug.txt"
        if not debug_file.exists():
            debug_file = self.reports_dir / "07-debug-info.txt"
        
        if not debug_file.exists():
            logger.warning("Debug info report not found")
            return

        content = debug_file.read_text()
        
        # Look for Qt headers in include paths
        qt_header_pattern = r'[^\s"]*(?:Qt|\.\./\.\./\.\./qt|qtbase)/\w+\.h'
        qt_headers = re.findall(qt_header_pattern, content, re.I)
        
        if qt_headers:
            logger.info(f"Found {len(qt_headers)} Qt header references in debug info")

    def analyze_strings(self) -> dict[str, list[str]]:
        """Extract Qt-related strings from binary strings dump."""
        strings_file = self.reports_dir / "10-strings.txt"
        if not strings_file.exists():
            return {}

        content = strings_file.read_text()

        qt_patterns = {
            "qml_files": re.findall(r'[^/]+\.qml', content),
            "plugin_paths": re.findall(r'plugins?/[^\\s"]+', content, re.I),
            "qt_plugins": re.findall(r'Qt\d?/\w+', content),
            "resource_paths": re.findall(r'qrc_[^\\s"]+', content),
        }

        return qt_patterns

    def generate_report(self, output_dir: Optional[Path] = None) -> None:
        """Generate Qt analysis report."""
        output_dir = output_dir or self.reports_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # Markdown report
        md_report = output_dir / "09-qt.md"
        content = self._generate_markdown()
        md_report.write_text(content)
        logger.info(f"Generated {md_report}")

        # JSON report
        json_report = output_dir / "qt-analysis.json"
        data = {
            "version": self.analysis.version,
            "modules": self.analysis.modules,
            "qml_types": self.analysis.qml_types,
            "qobject_classes": self.analysis.qobject_classes,
            "metatypes": self.analysis.metatypes,
            "plugins": self.analysis.plugins,
        }
        json_report.write_text(json.dumps(data, indent=2))
        logger.info(f"Generated {json_report}")

    def _generate_markdown(self) -> str:
        """Generate markdown report content."""
        content = f"""# Qt Analysis Report

## Qt Version
{self.analysis.version}

## Detected Qt Modules
"""
        for mod in sorted(self.analysis.modules):
            content += f"- {mod}\n"

        content += """
## QML Registered Types
"""
        for qml_type in sorted(self.analysis.qml_types)[:50]:
            content += f"- {qml_type}\n"

        content += """
## QObject-Derived Classes
"""
        for cls in sorted(self.analysis.qobject_classes)[:50]:
            content += f"- {cls}\n"

        content += """
## Metatypes
"""
        for mt in sorted(self.analysis.metatypes)[:20]:
            content += f"- {mt}\n"

        content += """
## Qt Plugins Imported
"""
        for plugin in sorted(self.analysis.plugins):
            content += f"- {plugin}\n"

        return content


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Qt-specific information in ELF binaries"
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path(__file__).parent.parent / "reports",
        help="Directory containing ELF analysis reports"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: same as reports-dir)"
    )

    args = parser.parse_args()
    output_dir = args.output_dir or args.reports_dir

    analyzer = QtAnalyzer(args.reports_dir)
    analyzer.analyze_dynamic()
    analyzer.analyze_symbols()
    analyzer.analyze_debug_info()
    analyzer.analyze_strings()
    analyzer.generate_report(output_dir)


if __name__ == "__main__":
    main()