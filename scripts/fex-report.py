#!/usr/bin/env python3
"""
FEX Report Generator - Analyzes Allwinner FEX files and generates hardware reports.

This tool parses script.fex files from Allwinner (Sunxi) platforms and produces:
- Markdown reports with hardware summary
- JSON output for programmatic consumption
- Warnings about potential issues
"""

import argparse
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class FexSection:
    """Represents a section in a FEX file."""
    name: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class FexReport:
    """Complete analysis report from FEX parsing."""
    sections: list[FexSection] = field(default_factory=list)
    hardware_summary: dict[str, Any] = field(default_factory=dict)
    gpio_summary: list[dict[str, Any]] = field(default_factory=list)
    lcd_timings: dict[str, Any] = field(default_factory=dict)
    peripherals: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def parse_fex_file(fex_path: Path) -> list[FexSection]:
    """Parse an Allwinner script.fex file into structured sections.
    
    FEX format:
    - Sections start with section name in square brackets [section_name]
    - Key-value pairs follow: key = value or key = value0,value1,...
    - Comments start with semicolon ; or hash #
    """
    sections: list[FexSection] = []
    current_section: FexSection | None = None
    
    content = fex_path.read_text(encoding='utf-8', errors='replace')
    
    for line in content.splitlines():
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith(';') or line.startswith('#'):
            continue
        
        # Check for section header
        section_match = re.match(r'\[(\w+)\]', line)
        if section_match:
            if current_section:
                sections.append(current_section)
            current_section = FexSection(name=section_match.group(1).lower())
            continue
        
        # Parse key-value pair
        if '=' in line and current_section:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Remove quotes
            value = value.strip('"')
            
            # Try to parse as list
            if ',' in value:
                try:
                    value = [v.strip() for v in value.split(',')]
                except ValueError:
                    pass
            
            # Try to parse as number
            elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                value = int(value)
            elif value.startswith('0x'):
                try:
                    value = int(value, 16)
                except ValueError:
                    pass
            
            current_section.parameters[key] = value
    
    if current_section:
        sections.append(current_section)
    
    return sections


def analyze_hardware(sections: list[FexSection]) -> dict[str, Any]:
    """Extract hardware summary from FEX sections."""
    summary: dict[str, Any] = {
        'soc': 'Allwinner A13 (sun5i)',
        'board_model': 'Unknown',
        'cpu_clock': 'Unknown',
        'memory': {},
        'storage': [],
        'display': {},
    }
    
    for section in sections:
        name = section.name
        params = section.parameters
        
        if name == 'product':
            summary['board_model'] = params.get('machine', 'Unknown')
        elif name == 'target':
            if 'boot_clock' in params:
                summary['cpu_clock'] = f"{params['boot_clock']} MHz"
            # PMIC voltages indicate AXP209
            if 'dcdc2_vol' in params or 'ldo2_vol' in params:
                summary['pmic'] = 'AXP20x (likely AXP209)'
                summary['dcdc2_voltage'] = f"{params.get('dcdc2_vol', 'N/A')} mV"
        elif name == 'dram' or name.startswith('dram_'):
            summary['memory'] = {
                'clock': f"{params.get('dram_clk', 'N/A')} MHz",
                'type': 'DDR3' if params.get('dram_type') == 3 else 'Unknown',
                'size': f"{params.get('dram_size', 'N/A')} MB",
                'bus_width': f"{params.get('dram_bus_width', 'N/A')} bit",
            }
        elif name.startswith('mmc') or name == 'card_boot0_para':
            summary['storage'].append({
                'type': 'MMC/SD',
                'host': name,
            })
        elif name.startswith('lcd'):
            summary['display'] = {
                'resolution': f"{params.get('lcd_x', 'N/A')}x{params.get('lcd_y', 'N/A')}",
                'pixel_clock_mhz': params.get('lcd_dclk_freq', 'N/A'),
                'timing_ht': params.get('lcd_ht', 'N/A'),
                'timing_hbp': params.get('lcd_hbp', 'N/A'),
                'timing_hspw': params.get('lcd_hv_hspw', 'N/A'),
                'timing_vt': params.get('lcd_vt', 'N/A'),
                'timing_vbp': params.get('lcd_vbp', 'N/A'),
                'timing_vspw': params.get('lcd_hv_vspw', 'N/A'),
            }
    
    return summary


def extract_gpio(sections: list[FexSection]) -> list[dict[str, Any]]:
    """Extract GPIO configuration from FEX sections."""
    gpio_list: list[dict[str, Any]] = []
    
    for section in sections:
        name = section.name
        if name.startswith('gpio') or 'pin' in name or 'lcd_bl_en' in section.parameters:
            gpio_config: dict[str, Any] = {
                'section': name,
                'pins': {},
            }
            
            for key, value in section.parameters.items():
                if any(port in str(value) for port in ['port:PA', 'port:PB', 'port:PC', 
                    'port:PD', 'port:PE', 'port:PF', 'port:PG', 'port:PH', 'port:PI']):
                    gpio_config['pins'][key] = value
            
            if gpio_config['pins']:
                gpio_list.append(gpio_config)
    
    return gpio_list


def extract_lcd_timings(sections: list[FexSection]) -> dict[str, Any]:
    """Extract LCD timing parameters from FEX sections."""
    timings: dict[str, Any] = {}
    
    for section in sections:
        if section.name.startswith('lcd'):
            controller_timings: dict[str, Any] = {}
            
            timing_keys = [
                'lcd_x', 'lcd_y', 'lcd_dclk_freq', 'lcd_ht', 'lcd_hbp', 'lcd_hv_hspw',
                'lcd_vt', 'lcd_vbp', 'lcd_hv_vspw', 'lcd_pwm_freq', 'lcd_pwm_pol'
            ]
            
            for key in timing_keys:
                if key in section.parameters:
                    controller_timings[key] = section.parameters[key]
            
            if controller_timings:
                timings[section.name] = controller_timings
    
    return timings


def extract_peripherals(sections: list[FexSection]) -> list[dict[str, Any]]:
    """Extract peripheral configurations from FEX sections."""
    peripherals: list[dict[str, Any]] = []
    
    peripheral_types = {
        'twi': 'I2C',
        'uart': 'UART',
        'spi': 'SPI',
        'pwm': 'PWM',
        'mmc': 'MMC/SD',
        'usb': 'USB',
        'csi': 'CSI/DVP Camera',
        'audio': 'Audio',
        'ir': 'IR Remote',
        'nand': 'NAND Flash',
        'rtp': 'Resistive Touch',
        'ctp': 'Capacitive Touch',
    }
    
    for section in sections:
        name = section.name
        for prefix, ptype in peripheral_types.items():
            if name.startswith(prefix):
                used = section.parameters.get(f'{prefix}_used', 
                             section.parameters.get(f'{prefix}0_used', 'unknown'))
                peripherals.append({
                    'type': ptype,
                    'section': name,
                    'used': used,
                    'parameters': section.parameters,
                })
    
    return peripherals


def generate_warnings(sections: list[FexSection]) -> list[str]:
    """Generate warnings about potential issues in FEX configuration."""
    warnings: list[str] = []
    
    # Known safe keys that shouldn't trigger warnings
    known_keys = {
        'version', 'machine', 'boot_clock', 'dcdc2_vol', 'dcdc3_vol', 'ldo2_vol',
        'ldo3_vol', 'ldo4_vol', 'pll4_freq', 'pll6_freq', 'logical_start',
        'sprite_gpio0', 'card_ctrl', 'card_high_speed', 'card_line',
        'sdc_d0', 'sdc_d1', 'sdc_d2', 'sdc_d3', 'sdc_clk', 'sdc_cmd',
        'twi_port', 'twi_scl', 'twi_sda', 'uart_debug_port',
        'uart_debug_tx', 'uart_debug_rx', 'jtag_enable',
    }
    
    for section in sections:
        for key in section.parameters:
            # Only warn on truly unusual keys
            if key not in known_keys and not key.startswith(('dram_', 'lcd_', 'csi_', 'port:')):
                # Skip common patterns
                if not any(skip in key for skip in ['nand_', 'mali_', 'twi_', 'uart_', 
                    'spi_', 'pmu_', 'gsensor_', 'leds_', 'motor_', 'keypad_', 'key_']):
                    warnings.append(f"[{section.name}] {key} = {section.parameters[key]}")
    
    return warnings[:20]  # Limit to 20 warnings


def generate_markdown_report(report: FexReport) -> str:
    """Generate a markdown report from the FEX analysis."""
    lines = [
        "# FEX Analysis Report",
        "",
        "## Hardware Summary",
        "",
    ]
    
    for key, value in report.hardware_summary.items():
        if isinstance(value, dict):
            lines.append(f"**{key}**:")
            for k, v in value.items():
                lines.append(f"  - {k}: {v}")
        elif isinstance(value, list):
            lines.append(f"**{key}**:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"**{key}**: {value}")
    
    lines.extend([
        "",
        "## GPIO Summary",
        "",
    ])
    
    for gpio in report.gpio_summary:
        lines.append(f"### {gpio['section']}")
        for pin, value in gpio.get('pins', {}).items():
            lines.append(f"- {pin}: {value}")
    
    if not report.gpio_summary:
        lines.append("No GPIO configurations found.")
    
    lines.extend([
        "",
        "## LCD Timings",
        "",
    ])
    
    if report.lcd_timings:
        for controller, timings in report.lcd_timings.items():
            lines.append(f"### {controller}")
            for key, value in timings.items():
                lines.append(f"- {key}: {value}")
    else:
        lines.append("No LCD timing configurations found.")
    
    lines.extend([
        "",
        "## Peripherals",
        "",
    ])
    
    if report.peripherals:
        for p in report.peripherals:
            lines.append(f"### {p['type']} ({p['section']})")
            lines.append(f"- used: {p['used']}")
            for key, value in p['parameters'].items():
                lines.append(f"- {key}: {value}")
    else:
        lines.append("No peripheral configurations found.")
    
    if report.warnings:
        lines.extend([
            "",
            "## Warnings",
            "",
        ])
        for warning in report.warnings:
            lines.append(f"- WARNING: {warning}")
    
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Analyze Allwinner FEX files and generate hardware reports'
    )
    parser.add_argument(
        'fex_file',
        type=Path,
        help='Path to script.fex file'
    )
    parser.add_argument(
        '--output-md',
        type=Path,
        default=None,
        help='Output markdown report path (default: stdout)'
    )
    parser.add_argument(
        '--output-json',
        type=Path,
        default=None,
        help='Output JSON report path (default: stdout)'
    )
    
    args = parser.parse_args()
    
    if not args.fex_file.exists():
        logger.error(f"FEX file not found: {args.fex_file}")
        return 1
    
    logger.info(f"Parsing FEX file: {args.fex_file}")
    
    # Parse FEX
    sections = parse_fex_file(args.fex_file)
    logger.info(f"Found {len(sections)} sections")
    
    # Generate report
    report = FexReport()
    report.sections = sections
    report.hardware_summary = analyze_hardware(sections)
    report.gpio_summary = extract_gpio(sections)
    report.lcd_timings = extract_lcd_timings(sections)
    report.peripherals = extract_peripherals(sections)
    report.warnings = generate_warnings(sections)
    
    # Generate markdown
    md_content = generate_markdown_report(report)
    
    if args.output_md:
        args.output_md.write_text(md_content, encoding='utf-8')
        logger.info(f"Markdown report written to: {args.output_md}")
    else:
        print(md_content)
    
    # Generate JSON
    json_content = {
        'sections': [{'name': s.name, 'parameters': s.parameters} for s in sections],
        'hardware_summary': report.hardware_summary,
        'gpio_summary': report.gpio_summary,
        'lcd_timings': report.lcd_timings,
        'peripherals': report.peripherals,
        'warnings': report.warnings,
    }
    
    if args.output_json:
        args.output_json.write_text(json.dumps(json_content, indent=2), encoding='utf-8')
        logger.info(f"JSON report written to: {args.output_json}")
    
    return 0


if __name__ == '__main__':
    exit(main())
