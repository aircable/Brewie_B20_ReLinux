# Brewie AVR Transport

The canonical command and recipe-step reference is maintained with the
[ReBrewieAVR firmware](https://github.com/aircable/ReBrewieAVR/blob/main/AVR_commands.md).

## ReLinux serial interface

The Brewie controller is available as `/dev/ttyS1` at 115200 baud, 8N1. A
host-to-AVR frame has this binary layout:

```text
$ <sequence> <payload-length> <ASCII payload> <checksum/reserved byte> *
```

The original B20 firmware uses a CRC-8 byte calculated over the ASCII payload
with polynomial `0x5e`. ReBrewie retains the byte position but does not validate
it. Accepted commands produce this acknowledgement:

```text
$ 0x01 <sequence> * CR LF
```

The AVR also sends tab-separated status records approximately once per second.

## Diagnostic tools

`/usr/bin/avr-protocol-test` generates the original B20 CRC framing and captures
the raw response. `/usr/bin/avr-valve-test` provides a guarded manual valve
test. Both tools may actuate hardware and must be used only on a supervised,
safe machine.

Firmware installation is handled by `/usr/bin/brewie-upload-fw`:

```sh
brewie-upload-fw read /tmp/b20-existing.hex
brewie-upload-fw write /tmp/ReBrewie.ino.hex
```
