#!/usr/bin/env python3
"""
ELF Analysis Toolkit - Primary entry point for embedded Linux executable analysis.

This tool analyzes ELF executables using cross-toolchain utilities and generates
comprehensive reports for understanding architecture, dependencies, and build requirements.

Plugin Architecture:
- Core analyzers handle basic ELF parsing
- Plugin analyzers can be registered for domain-specific analysis
- Plugins: Qt, Network, Serial, Resources, Debug, Firmware, Database

Usage:
    python3 scripts/elf-report.py BrewieApplication
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, TYPE_CHECKING

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import plugins
try:
    from plugins import ResourceAnalyzer, FirmwareAnalyzer, DatabaseAnalyzer
except ImportError:
    # Plugins not available (e.g., running from outside scripts dir)
    ResourceAnalyzer = None
    FirmwareAnalyzer = None
    DatabaseAnalyzer = None


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class ElfInfo:
    """Parsed ELF header information."""
    architecture: str = ""
    abi: str = ""
    float_abi: str = ""
    elf_class: str = ""
    endian: str = ""
    entry_point: str = ""
    machine: str = ""
    flags: str = ""


@dataclass
class QtInfo:
    """Parsed Qt module information."""
    version: str = "5"
    modules: list[str] = field(default_factory=list)
    plugins: list[str] = field(default_factory=list)
    qml_types: list[str] = field(default_factory=list)
    qobject_subclasses: list[str] = field(default_factory=list)


@dataclass
class BuildInfo:
    """Build toolchain information from DWARF."""
    compiler: str = ""
    linker: str = ""
    cxx_standard: str = ""
    build_ids: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)
    namespaces: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    elf_info: ElfInfo = field(default_factory=ElfInfo)
    qt_info: QtInfo = field(default_factory=QtInfo)
    build_info: BuildInfo = field(default_factory=BuildInfo)
    libraries: list[str] = field(default_factory=list)
    has_pie: bool = False
    has_dwarf: bool = False
    rpath: str = ""
    runpath: str = ""
    strings: dict[str, list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    # Extended analysis results
    firmware_update_strings: list[str] = field(default_factory=list)
    filesystem_paths: list[str] = field(default_factory=list)
    sqlite_references: list[str] = field(default_factory=list)


# ============================================================================
# Plugin Interface
# ============================================================================

class AnalyzerPlugin(ABC):
    """Abstract base class for analysis plugins.
    
    Plugins must implement:
    - name: unique identifier for the plugin
    - output_files: list of report files this plugin generates
    - analyze(result, elf_path): perform analysis and update result
    - generate_report(): optional, create plugin-specific reports
    """
    
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name for identification."""
        pass
    
    @property
    @abstractmethod  
    def output_files(self) -> list[str]:
        """List of output report files this plugin generates."""
        pass
    
    def analyze(self, result: AnalysisResult, elf_path: Path) -> Optional[dict]:
        """Perform analysis and return results. Called after core analysis."""
        return None
    
    def generate_report(self) -> None:
        """Generate plugin-specific report files. Override if needed."""
        pass
    
    def _report_exists(self, filename: str) -> bool:
        """Check if a report already exists."""
        return (self.reports_dir / filename).exists()


# ============================================================================
# Core ELF Analyzer
# ============================================================================

class ELFAnalyzer:
    """Main ELF analyzer with plugin architecture.
    
    This class handles the core ELF analysis and delegates plugin-specific
    analysis to registered plugins.
    """
    
    REPORT_FILES = [
        "00-summary.md",
        "01-header.txt",
        "02-program-headers.txt",
        "03-sections.txt",
        "04-symbols.txt",
        "05-dynamic.txt",
        "06-libraries.txt",
        "07-debug.txt",
        "08-source-files.txt",
        "09-qt.md",
        "10-strings.txt",
        "11-network.txt",
        "12-serial.txt",
        "13-json-summary.json",
    ]
    
    def __init__(self, elf_path: Path, reports_dir: Path, tool_prefix: Optional[str] = None):
        self.elf_path = elf_path
        self.reports_dir = reports_dir
        self.tool_prefix = tool_prefix
        self.result = AnalysisResult()
        self._plugins: list[AnalyzerPlugin] = []
    
    def register_plugin(self, plugin) -> None:
        """Register an analysis plugin.
        
        Accepts any object with:
        - name property
        - output_files property  
        - analyze() method
        - generate_report() method
        """
        self._plugins.append(plugin)
        logger.info(f"Registered plugin: {plugin.name}")
    
    def auto_register_plugins(self) -> None:
        """Auto-register available plugins from the plugins package."""
        if ResourceAnalyzer:
            self.register_plugin(ResourceAnalyzer(self.reports_dir))
        if FirmwareAnalyzer:
            self.register_plugin(FirmwareAnalyzer(self.reports_dir))
        if DatabaseAnalyzer:
            self.register_plugin(DatabaseAnalyzer(self.reports_dir))
    
    def _load_toolprefix(self) -> Optional[str]:
        """Load TOOLPREFIX from fish_env file if available.
        
        The fish_env file contains: set -g TOOLPREFIX /path/to/tools
        We extract the path portion.
        """
        env_file = Path(__file__).parent.parent / "fish_env"
        if env_file.exists():
            content = env_file.read_text().strip()
            # Match: set -g TOOLPREFIX /path/to/bin/arm-linux
            match = re.search(r'TOOLPREFIX\s+(\S+)', content)
            if match:
                return match.group(1).strip()
        return None
    
    def _get_tool(self, tool_name: str) -> str:
        """Get full tool path with prefix if configured."""
        prefix = self.tool_prefix or self._load_toolprefix()
        if prefix:
            return f"{prefix}-{tool_name}"
        return tool_name
    
    def _run_tool(self, tool_name: str, args: list[str], capture_output: bool = True) -> str:
        """Run a cross-toolchain binary tool."""
        tool = self._get_tool(tool_name)
        cmd = [tool] + args + [str(self.elf_path)]
        
        try:
            proc = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=120
            )
            return proc.stdout + proc.stderr
        except FileNotFoundError:
            logger.warning(f"Tool {tool} not found, trying fallback")
            cmd = [tool_name] + args + [str(self.elf_path)]
            proc = subprocess.run(cmd, capture_output=capture_output, text=True, timeout=120)
            return proc.stdout + proc.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Tool {tool} timed out")
            return ""
    
    def _report_exists(self, filename: str) -> bool:
        """Check if a report already exists."""
        return (self.reports_dir / filename).exists()
    
    def _write_report(self, filename: str, content: str) -> None:
        """Write report to file."""
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / filename).write_text(content)
        logger.info(f"Generated {filename}")
    
    def _write_json_report(self, filename: str, data: dict) -> None:
        """Write JSON report to file."""
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / filename).write_text(json.dumps(data, indent=2))
        logger.info(f"Generated {filename}")
    
    # ========================================================================
    # Core Analysis Methods
    # ========================================================================
    
    def analyze_header(self) -> None:
        """Analyze ELF header (report 01-header.txt)."""
        output_file = "01-header.txt"
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists), parsing existing")
            content = (self.reports_dir / output_file).read_text()
        else:
            content = self._run_tool("readelf", ["-h"])
            self._write_report(output_file, content)
        
        self._parse_header(content)
    
    def _parse_header(self, content: str) -> None:
        """Parse ELF header content."""
        for line in content.splitlines():
            if "Machine:" in line:
                if "ARM" in line:
                    self.result.elf_info.machine = "ARM"
                elif "AArch64" in line:
                    self.result.elf_info.machine = "ARM64"
            if "Class:" in line:
                self.result.elf_info.elf_class = "ELF32" if "ELF32" in line else "ELF64"
            if "Data:" in line:
                self.result.elf_info.endian = "little" if "little" in line else "big"
            if "Entry point address:" in line:
                self.result.elf_info.entry_point = line.split(":")[-1].strip()
            if "Flags:" in line:
                # Format: Flags:                             0x5000002, Version5 EABI, hard-float
                flags = line.split(":", 1)[-1].strip() if ":" in line else ""
                self.result.elf_info.flags = flags
                if "hard" in flags.lower() or "0x5000" in flags:
                    self.result.elf_info.float_abi = "hard"
            if "OS/ABI:" in line and "System V" in line:
                self.result.elf_info.abi = "UNIX - System V"
    
    def analyze_program_headers(self) -> None:
        """Analyze program headers (report 02-program-headers.txt)."""
        output_file = "02-program-headers.txt"
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists)")
            return
        
        content = self._run_tool("readelf", ["-l"])
        self._write_report(output_file, content)
        
        # Detect PIE - presence of PT_INTERP means not PIE
        if "PT_INTERP" in content:
            self.result.has_pie = False
    
    def analyze_sections(self) -> None:
        """Analyze sections (report 03-sections.txt)."""
        output_file = "03-sections.txt"
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists), parsing for DWARF")
            content = (self.reports_dir / output_file).read_text()
        else:
            content = self._run_tool("readelf", ["-S"])
            self._write_report(output_file, content)
        
        # Detect DWARF presence
        if ".debug_info" in content or ".debug_str" in content:
            self.result.has_dwarf = True
            logger.info("DWARF debug information detected")
    
    def analyze_symbols(self) -> None:
        """Analyze symbols (report 04-symbols.txt)."""
        output_file = "04-symbols.txt"
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists)")
            return
        
        content = self._run_tool("nm", ["-C"])
        self._write_report(output_file, content)
    
    def analyze_dynamic(self) -> None:
        """Analyze dynamic section (report 05-dynamic.txt)."""
        output_file = "05-dynamic.txt"
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists), parsing libraries")
            content = (self.reports_dir / output_file).read_text()
        else:
            content = self._run_tool("readelf", ["-d"])
            self._write_report(output_file, content)
        
        # Always parse dynamic content to populate libraries
        self._parse_dynamic(content)
    
    def _parse_dynamic(self, content: str) -> None:
        """Parse dynamic section for libraries and paths."""
        for line in content.splitlines():
            if "(NEEDED)" in line:
                # Format: 0x00000001 (NEEDED) Shared library: [libQt5Core.so.5]
                match = re.search(r'\[\s*([^\]]+)\s*\]', line)
                if match:
                    lib = match.group(1).strip()
                    self.result.libraries.append(lib)
            if "(RPATH)" in line:
                # Format: 0x... (RPATH) Library rpath: [/usr/lib]
                match = re.search(r'Library rpath:\s*\[\s*([^\]]+)\s*\]', line)
                if match:
                    self.result.rpath = match.group(1).strip()
            if "(RUNPATH)" in line:
                match = re.search(r'Library runpath:\s*\[\s*([^\]]+)\s*\]', line)
                if match:
                    self.result.runpath = match.group(1).strip()
    
    def analyze_libraries(self) -> None:
        """Analyze shared libraries (report 06-libraries.txt)."""
        output_file = "06-libraries.txt"
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists)")
            return
        
        content = f"# Shared Libraries Required by {self.elf_path.name}\n\n"
        for lib in sorted(set(self.result.libraries)):
            content += f"- {lib}\n"
        self._write_report(output_file, content)
    
    def analyze_debug(self) -> None:
        """Analyze DWARF debug information (report 07-debug.txt)."""
        output_file = "07-debug.txt"
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists), parsing debug info")
            content = (self.reports_dir / output_file).read_text()
            self._parse_debug_info(content)
        else:
            content = self._run_tool("readelf", ["--debug-dump=info"])
            self._write_report(output_file, content)
            self._parse_debug_info(content)
    
    def _parse_debug_info(self, content: str) -> None:
        """Parse DWARF debug info for build artifacts.
        
        The format from readelf --debug-dump=info looks like:
        <0><b><abbrev number>: 16
          <..><..> DW_AT_producer: (indirect string, offset: 0x....): GNU C++ 4.8.2
        <0><b><abbrev number>: 16
          <..><..> DW_AT_name: (indirect string, offset: 0x....): ../main.cpp
        """
        # Extract compiler info
        compiler_match = re.search(
            r'DW_AT_producer\s*:\s*\(indirect string, offset: [^)]+\):\s+(GNU C\+\+\s*[\d.]+)',
            content
        )
        if compiler_match:
            self.result.build_info.compiler = compiler_match.group(1)
            logger.info(f"Detected compiler: {compiler_match.group(1)}")
        
        # Extract C++ standard
        std_match = re.search(r'-std=c\+\+(\d+)', content)
        if std_match:
            self.result.build_info.cxx_standard = f"C++{std_match.group(1)}"
        
        # Extract source files - format: DW_AT_name: (indirect string, offset: X): ../path/to/file.cpp
        source_pattern = r'DW_AT_name\s*:\s*\(indirect string, offset: [^)]+\):\s*(\.\./[^\s<]+)'
        source_matches = re.findall(source_pattern, content)
        seen = set()
        for src in source_matches:
            clean = src.rstrip('<').rstrip('|')
            if clean and clean not in seen:
                seen.add(clean)
                self.result.build_info.source_files.append(clean)
        
        if self.result.build_info.source_files:
            logger.info(f"Recovered {len(self.result.build_info.source_files)} source files from DWARF")
    
    def analyze_source_files(self) -> None:
        """Extract source file references (report 08-source-files.txt)."""
        output_file = "08-source-files.txt"
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists)")
            return
        
        content = f"# Source Files Recovered from DWARF\n\n"
        content += f"Compiler: {self.result.build_info.compiler or 'Unknown'}\n"
        content += f"C++ Standard: {self.result.build_info.cxx_standard or 'Unknown'}\n\n"
        content += "## Source Files\n"
        for src in sorted(set(self.result.build_info.source_files)):
            content += f"- {src}\n"
        
        self._write_report(output_file, content)
    
    def analyze_strings(self) -> None:
        """Analyze strings in binary (report 10-strings.txt)."""
        output_file = "10-strings.txt"
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists)")
            content = (self.reports_dir / output_file).read_text()
        else:
            content = self._run_tool("strings", ["-n", "8"])
            self._write_report(output_file, content)
        
        # Extract various string categories
        self.result.strings = {
            "http": re.findall(r'https?://[^\s<>"\']+', content),
            "file": re.findall(r'/[\w/.-]+\.[a-zA-Z]{1,5}', content),
            "update": re.findall(r'[a-z]*update[a-z]*', content, re.I),
            "firmware": re.findall(r'[a-z]*firmware[a-z]*', content, re.I),
        }
        
        # Extract firmware update patterns
        self.result.firmware_update_strings = [
            s for s in self.result.strings["update"] 
            if "firmware" in s.lower()
        ]
        
        # Extract filesystem paths
        self.result.filesystem_paths = [
            p for p in self.result.strings["file"] 
            if p.startswith('/') and len(p) > 1
        ]
        
        # Detect SQLite references
        sqlite_patterns = re.findall(r'(?:sqlite|QSql|\.db|\.sqlite)', content, re.I)
        self.result.sqlite_references = list(set(sqlite_patterns))
        
        if self.result.sqlite_references:
            logger.info(f"Found {len(self.result.sqlite_references)} SQLite references")
    
    def analyze_network(self) -> None:
        """Analyze network-related strings (report 11-network.txt)."""
        output_file = "11-network.txt"
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists)")
            return
        
        strings_file = self.reports_dir / "10-strings.txt"
        if strings_file.exists():
            content = strings_file.read_text()
        else:
            content = self._run_tool("strings", ["-n", "8"])
        
        report = "# Network Analysis\n\n"
        
        # Check for Qt Network module
        if "libQt5Network.so.5" in self.result.libraries:
            report += "## Qt Network Module\n- Qt5Network module detected\n\n"
        
        network_patterns = [
            (r'https?://[^\s<>"\']+', "URLs"),
            (r'[a-z]*tcp[a-z]*', "TCP"),
            (r'[a-z]*socket[a-z]*', "Socket"),
            (r'[a-z]*network[a-z]*', "Network"),
            (r'[a-z]*http[a-z]*', "HTTP"),
            (r'[a-z]*ftp[a-z]*', "FTP"),
            (r'[a-z]*mqtt[a-z]*', "MQTT"),
            (r'[a-z]*ssl[a-z]*', "SSL/TLS"),
        ]
        
        for pattern, label in network_patterns:
            matches = re.findall(pattern, content, re.I)
            if matches:
                report += f"## {label}\n"
                for m in sorted(set(matches))[:50]:
                    report += f"- {m}\n"
                report += "\n"
        
        self._write_report(output_file, report)
    
    def analyze_serial(self) -> None:
        """Analyze serial port related strings (report 12-serial.txt)."""
        output_file = "12-serial.txt"
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists)")
            return
        
        strings_file = self.reports_dir / "10-strings.txt"
        if strings_file.exists():
            content = strings_file.read_text()
        else:
            content = self._run_tool("strings", ["-n", "8"])
        
        report = "# Serial Port Analysis\n\n"
        
        # Check for Qt Serial Port module
        if "libQt5SerialPort.so.5" in self.result.libraries:
            report += "## Qt Serial Port Module\n- Qt5SerialPort module detected\n- Used for serial communication with brewing equipment\n\n"
        
        serial_patterns = [
            (r'UART\d*', "UART"),
            (r'/dev/tty[AS]?[A-Za-z0-9]*', "Device Paths"),
            (r'baudrate|baud', "Baud Rate"),
            (r'parity|stop.?bits|data.?bits', "Serial Settings"),
            (r'[a-z]*serial[a-z]*', "Serial"),
            (r'modbus|rtu', "Protocols"),
        ]
        
        for pattern, label in serial_patterns:
            matches = re.findall(pattern, content, re.I)
            if matches:
                report += f"## {label}\n"
                for m in sorted(set(matches))[:50]:
                    report += f"- {m}\n"
                report += "\n"
        
        self._write_report(output_file, report)
    
    def analyze_qt(self) -> None:
        """Analyze Qt-specific information (report 09-qt.md)."""
        output_file = "09-qt.md"
        
        # Always parse Qt info from existing reports regardless of file existence
        self._parse_qt_from_existing()
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists), Qt info already parsed")
            return
        
        content = "# Qt Analysis Report\n\n"
        
        # Extract Qt modules from libraries (already done in _parse_qt_from_existing)
        content += f"## Qt Version\n{self.result.qt_info.version}\n\n"
        
        content += "## Detected Qt Modules\n"
        for mod in sorted(self.result.qt_info.modules):
            clean_mod = mod.replace("Qt5", "Qt5 ").replace("Qt6", "Qt6 ")
            content += f"- {clean_mod}\n"
        
        content += "\n## QML Registered Types\n"
        for qml_type in sorted(self.result.qt_info.qml_types)[:50]:
            content += f"- {qml_type}\n"
        
        content += "\n## QObject-Derived Classes\n"
        for cls in sorted(self.result.qt_info.qobject_subclasses)[:50]:
            content += f"- {cls}\n"
        
        self._write_report(output_file, content)
    
    def _parse_qt_from_existing(self) -> None:
        """Parse existing reports to populate QtInfo without regenerating."""
        # Parse Qt modules directly from dynamic section
        dyn_file = self.reports_dir / "05-dynamic.txt"
        if dyn_file.exists():
            content = dyn_file.read_text()
            # Extract NEEDED libraries and find Qt ones
            for line in content.splitlines():
                if "(NEEDED)" in line:
                    match = re.search(r'\[\s*([^\]]+)\s*\]', line)
                    if match:
                        lib = match.group(1).strip()
                        if ("Qt5" in lib or "Qt6" in lib) and lib in self.result.libraries:
                            clean_mod = lib.replace("lib", "").replace(".so.5", "").replace(".so.6", "")
                            if clean_mod not in self.result.qt_info.modules:
                                self.result.qt_info.modules.append(clean_mod)
        
        # Parse QML types from strings
        strings_file = self.reports_dir / "10-strings.txt"
        if strings_file.exists():
            sym_content = strings_file.read_text()
            qml_pattern = r'qmlRegisterType<([^>]+)>'
            self.result.qt_info.qml_types = re.findall(qml_pattern, sym_content)
        
        # Parse QObject subclasses from symbols using moc patterns
        # Pattern matches qt_static_metacall for class names
        sym_file = self.reports_dir / "04-symbols.txt"
        if sym_file.exists():
            sym_content = sym_file.read_text()
            # Look for qt_meta_data_ClassName pattern or qt_static_metacall patterns
            metaobj_pattern = r'qt_meta_data_([A-Z][a-zA-Z0-9]+)'
            meta_matches = re.findall(metaobj_pattern, sym_content)
            
            for name in meta_matches:
                if name not in self.result.qt_info.qobject_subclasses and name not in ["QString", "QObject", "QVariant"]:
                    self.result.qt_info.qobject_subclasses.append(name)
    
    def generate_summary(self) -> None:
        """Generate executive summary (report 00-summary.md)."""
        output_file = "00-summary.md"
        
        if self._report_exists(output_file):
            logger.info(f"Skipping {output_file} (exists)")
            return
        
        content = f"""# ELF Analysis Summary

## Binary Information
- **File**: {self.elf_path.name}
- **Size**: {self.elf_path.stat().st_size:,} bytes
- **Architecture**: {self.result.elf_info.machine} ({self.result.elf_info.elf_class})
- **Endian**: {self.result.elf_info.endian}
- **ABI**: {self.result.elf_info.abi}
- **Float ABI**: {self.result.elf_info.float_abi}
- **Entry Point**: {self.result.elf_info.entry_point}
- **PIE**: {"Yes" if self.result.has_pie else "No"}
- **DWARF Debug**: {"Yes" if self.result.has_dwarf else "No"}

## Build Information
- **Compiler**: {self.result.build_info.compiler or "Unknown"}
- **C++ Standard**: {self.result.build_info.cxx_standard or "Unknown"}
- **RPATH**: {self.result.rpath or "None"}
- **RUNPATH**: {self.result.runpath or "None"}

## Dependencies
- **Total Libraries**: {len(self.result.libraries)}
- **Qt Modules**: {len(self.result.qt_info.modules)}
- **Source Files Recovered**: {len(self.result.build_info.source_files)}

"""
        
        content += "## Qt Modules\n"
        for mod in sorted(self.result.qt_info.modules):
            clean_mod = mod.replace("Qt5", "Qt5 ").replace("Qt6", "Qt6 ")
            content += f"- {clean_mod}\n"
        
        content += f"\n## QObject Subclasses\n"
        content += f"Found {len(self.result.qt_info.qobject_subclasses)} classes with QObject inheritance.\n"
        for cls in sorted(self.result.qt_info.qobject_subclasses)[:20]:
            content += f"- {cls}\n"
        if len(self.result.qt_info.qobject_subclasses) > 20:
            content += f"- ... and {len(self.result.qt_info.qobject_subclasses) - 20} more\n"
        
        content += f"\n## Source Files Recovered\n"
        content += f"Found {len(self.result.build_info.source_files)} source files in debug info.\n"
        for src in sorted(self.result.build_info.source_files)[:20]:
            content += f"- {src}\n"
        if len(self.result.build_info.source_files) > 20:
            content += f"- ... and {len(self.result.build_info.source_files) - 20} more\n"
        
        if self.result.warnings:
            content += "\n## Warnings\n"
            for w in self.result.warnings:
                content += f"- {w}\n"
        
        self._write_report(output_file, content)
    
    def generate_json_summary(self, update: bool = False) -> None:
        """Generate JSON summary (report 13-json-summary.json)."""
        
        # Always parse from existing reports to populate data
        self._parse_qt_from_existing()
        
        output_file = "13-json-summary.json"
        
        if self._report_exists(output_file) and not update:
            logger.info(f"Skipping {output_file} (exists, use --update-json to refresh)")
            return
        
        data = {
            "binary": {
                "name": self.elf_path.name,
                "size": self.elf_path.stat().st_size,
            },
            "elf": {
                "architecture": self.result.elf_info.machine,
                "class": self.result.elf_info.elf_class,
                "endian": self.result.elf_info.endian,
                "abi": self.result.elf_info.abi,
                "float_abi": self.result.elf_info.float_abi,
                "entry_point": self.result.elf_info.entry_point,
                "pie": self.result.has_pie,
                "dwarf": self.result.has_dwarf,
            },
            "build": {
                "compiler": self.result.build_info.compiler,
                "cxx_standard": self.result.build_info.cxx_standard,
                "rpath": self.result.rpath,
                "runpath": self.result.runpath,
            },
            "qt": {
                "version": self.result.qt_info.version,
                "modules": sorted(self.result.qt_info.modules),
                "qml_types": sorted(self.result.qt_info.qml_types),
                "qobject_subclasses": sorted(self.result.qt_info.qobject_subclasses),
            },
            "libraries": sorted(self.result.libraries),
            "source_files": sorted(self.result.build_info.source_files),
            "sqlite_references": self.result.sqlite_references,
            "firmware_strings": self.result.firmware_update_strings,
            "warnings": self.result.warnings,
        }
        
        self._write_json_report(output_file, data)
    
    def run_all(self, update_json: bool = False) -> None:
        """Run all core analyzers and plugins in the required order."""
        logger.info(f"Analyzing {self.elf_path}")
        
        # Core analysis in order (per AGENT.md)
        self.analyze_header()
        self.analyze_program_headers()
        self.analyze_sections()
        self.analyze_dynamic()
        self.analyze_symbols()
        self.analyze_debug()
        self.analyze_source_files()
        self.analyze_strings()
        self.analyze_qt()
        self.analyze_network()
        self.analyze_serial()
        self.analyze_libraries()
        self.generate_summary()
        self.generate_json_summary(update_json)
        
        # Run plugin analysis
        for plugin in self._plugins:
            plugin.analyze(self.result, self.elf_path)
            plugin.generate_report()
        
        logger.info("Analysis complete")


# ============================================================================
# Main Entry Point
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze embedded Linux ELF executables using cross-toolchain utilities"
    )
    parser.add_argument(
        "binary",
        type=Path,
        help="Path to the ELF binary to analyze"
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path(__file__).parent.parent / "reports",
        help="Directory to write reports"
    )
    parser.add_argument(
        "--tool-prefix",
        type=str,
        default=None,
        help="Cross-toolchain prefix (overrides fish_env)"
    )
    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Regenerate reports even if they exist"
    )
    parser.add_argument(
        "--no-plugins",
        action="store_true",
        help="Skip plugin analysis (resources, firmware, database)"
    )
    parser.add_argument(
        "--update-json",
        action="store_true",
        help="Update JSON summary from existing reports"
    )
    
    args = parser.parse_args()
    
    # Resolve binary path
    binary_path = args.binary.resolve()
    if not binary_path.exists():
        logger.error(f"Binary not found: {binary_path}")
        sys.exit(1)
    
    analyzer = ELFAnalyzer(
        elf_path=binary_path,
        reports_dir=args.reports_dir,
        tool_prefix=args.tool_prefix
    )
    
    # Register plugins (unless disabled)
    if not args.no_plugins:
        analyzer.auto_register_plugins()
    
    analyzer.run_all(args.update_json)


if __name__ == "__main__":
    main()