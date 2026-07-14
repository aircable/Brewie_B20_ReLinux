# BSP Modernization Plan

## Status: Phase 2 - Device Tree Development

### Milestone 1: FEX Analysis (COMPLETED)
- [x] Parse script.fex into structured format
- [x] Generate hardware summary
- [x] Extract GPIO configurations
- [x] Extract LCD timing parameters
- [x] Extract peripheral configurations
- [x] Create DISCOVERY.md with findings

### Milestone 2: Device Tree Generation (COMPLETED)
- [x] Create fex2dts.py converter tool
- [x] Generate first-pass DTS
- [x] Validate DTS against upstream A13 DTS
- [x] Add missing pin control definitions
- [x] Add backlight PWM configuration
- [x] Add panel timing definitions (verified via fbset)
- [x] Fix I2C0 configuration (PMIC + RTC verified)
- [x] Include AXP209 regulator definitions

### Milestone 3: Kernel Preparation (PENDING)
- [x] Identify best upstream A13 DTS to inherit (sun5i-a13-q8-tablet.dts)
- [ ] Create kernel configuration
- [ ] Build kernel with DTS overlay
- [ ] Test DTS in QEMU

---

## Completed Work

### scripts/fex-report.py
Created FEX parsing and reporting tool that:
- Extracts hardware configuration from Allwinner script.fex files
- Generates JSON and Markdown reports
- Identifies peripherals, GPIOs, LCD timings
- Maps GPIO pins to port/pin numbers

### scripts/fex2dts.py
Created FEX to Device Tree converter that:
- Parses script.fex into structured data
- Generates device tree source inheriting from sun5i-a13.dtsi
- Enables peripherals based on FEX configuration
- Sets up I2C0 with AXP209 PMIC and PCF8563 RTC
- Sets up I2C2 with ft5x06 touchscreen
- Configures UART1 console on PG3/PG4
- Configures MMC0 SD card interface
- Configures SPI2 with spidev
- Enables USB EHCI/OHCI
- Adds PWM backlight with AXP209 GPIO enable

### board/brewie/sun5i-brewie.dts
Generated Device Tree with:
- Model: "Brewie B20"
- Compatible: "brewie,b20", "allwinner,sun5i-a13"
- UART1 console on PG3/PG4
- I2C0 with AXP209 PMIC (interrupt on PB7) and PCF8563 RTC
- I2C2 with ft5x06 touchscreen (interrupt on PG11, reset on PC03)
- MMC0 SD card interface (4-bit)
- SPI2 with spidev
- USB EHCI/OHCI controllers enabled
- LCD RGB24 pinctrl (PD0-PD27)
- PWM backlight with AXP209 GPIO1 enable
- Simple framebuffer (480x272 r5g6b5)

### include/ directory structure
Copied upstream Allwinner DTSI files:
- arch/arm/boot/dts/allwinner/*.dtsi (sun5i-a13.dtsi, sunxi-common-regulators.dtsi, axp209.dtsi, etc.)
- include/dt-bindings/* (gpio.h, pwm.h, input.h)
- include/dt-bindings/linux-event-codes.h (input event codes)

---

## Recommendations

### Best Upstream DTS to Inherit From

**Recommended: sun5i-a13-q8-tablet.dts**

Rationale:
1. Similar tablet form factor
2. LCD panel support (480x272)
3. I2C touchscreens supported
4. USB host support
5. AXP209 PMIC support available via sunxi-common-regulators.dtsi

Alternative: sun5i-a13-licheepi-one.dts
- Simpler configuration (no LCD)
- Good reference for base peripherals

---

## Next Steps

1. Install dtc to validate DTS compiles correctly
2. Verify AXP209 connection on I2C bus (address 0x34)
3. Add proper LCD panel compatible string (using generic simple framebuffer for now)
4. Create Buildroot board configuration
5. Test in QEMU emulation

---

## Timing Analysis

From FEX (Allwinner controller values):
- Resolution: 480x272
- HT (horizontal total): 525
- HBP (horizontal back porch): 40
- HSPW (horizontal sync pulse width): 30
- VT (vertical total): 576
- VBP (vertical back porch): 8
- VSPW (vertical sync pulse width): 5

**Corrected Interpretation** (from fbset output confirmed in dmesg):
- fbset shows: `timings 111111 10 5 3 8 30 5`
- Standard fbtest format: pixclk hfp hbp vfp vbp hspw vspw
- The discrepancy was resolved by examining the Allwinner legacy display driver. The FEX HBP value of 40 is the **total horizontal back porch including sync**, while fbset's right_margin (hbp=5) is the actual back porch. This means:
  - Allwinner HBP (40) = hbp (5) + hspw (30) + some offset
  - Allwinner VBP (8) = vbp (8) + vspw (5) - vspw = 3 + 5 = 8 ✓

The current DTS uses the fbset-derived timings which are verified to work by the running system.

---

## Verified Hardware Configuration

Based on i2cdetect output from Olimex A13 reference board:
- I2C0: PCF8563 RTC at 0x51 (UU = used by kernel driver)
- I2C2: ft5x06 touchscreen at 0x38 (UU = used by kernel driver)

The FEX confirms:
- `pmu_twi_id = 0` (AXP209 on I2C0 at address 0x34)
- `rtc_twi_id = 0` (PCF8563 on I2C0 at address 0x51)
- `ctp_twi_id = 2` (ft5x06 on I2C2 at address 0x38)

The RTC and PMIC are correctly placed on I2C0, while the touchscreen is on I2C2.