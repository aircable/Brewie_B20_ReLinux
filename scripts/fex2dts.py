#!/usr/bin/env python3
"""
FEX to Device Tree Converter - Generates Device Tree from Allwinner FEX files.

This tool converts script.fex configuration to Linux Device Tree Source (DTS)
format, suitable for use with mainline kernel.
"""

import argparse
import logging
import re
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Allwinner GPIO port to pinctrl bank mapping (for interrupt parent)
PORT_TO_BANK = {
    'PA': 0, 'PB': 1, 'PC': 2, 'PD': 3, 'PE': 4, 'PF': 5, 'PG': 6,
}


def parse_gpio_spec(spec: str) -> Optional[dict]:
    """Parse FEX GPIO specification like 'port:PG03<4><1><default><default>'."""
    if not spec or not spec.startswith("port:"):
        return None
    
    # Extract port letter and pin number (PG03 -> PG, 03)
    match = re.match(r'port:([A-Z]+)(\d+)<(\d+)>', spec)
    if not match:
        return None
    
    port_full, pin_str, func = match.groups()
    bank = PORT_TO_BANK.get(port_full, 0)
    
    return {
        'port': port_full,
        'pin': int(pin_str),
        'bank': bank,
    }


def parse_fex_file(fex_path: Path) -> list[dict]:
    """Parse FEX file into structured data."""
    sections = []
    current_section = None
    
    with open(fex_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            
            if not line or line.startswith(';') or line.startswith('#'):
                continue
            
            section_match = re.match(r'\[(\w+)\]', line)
            if section_match:
                if current_section:
                    sections.append(current_section)
                current_section = {'name': section_match.group(1).lower(), 'parameters': {}}
                continue
            
            if '=' in line and current_section:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if ',' in value:
                    value = [v.strip() for v in value.split(',')]
                elif value.isdigit():
                    value = int(value)
                elif value.startswith('0x'):
                    try:
                        value = int(value, 16)
                    except ValueError:
                        pass
                elif value.startswith('"'):
                    value = value.strip('"')
                
                current_section['parameters'][key] = value
    
    if current_section:
        sections.append(current_section)
    
    return sections


def generate_dts(fex_sections: list[dict], board_name: str) -> str:
    """Generate complete Device Tree Source from FEX sections."""
    sections = {s['name']: s.get('parameters', {}) for s in fex_sections}
    
    lcd0 = sections.get('lcd0_para', {})
    lcd_x = lcd0.get('lcd_x', 480)
    lcd_y = lcd0.get('lcd_y', 272)
    lcd_pwm_freq = lcd0.get('lcd_pwm_freq', 10000)
    lcd_backlight = lcd0.get('lcd0_backlight', 5)
    
    lines = []
    lines.append("// SPDX-License-Identifier: GPL-2.0-or-later")
    lines.append("//")
    lines.append("// Device Tree for Brewie B20")
    lines.append("// Generated from script.fex analysis")
    lines.append("//")
    lines.append("// Based on sun5i-a13-q8-tablet.dts")
    lines.append("// LCD timing from fbset: 480x272 r5g6b5, ~9MHz pixel clock")
    lines.append("// Touch: ft5x06 at 0x38 (I2C2, PG11 interrupt, PC03 reset)")
    lines.append("// RTC: PCF8563 at 0x51 (I2C0)")
    lines.append("// PMIC: AXP209 at 0x34 (I2C0)")
    lines.append("//")
    lines.append("/dts-v1/;")
    lines.append("")
    lines.append('#include "allwinner/sun5i-a13.dtsi"')
    lines.append('#include "allwinner/sunxi-common-regulators.dtsi"')
    lines.append("")
    lines.append('#include <dt-bindings/gpio/gpio.h>')
    lines.append('#include <dt-bindings/pwm/pwm.h>')
    lines.append('#include <dt-bindings/interrupt-controller/irq.h>')
    lines.append("")
    lines.append("/ {")
    lines.append(f'    model = "{board_name.split(",")[0].replace("_", " ").title()} B20";')
    lines.append(f'    compatible = "{board_name}", "allwinner,sun5i-a13";')
    lines.append("")
    lines.append("    aliases {")
    lines.append("        serial0 = &uart1;")
    lines.append("    };")
    lines.append("")
    lines.append("    chosen {")
    lines.append('        stdout-path = "serial0:115200n8";')
    lines.append("    };")
    lines.append("")
    lines.append("    /* LCD backlight - uses PWM0 on PB2 for brightness control */")
    lines.append("    backlight: backlight {")
    lines.append('        compatible = "pwm-backlight";')
    lines.append('        pwms = <&pwm 0 9000 PWM_POLARITY_INVERTED>; /* ~10kHz PWM */')
    lines.append("        brightness-levels = <0 10 20 30 40 50 60 70 80 90 100>;")
    lines.append(f"        default-brightness-level = <{lcd_backlight}>;")
    lines.append('        enable-gpios = <&axp_gpio 1 GPIO_ACTIVE_HIGH>; /* AXP209 GPIO1 (power1) */')
    lines.append("        power-supply = <&reg_vcc3v3>;")
    lines.append("    };")
    lines.append("")
    lines.append("    /* Simple framebuffer for early console */")
    lines.append("    framebuffer-lcd0@40000000 {")
    lines.append('        compatible = "allwinner,simple-framebuffer", "simple-framebuffer";')
    lines.append('        allwinner,pipeline = "de_be0-lcd0";')
    lines.append(f"        reg = <0x40000000 0x{lcd_x * lcd_y * 2:x}>; /* {lcd_x}x{lcd_y}x16bpp */")
    lines.append(f"        width = <{lcd_x}>;")
    lines.append(f"        height = <{lcd_y}>;")
    lines.append(f"        stride = <{lcd_x * 2}>; /* {lcd_x} x 16bpp */")
    lines.append('        format = "r5g6b5";')
    lines.append("        clocks = <&ccu CLK_AHB_LCD>, <&ccu CLK_AHB_DE_BE>, <&ccu CLK_DE_BE>,")
    lines.append("                 <&ccu CLK_TCON_CH0>, <&ccu CLK_DRAM_DE_BE>;")
    lines.append("        /* Timing from fbset output: hfp=10, hbp=5, vfp=3, vbp=8, hspw=30, vspw=5 */")
    lines.append("    };")
    lines.append("};")
    lines.append("")
    
    return "\n".join(lines)


def generate_pinctrl(sections: dict) -> str:
    """Generate pinctrl definitions for LCD RGB24 pins."""
    lines = []
    
    lines.append("/* LCD RGB24 pins (PD0-PD27) - 24-bit color mode */")
    lines.append("&pio {")
    lines.append("    lcd_rgb24_pins: lcd-rgb24-pins {")
    lines.append('        pins = "PD0", "PD1", "PD2", "PD3", "PD4", "PD5", "PD6", "PD7",')
    lines.append('               "PD8", "PD9", "PD10", "PD11", "PD12", "PD13", "PD14", "PD15",')
    lines.append('               "PD16", "PD17", "PD18", "PD19", "PD20", "PD21", "PD22", "PD23",')
    lines.append('               "PD24", "PD25", "PD26", "PD27";')
    lines.append('        function = "lcd0";')
    lines.append("    };")
    lines.append("};")
    lines.append("")
    
    return "\n".join(lines)


def generate_i2c_overlay(sections: dict) -> str:
    """Generate I2C overlay nodes that enable peripherals."""
    lines = []
    
    twi0 = sections.get('twi0_para', {})
    twi2 = sections.get('twi2_para', {})
    pmu = sections.get('pmu_para', {})
    rtc = sections.get('rtc_para', {})
    
    # I2C0 - PMIC (AXP209) and RTC (PCF8563)
    if twi0.get('twi0_used') == 1:
        pmu_addr = pmu.get('pmu_twi_addr', 52)  # Default 0x34
        rtc_addr = rtc.get('rtc_twi_addr', 81)  # Default 0x51
        
        lines.append("&i2c0 {")
        lines.append('    pinctrl-names = "default";')
        lines.append("    pinctrl-0 = <&i2c0_pins>;")
        lines.append('    status = "okay";')
        lines.append("")
        
        if pmu_addr:
            lines.append("    axp209: pmic@34 {")
            lines.append('        compatible = "x-powers,axp209";')
            lines.append(f"        reg = <0x{pmu_addr:x}>;")
            lines.append("        interrupt-parent = <&pio>;")
            lines.append("        interrupts = <0 7 IRQ_TYPE_EDGE_FALLING>; /* PB7 */")
            lines.append("    };")
            lines.append("")
        
        if rtc_addr:
            lines.append("    rtc@51 {")
            lines.append('        compatible = "nxp,pcf8563";')
            lines.append(f"        reg = <0x{rtc_addr:x}>;")
            lines.append("    };")
        
        lines.append("};")
        lines.append("")
        
        # Include axp209 regulators after defining the axp209 label
        lines.append("#include \"allwinner/axp209.dtsi\"")
        lines.append("")
    
    # I2C2 - CTP (ft5x06)
    if twi2.get('twi2_used') == 1:
        ctp = sections.get('ctp_para', {})
        if ctp.get('ctp_used', 0) == 1:
            ctp_int = ctp.get('ctp_int_port', '')
            ctp_rst = ctp.get('rst_port', '')
            gpio_spec = parse_gpio_spec(ctp_int)
            rst_spec = parse_gpio_spec(ctp_rst)
            
            lines.append("&i2c2 {")
            lines.append('    pinctrl-names = "default";')
            lines.append("    pinctrl-0 = <&i2c2_pins>;")
            lines.append('    status = "okay";')
            
            if gpio_spec:
                bank = gpio_spec['bank']
                pin = gpio_spec['pin']
                lines.append("")
                lines.append("    ft5x06@38 {")
                lines.append('        compatible = "edt,edt-ft5x06";')
                lines.append("        reg = <0x38>;")
                lines.append("        interrupt-parent = <&pio>;")
                lines.append(f"        interrupts = <{bank} {pin} IRQ_TYPE_EDGE_FALLING>;")
                if rst_spec:
                    rst_bank = rst_spec['bank']
                    rst_pin = rst_spec['pin']
                    lines.append(f"        reset-gpios = <&pio {rst_bank} {rst_pin} GPIO_ACTIVE_LOW>;")
                lines.append("    };")
            
            lines.append("};")
            lines.append("")
    
    return "\n".join(lines)


def generate_uart_overlay(sections: dict) -> str:
    """Generate UART overlay nodes."""
    lines = []
    
    uart1 = sections.get('uart_para1', {})
    uart2 = sections.get('uart_para3', {})
    
    # UART1 - Debug console (from FEX uart_para1 on PG3/PG4)
    if uart1.get('uart_used') == 1:
        lines.append("&uart1 {")
        lines.append('    pinctrl-names = "default";')
        lines.append("    pinctrl-0 = <&uart1_pg_pins>;")
        lines.append('    status = "okay";')
        lines.append("};")
    
    # UART2 (actually UART3 on PG9/PG10 in FEX uart_para3)
    if uart2.get('uart_used') == 1:
        lines.append("&uart3 {")
        lines.append('    pinctrl-names = "default";')
        lines.append("    pinctrl-0 = <&uart3_pg_pins>;")
        lines.append('    status = "okay";')
        lines.append("};")
    
    return "\n".join(lines)


def generate_mmc_overlay(sections: dict) -> str:
    """Generate MMC overlay nodes."""
    lines = []
    
    mmc0 = sections.get('mmc0_para', {})
    
    if mmc0.get('sdc_used') == 1:
        lines.append("&mmc0 {")
        lines.append('    pinctrl-names = "default";')
        lines.append("    pinctrl-0 = <&mmc0_pins>;")
        lines.append("    bus-width = <4>;")
        lines.append("    cd-gpios = <&pio 5 6 GPIO_ACTIVE_LOW>; /* PF6 */")
        lines.append('    status = "okay";')
        lines.append("};")
    
    return "\n".join(lines)


def generate_spi_overlay(sections: dict) -> str:
    """Generate SPI overlay nodes."""
    lines = []
    
    spi2 = sections.get('spi2_para', {})
    
    if spi2.get('spi_used') == 1:
        lines.append("&spi2 {")
        lines.append('    pinctrl-names = "default";')
        lines.append("    pinctrl-0 = <&spi2_pe_pins>, <&spi2_cs0_pe_pin>;")
        lines.append('    status = "okay";')
        lines.append("")
        lines.append("    spidev@0 {")
        lines.append('        compatible = "spidev";')
        lines.append("        reg = <0>;")
        lines.append("        spi-max-frequency = <1000000>;")
        lines.append("    };")
        lines.append("};")
    
    return "\n".join(lines)


def generate_usb_overlay(sections: dict) -> str:
    """Generate USB overlay nodes."""
    lines = []
    
    usbc0 = sections.get('usbc0', {})
    
    if usbc0.get('usb_used') == 1:
        lines.append("&ehci0 {")
        lines.append('    status = "okay";')
        lines.append("};")
        lines.append("")
        lines.append("&ohci0 {")
        lines.append('    status = "okay";')
        lines.append("};")
    
    return "\n".join(lines)


def generate_pwm_overlay(sections: dict) -> str:
    """Generate PWM overlay."""
    lines = []
    
    lines.append("&pwm {")
    lines.append('    pinctrl-names = "default";')
    lines.append("    pinctrl-0 = <&pwm0_pin>;")
    lines.append('    status = "okay";')
    lines.append("};")
    
    return "\n".join(lines)


def generate_lradc_overlay(sections: dict) -> str:
    """Generate LRADC overlay for keypad."""
    lines = []
    
    lines.append("&lradc {")
    lines.append("    vref-supply = <&reg_vcc3v0>;")
    lines.append('    status = "okay";')
    lines.append("};")
    
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Convert Allwinner FEX to Device Tree Source'
    )
    parser.add_argument(
        'fex_file',
        type=Path,
        help='Path to script.fex file'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=None,
        help='Output DTS file path (default: stdout)'
    )
    parser.add_argument(
        '--board',
        default="brewie,b20",
        help='Board compatible string (default: brewie,b20)'
    )
    
    args = parser.parse_args()
    
    if not args.fex_file.exists():
        logger.error(f"FEX file not found: {args.fex_file}")
        return 1
    
    logger.info(f"Parsing FEX file: {args.fex_file}")
    
    fex_sections = parse_fex_file(args.fex_file)
    logger.info(f"Found {len(fex_sections)} sections")
    
    sections = {s['name']: s.get('parameters', {}) for s in fex_sections}
    
    dts = generate_dts(fex_sections, args.board)
    pinctrl = generate_pinctrl(sections)
    i2c_overlay = generate_i2c_overlay(sections)
    uart_overlay = generate_uart_overlay(sections)
    mmc_overlay = generate_mmc_overlay(sections)
    spi_overlay = generate_spi_overlay(sections)
    usb_overlay = generate_usb_overlay(sections)
    pwm_overlay = generate_pwm_overlay(sections)
    lradc_overlay = generate_lradc_overlay(sections)
    
    # Build complete output with proper blank lines between sections
    overlays = [pinctrl, i2c_overlay, uart_overlay, mmc_overlay, spi_overlay, usb_overlay, pwm_overlay, lradc_overlay]
    output = dts + "\n" + "\n".join(o for o in overlays if o) + "\n"
    
    if args.output:
        args.output.write_text(output, encoding='utf-8')
        logger.info(f"DTS written to: {args.output}")
    else:
        print(output)
    
    return 0


if __name__ == '__main__':
    exit(main())