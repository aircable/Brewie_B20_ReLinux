# FEX Analysis Report

## Hardware Summary

**soc**: Allwinner A13 (sun5i)
**board_model**: A13-EVB-V1.0
**cpu_clock**: 1008 MHz
**memory**:
  - clock: 408 MHz
  - type: DDR3
  - size: 512 MB
  - bus_width: 16 bit
**storage**:
  - {'type': 'MMC/SD', 'host': 'card_boot0_para'}
  - {'type': 'MMC/SD', 'host': 'mmc0_para'}
  - {'type': 'MMC/SD', 'host': 'mmc1_para'}
  - {'type': 'MMC/SD', 'host': 'mmc2_para'}
**display**:
  - resolution: 480x272
  - pixel_clock_mhz: 9
  - timing_ht: 525
  - timing_hbp: 40
  - timing_hspw: 30
  - timing_vt: 576
  - timing_vbp: 8
  - timing_vspw: 5
**pmic**: AXP20x (likely AXP209)
**dcdc2_voltage**: 1400 mV

## GPIO Summary

### lcd0_para
- lcd_power: port:PB10<1><0><default><1>
- lcd_pwm: port:PB02<2><0><default><default>
- lcdd0: port:PD00<2><0><default><default>
- lcdd1: port:PD01<2><0><default><default>
- lcdd2: port:PD02<2><0><default><default>
- lcdd3: port:PD03<2><0><default><default>
- lcdd4: port:PD04<2><0><default><default>
- lcdd5: port:PD05<2><0><default><default>
- lcdd6: port:PD06<2><0><default><default>
- lcdd7: port:PD07<2><0><default><default>
- lcdd8: port:PD08<2><0><default><default>
- lcdd9: port:PD09<2><0><default><default>
- lcdd10: port:PD10<2><0><default><default>
- lcdd11: port:PD11<2><0><default><default>
- lcdd12: port:PD12<2><0><default><default>
- lcdd13: port:PD13<2><0><default><default>
- lcdd14: port:PD14<2><0><default><default>
- lcdd15: port:PD15<2><0><default><default>
- lcdd16: port:PD16<2><0><default><default>
- lcdd17: port:PD17<2><0><default><default>
- lcdd18: port:PD18<2><0><default><default>
- lcdd19: port:PD19<2><0><default><default>
- lcdd20: port:PD20<2><0><default><default>
- lcdd21: port:PD21<2><0><default><default>
- lcdd22: port:PD22<2><0><default><default>
- lcdd23: port:PD23<2><0><default><default>
- lcdclk: port:PD24<2><0><default><default>
- lcdde: port:PD25<2><0><default><default>
- lcdhsync: port:PD26<2><0><default><default>
- lcdvsync: port:PD27<2><0><default><default>
### gpio_para
- gpio_pin_1: port:PB03<0><default><default><default>
- gpio_pin_2: port:PB15<0><default><default><default>
- gpio_pin_3: port:PB04<1><default><default><1>
- gpio_pin_4: port:PB16<1><default><default><0>
- gpio_pin_5: port:PB02<1><default><default><default>
- gpio_pin_6: port:PE09<1><default><default><1>
- gpio_pin_7: port:PB10<1><default><default><1>
- gpio_pin_8: port:PC07<1><default><default><1>
- gpio_pin_9: port:PG12<1><default><default><0>
### gpio_init
- pin_3: port:PB04<1><default><default><1>
- pin_7: port:PB10<1><default><default><1>
- pin_8: port:PC07<1><default><default><1>

## LCD Timings

### lcd0_para
- lcd_x: 480
- lcd_y: 272
- lcd_dclk_freq: 9
- lcd_ht: 525
- lcd_hbp: 40
- lcd_hv_hspw: 30
- lcd_vt: 576
- lcd_vbp: 8
- lcd_hv_vspw: 5
- lcd_pwm_freq: 10000
- lcd_pwm_pol: 1

## Peripherals

### I2C (twi_para)
- used: unknown
- twi_port: 0
- twi_scl: port:PB00<2><1><default><default>
- twi_sda: port:PB01<2><1><default><default>
### UART (uart_para)
- used: unknown
- uart_debug_port: 1
- uart_debug_tx: port:PG03<4><1><default><default>
- uart_debug_rx: port:PG04<4><1><default><default>
### NAND Flash (nand_para)
- used: 1
- nand_used: 1
- nand_we: port:PC00<2><default><default><default>
- nand_ale: port:PC01<2><default><default><default>
- nand_cle: port:PC02<2><default><default><default>
- nand_ce1: port:PC03<2><default><default><default>
- nand_ce0: port:PC04<2><default><default><default>
- nand_nre: port:PC05<2><default><default><default>
- nand_rb0: port:PC06<2><default><default><default>
- nand_rb1: port:PC07<2><default><default><default>
- nand_d0: port:PC08<2><default><default><default>
- nand_d1: port:PC09<2><default><default><default>
- nand_d2: port:PC10<2><default><default><default>
- nand_d3: port:PC11<2><default><default><default>
- nand_d4: port:PC12<2><default><default><default>
- nand_d5: port:PC13<2><default><default><default>
- nand_d6: port:PC14<2><default><default><default>
- nand_d7: port:PC15<2><default><default><default>
- nand_wp: 
- nand_ce2: 
- nand_ce3: 
- nand_ce4: 
- nand_ce5: 
- nand_ce6: 
- nand_ce7: 
- nand_spi: 
- nand_ndqs: port:PC19<2><default><default><default>
### I2C (twi0_para)
- used: 1
- twi0_used: 1
- twi0_scl: port:PB00<2><default><default><default>
- twi0_sda: port:PB01<2><default><default><default>
### I2C (twi1_para)
- used: unknown
- twi1_used: 0
- twi1_scl: port:PB15<2><default><default><default>
- twi1_sda: port:PB16<2><default><default><default>
### I2C (twi2_para)
- used: unknown
- twi2_used: 1
- twi2_scl: port:PB17<2><default><default><default>
- twi2_sda: port:PB18<2><default><default><default>
### UART (uart_para0)
- used: 0
- uart_used: 0
- uart_port: 0
- uart_type: 2
- uart_tx: port:PB19<2><1><default><default>
- uart_rx: port:PB20<2><1><default><default>
### UART (uart_para1)
- used: 1
- uart_used: 1
- uart_port: 1
- uart_type: 2
- uart_tx: port:PG03<4><1><default><default>
- uart_rx: port:PG04<4><1><default><default>
### UART (uart_para3)
- used: 1
- uart_used: 1
- uart_port: 2
- uart_type: 2
- uart_tx: port:PG09<3><1><default><default>
- uart_rx: port:PG10<3><1><default><default>
### SPI (spi1_para)
- used: 0
- spi_used: 0
- spi_cs0: port:PG09<2><default><default><default>
- spi_cs1: port:PG13<2><default><default><default>
- spi_sclk: port:PG10<2><default><default><default>
- spi_mosi: port:PG11<2><default><default><default>
- spi_miso: port:PG12<2><default><default><default>
### SPI (spi2_para)
- used: 1
- spi_used: 1
- spi_cs0: port:PE00<4><default><default><default>
- spi_sclk: port:PE01<4><default><default><default>
- spi_mosi: port:PE02<4><default><default><default>
- spi_miso: port:PE03<4><default><default><default>
### SPI (spi_devices)
- used: unknown
- spi_dev_num: 1
### SPI (spi_board0)
- used: unknown
- modalias: spidev
- max_speed_hz: 1000000
- bus_num: 2
- chip_select: 0
- mode: 3
- full_duplex: 0
- manual_cs: 0
### Resistive Touch (rtp_para)
- used: 0
- rtp_used: 0
- rtp_screen_size: 5
- rtp_regidity_level: 5
- rtp_press_threshold_enable: 0
- rtp_press_threshold: 8000
- rtp_sensitive_level: 15
- rtp_exchange_x_y_flag: 0
### Capacitive Touch (ctp_para)
- used: 1
- ctp_used: 1
- ctp_name: ft5x_ts
- ctp_twi_id: 2
- ctp_twi_addr: 56
- ctp_screen_max_x: 480
- ctp_screen_max_y: 272
- ctp_revert_x_flag: 0
- ctp_revert_y_flag: 0
- ctp_exchange_x_y_flag: 0
- ctp_int_port: port:PG11<6><default><default><default>
- ctp_wakeup: 
- ctp_io_port: port:PG11<0><default><default><default>
- rst_port: port:PC03<1><default><default><default>
### CSI/DVP Camera (csi0_para)
- used: 0
- csi_used: 0
- csi_mode: 0
- csi_dev_qty: 1
- csi_stby_mode: 1
- csi_mname: gc0308
- csi_twi_id: 2
- csi_twi_addr: 66
- csi_if: 0
- csi_vflip: 0
- csi_hflip: 1
- csi_iovdd: 
- csi_avdd: 
- csi_dvdd: 
- csi_flash_pol: 1
- csi_mname_b: 
- csi_twi_id_b: 1
- csi_twi_addr_b: 120
- csi_if_b: 0
- csi_vflip_b: 1
- csi_hflip_b: 0
- csi_iovdd_b: 
- csi_avdd_b: 
- csi_dvdd_b: 
- csi_flash_pol_b: 1
- csi_pck: port:PE00<3><default><default><default>
- csi_ck: port:PE01<3><default><default><default>
- csi_hsync: port:PE02<3><default><default><default>
- csi_vsync: port:PE03<3><default><default><default>
- csi_d0: port:PE04<3><default><default><default>
- csi_d1: port:PE05<3><default><default><default>
- csi_d2: port:PE06<3><default><default><default>
- csi_d3: port:PE07<3><default><default><default>
- csi_d4: port:PE08<3><default><default><default>
- csi_d5: port:PE09<3><default><default><default>
- csi_d6: port:PE10<3><default><default><default>
- csi_d7: port:PE11<3><default><default><default>
- csi_reset: port:power3<1><default><default><0>
- csi_power_en: 
- csi_stby: port:PB10<1><default><default><1>
- csi_flash: 
- csi_af_en: 
- csi_reset_b: 
- csi_power_en_b: 
- csi_stby_b: 
- csi_flash_b: 
- csi_af_en_b: 
### CSI/DVP Camera (csi1_para)
- used: 0
- csi_used: 0
- csi_mode: 0
- csi_dev_qty: 1
- csi_stby_mode: 1
- csi_mname: 
- csi_twi_id: 1
- csi_twi_addr: 186
- csi_if: 0
- csi_vflip: 0
- csi_hflip: 0
- csi_iovdd: 
- csi_avdd: 
- csi_dvdd: 
- csi_flash_pol: 1
- csi_mname_b: 
- csi_twi_id_b: 1
- csi_twi_addr_b: 120
- csi_if_b: 0
- csi_vflip_b: 1
- csi_hflip_b: 0
- csi_iovdd_b: 
- csi_avdd_b: 
- csi_dvdd_b: 
- csi_flash_pol_b: 1
- csi_reset: 
- csi_power_en: 
- csi_stby: 
- csi_flash: 
- csi_af_en: 
- csi_reset_b: 
- csi_power_en_b: 
- csi_stby_b: 
- csi_flash_b: 
- csi_af_en_b: 
### MMC/SD (mmc0_para)
- used: unknown
- sdc_used: 1
- sdc_detmode: 3
- bus_width: 4
- sdc_d1: port:PF00<2><1><2><default>
- sdc_d0: port:PF01<2><1><2><default>
- sdc_clk: port:PF02<2><1><2><default>
- sdc_cmd: port:PF03<2><1><2><default>
- sdc_d3: port:PF04<2><1><2><default>
- sdc_d2: port:PF05<2><1><2><default>
- sdc_det: port:PG00<0><0><default><default>
- sdc_use_wp: 0
- sdc_wp: 
### MMC/SD (mmc1_para)
- used: unknown
- sdc_used: 0
- sdc_detmode: 
- bus_width: 
- sdc_cmd: 
- sdc_clk: 
- sdc_d0: 
- sdc_d1: 
- sdc_d2: 
- sdc_d3: 
- sdc_det: 
- sdc_use_wp: 
- sdc_wp: 
### MMC/SD (mmc2_para)
- used: unknown
- sdc_used: 0
- sdc_detmode: 3
- bus_width: 4
- sdc_cmd: port:PE08<4><1><2><default>
- sdc_clk: port:PE09<4><1><2><default>
- sdc_d0: port:PE04<4><1><2><default>
- sdc_d1: port:PE05<4><1><2><default>
- sdc_d2: port:PE06<4><1><2><default>
- sdc_d3: port:PE07<4><1><2><default>
- sdc_det: 
- sdc_use_wp: 0
- sdc_wp: 
### USB (usbc0)
- used: 1
- usb_used: 1
- usb_port_type: 2
- usb_detect_type: 1
- usb_id_gpio: port:PG02<0><1><default><default>
- usb_det_vbus_gpio: port:PG01<0><0><default><default>
- usb_drv_vbus_gpio: port:PG13<1><0><default><0>
- usb_host_init_state: 1
### USB (usbc1)
- used: 1
- usb_used: 1
- usb_port_type: 1
- usb_detect_type: 0
- usb_id_gpio: 
- usb_det_vbus_gpio: 
- usb_drv_vbus_gpio: port:PG05<1><0><default><0>
- usb_host_init_state: 1
### USB (usb_feature)
- used: unknown
- vendor_id: 6353
- mass_storage_id: 1
- adb_id: 2
- manufacturer_name: USB Developer
- product_name: Android
- serial_number: 20080411
### USB (usb_wifi_para)
- used: unknown
- usb_wifi_used: 1
- usb_wifi_usbc_num: 1
### Audio (audio_para)
- used: 1
- audio_used: 1
- capture_used: 1
- playback_used: 1
- audio_lr_change: 0
### IR Remote (ir_para)
- used: 0
- ir_used: 0
- ir0_rx: port:PB04<2><default><default><default>
### PWM (pwm0_para)
- used: 0
- pwm_used: 0
- pwm_period: 10000
- pwm_duty_percent: 99

## Warnings

- WARNING: [jtag_para] jtag_ms = port:PF00<4><1><default><default>
- WARNING: [jtag_para] jtag_ck = port:PF05<4><1><default><default>
- WARNING: [jtag_para] jtag_do = port:PF03<4><1><default><default>
- WARNING: [jtag_para] jtag_di = port:PF01<4><1><default><default>
- WARNING: [twi0_para] twi0_used = 1
- WARNING: [twi0_para] twi0_scl = port:PB00<2><default><default><default>
- WARNING: [twi0_para] twi0_sda = port:PB01<2><default><default><default>
- WARNING: [twi1_para] twi1_used = 0
- WARNING: [twi1_para] twi1_scl = port:PB15<2><default><default><default>
- WARNING: [twi1_para] twi1_sda = port:PB16<2><default><default><default>
- WARNING: [twi2_para] twi2_used = 1
- WARNING: [twi2_para] twi2_scl = port:PB17<2><default><default><default>
- WARNING: [twi2_para] twi2_sda = port:PB18<2><default><default><default>
- WARNING: [spi_board0] modalias = spidev
- WARNING: [spi_board0] max_speed_hz = 1000000
- WARNING: [spi_board0] bus_num = 2
- WARNING: [spi_board0] chip_select = 0
- WARNING: [spi_board0] mode = 3
- WARNING: [spi_board0] full_duplex = 0
- WARNING: [spi_board0] manual_cs = 0