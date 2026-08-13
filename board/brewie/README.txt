Brewie B20
==========

This directory contains the Buildroot integration for the Brewie B20.

Building
========

Configure Buildroot with:

  make brewie_b20_defconfig

Then build the image with:

  make -j4

QtWebKit build integration
==========================

QtWebKit itself is not source-patched.  Its CMake install places the qmake
module metadata (`qt_lib_webkit*.pri`) below the target sysroot, while the
host qmake used to build qt-webkit-kiosk searches below QT_HOST_DATA.  Without
the Buildroot integration fix, kiosk configuration fails with:

  Project ERROR: Unknown module(s) in QT: webkit webkitwidgets

The permanent fix is the QT5WEBKIT_INSTALL_QMAKE_MODULES post-install-staging
hook in:

  package/qt5/qt5webkit/qt5webkit.mk

The hook copies the generated module metadata into the host qmake module
directory and rewrites its include and library paths to use qmake's target
sysroot variables.  Files repaired or generated below output/ are build
artifacts and are not source inputs to the image.

The GCC processes used for QtWebKit and the kernel have occasionally exited
with transient internal compiler errors during highly parallel builds.  The
same source files compile successfully with reduced parallelism.  Use
`make -j4`; these host-side compiler crashes do not indicate unsupported ARM
instructions on the Allwinner A13.

Result
======

The main output is:

  output/images/sdcard.img

The image contains:

  - U-Boot SPL and U-Boot
  - a VFAT boot partition with the kernel and DTB
  - an ext4 root filesystem

Verified bring-up
==================

The current image has been tested on the B20 hardware with:

  - the power button on PB3/GPIO35 as a Linux gpio-keys input;
  - the hardware startup sequence: hold the power button until the power
    indication appears, then release it;
  - the RGB LCD through sun4i DRM and /dev/fb0;
  - the Qt5 display test: /usr/bin/qt-screen-test;
  - the PWM backlight on PB2/GPIO34 with PB10/GPIO42 as enable.  A known
    working manual setting is:

      echo 9 > /sys/class/backlight/backlight/brightness

  - the EDT FT5x06 touchscreen on I2C2 at 0x38, with PG11 interrupt and PC03
    reset, verified with evtest;
  - the PCF8563 RTC on I2C0 at 0x51;
  - USB host and the RTL8188EU WiFi adapter.

GPIO71/PC7 was tested as a possible power-hold output but is deliberately not
claimed by the Device Tree: a GPIO hog there prevented Linux from booting.
The hardware latch maintains power after the startup button is released.

The AVR UART is enabled in the Device Tree on UART3/PG09-PG10 and appears as
/dev/ttyS1.  The original B20 protocol was verified with the existing AVR
firmware: valve commands use 115200 8N1 and the framed command format
documented in AVR_commands.md.  The B20 valve test was successfully run with
/usr/bin/avr-valve-test.

`avr-protocol-test` starts its receiver before sending the command and streams
the hexadecimal response to the console while saving it to the capture file:

  avr-protocol-test /dev/ttyS1 P112 /tmp/avr-response.hex 15

The original B20 firmware may not emit the status/ACK data until roughly ten
seconds after the UART is opened.  The timeout is configurable; the default is
15 seconds.  This is AVR protocol timing, not Linux UART output buffering.
`P112` is an actuator command and should only be used with the appropriate
valve and test setup.

AVR firmware maintenance
=========================

The image includes avrdude 8.1, configured for the ATmega2560 and the
`wiring` bootloader protocol.  The reset line is PE9/GPIO137.  The early board
init exports it high and creates the compatibility path
`/dev/brewie-mcu-reset`.

Read the existing AVR flash without changing it:

  brewie-upload-fw read /tmp/b20-existing.hex

Upload an Intel HEX image:

  brewie-upload-fw write /tmp/firmware.hex

The legacy short form remains supported:

  brewie-upload-fw /tmp/firmware.hex

The updater opens the UART first with `-x noautoreset -x snooze=250`, then
resets the AVR through GPIO137 while avrdude is waiting.  This is required
because the B20 uses the A13's native UART rather than a USB serial adapter;
the UART cannot provide the DTR/RTS auto-reset signals expected by the generic
wiring driver.

The read-back operation is the recommended first test after enabling the
infrastructure.  It verifies the serial port, reset path, avrdude wiring
programmer, bootloader, and ATmega2560 configuration without erasing flash.
The ReBrewieAVR source is retained separately; its B20 hardware pin mapping
still requires validation before that firmware is flashed onto a B20.

Audio note
==========

The legacy beeper/audio path was investigated but is not included in the
current BSP image.  The beeper was not required for system operation; boot
success is indicated by the power LED instead.
