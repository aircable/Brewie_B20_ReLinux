#!/usr/bin/env python3
"""
Database Analyzer Plugin for ELF binaries.

Detects database and file operation patterns from strings and symbols.

Usage:
    analyzer.register_plugin(DatabaseAnalyzer(reports_dir))
    # Or run standalone: python3 plugins/database_analyzer.py
"""

import re
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class DatabaseInfo:
    """Database analysis results."""
    sqlite_refs: list[str] = field(default_factory=list)
    sql_queries: list[str] = field(default_factory=list)
    file_operations: list[str] = field(default_factory=list)
    config_files: list[str] = field(default_factory=list)


class DatabaseAnalyzer:
    """Detect database-related patterns in ELF binaries.
    
    Looks for:
    - SQLite/QSql references
    - SQL query patterns
    - File operations (open, read, write, close)
    - Configuration file paths
    
    Compatible with AnalyzerPlugin interface via duck typing.
    """
    
    OUTPUT_FILES = ["15-database.md", "database.json"]
    
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.database_info = DatabaseInfo()
        self.name = "database-analyzer"
        self.output_files = self.OUTPUT_FILES
    
    def analyze(self, result: Optional[dict] = None, elf_path: Optional[Path] = None) -> DatabaseInfo:
        """Extract database information from strings and symbols."""
        # Check strings first
        strings_file = self.reports_dir / "10-strings.txt"
        if strings_file.exists():
            content = strings_file.read_text()
            
            # SQLite/QSql references
            self.database_info.sqlite_refs.extend(
                re.findall(r'(?:sqlite|QSql)[^\s]*', content, re.I)
            )
            
            # SQL queries
            self.database_info.sql_queries.extend(
                re.findall(r'(?:SELECT|INSERT|UPDATE|DELETE|CREATE)\s+[^\s;"]+', content, re.I)
            )
            
            # File operations
            self.database_info.file_operations.extend(
                re.findall(r'(?:open|read|write|close)\s*\([^)]+\)', content, re.I)
            )
            
            # Config files
            self.database_info.config_files.extend(
                re.findall(r'[^\s/]+/(?:[^\s/]+\.)?(?:conf|ini|json|xml)', content, re.I)
            )
        
        # Also check debug/symbols for QSql class references
        debug_file = self.reports_dir / "07-debug.txt"
        if debug_file.exists():
            content = debug_file.read_text()
            self.database_info.sqlite_refs.extend(
                re.findall(r'QSql[a-zA-Z]*', content)
            )
        
        return self.database_info
    
    def generate_report(self) -> None:
        """Generate database analysis report."""
        report = f"""# Database Analysis

## SQLite/QSql References
Found {len(self.database_info.sqlite_refs)} database library references.
"""
        for ref in sorted(set(self.database_info.sqlite_refs))[:30]:
            report += f"- {ref}\n"
        
        report += f"""
## SQL Queries Detected
Found {len(self.database_info.sql_queries)} SQL query fragments.
"""
        for query in sorted(set(self.database_info.sql_queries))[:30]:
            report += f"- {query}\n"
        
        report += f"""
## File Operations
Found {len(self.database_info.file_operations)} file operation references.
"""
        for op in sorted(set(self.database_info.file_operations))[:30]:
            report += f"- {op}\n"
        
        report += f"""
## Configuration Files
Found {len(self.database_info.config_files)} configuration file references.
"""
        for cfg in sorted(set(self.database_info.config_files))[:30]:
            report += f"- {cfg}\n"
        
        output_path = self.reports_dir / "15-database.md"
        if not output_path.exists():
            output_path.write_text(report)
            logger.info(f"Generated {output_path}")
        else:
            logger.info(f"Skipping {output_path} (exists)")
        
        json_path = self.reports_dir / "database.json"
        if not json_path.exists():
            json_path.write_text(json.dumps({
                "sqlite_refs": self.database_info.sqlite_refs,
                "sql_queries": self.database_info.sql_queries,
                "file_operations": self.database_info.file_operations,
                "config_files": self.database_info.config_files,
            }, indent=2))


def main() -> None:
    """Run standalone database analysis."""
    logging.basicConfig(level=logging.INFO)
    
    reports_dir = Path(__file__).parent.parent.parent / "reports"
    
    analyzer = DatabaseAnalyzer(reports_dir)
    analyzer.analyze()
    analyzer.generate_report()
    
    logger.info(f"Found {len(analyzer.database_info.sqlite_refs)} database references")


if __name__ == "__main__":
    main()