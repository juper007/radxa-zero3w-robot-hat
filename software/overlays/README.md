# Radxa ZERO 3W Robot HAT Qwiic overlay

This overlay restores the three auxiliary Qwiic ports from the upstream Raspberry Pi Robot HAT while preserving their routed GPIO pairs. J5 remains on the separate hardware I2C3 M0 bus.

## Bus map

| Connector | SDA | SCL | Device-tree alias | Pull-ups |
|---|---|---|---|---|
| J5 | header pin 3 / I2C3 SDA M0 | header pin 5 / I2C3 SCL M0 | hardware I2C3 | shared main-bus pull-ups |
| J6 | pin 7 / GPIO3_C4 | pin 29 / GPIO3_B3 | `i2c10` | R20/R21, 10 kΩ |
| J7 | pin 24 / GPIO4_C6 | pin 21 / GPIO4_C5 | `i2c11` | R34/R35, 10 kΩ |
| J8 | pin 19 / GPIO4_C3 | pin 23 / GPIO4_C2 | `i2c12` | R38/R39, 10 kΩ |

J6 also uses populated 0 Ω links R18/R19. Each auxiliary bus is independent, so devices with the same I2C address may be used simultaneously on different connectors.

## Build

The overlay is self-contained and vendors only the two Linux DT-binding headers it uses. On a Linux host with `cpp` and `dtc`:

```sh
cpp -nostdinc -I software/overlays/include -undef -x assembler-with-cpp \
  software/overlays/radxa-zero3w-robot-hat-qwiic.dts \
  /tmp/radxa-zero3w-robot-hat-qwiic.pp.dts

dtc -@ -Wno-alias_paths -I dts -O dtb \
  -o /tmp/radxa-zero3w-robot-hat-qwiic.dtbo \
  /tmp/radxa-zero3w-robot-hat-qwiic.pp.dts
```

The CI workflow compiles this source with DTC 1.7.0, applies it to `test/rk3566-symbols-base.dts`, treats invalid alias paths as errors, and reads back all three controller nodes and aliases. The resulting DTBO is generated output and is not committed.

## Integration with the existing Robot runtime

The existing J5/audio/UART bring-up remains authoritative and is not duplicated in this overlay. The compatibility reference used for this port is microduck commit `6507d2e960417aaa4ecd38eccf59b2dcf586ecd2`:

- [`i2c3-pihat.dts`](https://github.com/pollen-robotics/microduck/blob/6507d2e960417aaa4ecd38eccf59b2dcf586ecd2/deploy/audio/i2c3-pihat.dts) remuxes I2C3 to M0 on J5 pins 3/5 and disables the FUSB302 node on the vacated M1 pins;
- [`aic3104-i2c3.dts`](https://github.com/pollen-robotics/microduck/blob/6507d2e960417aaa4ecd38eccf59b2dcf586ecd2/deploy/audio/aic3104-i2c3.dts) attaches the codec and I2S3 sound card to that bus;
- Armbian's `uart2-m0` overlay enables the Dynamixel UART.

Load the auxiliary Qwiic overlay in addition to those existing overlays. For the pinned Armbian setup, the logical order is:

```text
uart2-m0 i2c3-pihat aic3104-i2c3 radxa-zero3w-robot-hat-qwiic
```

Install the generated file under the image's Rockchip overlay directory using the prefixed filename `rk3568-radxa-zero3w-robot-hat-qwiic.dtbo`, then add the unprefixed word `radxa-zero3w-robot-hat-qwiic` to `overlays=` in `/boot/armbianEnv.txt`. Preserve any existing overlay words. Other images must use their own documented overlay loader.

This separation is deliberate: J6/J7/J8 use only GPIO-backed buses and do not alter I2C3, the codec, I2S3, UART2 or the FUSB302 node.

## Install prerequisites

- The target kernel must enable `CONFIG_I2C_GPIO` (built-in or module).
- No other enabled overlay or device may claim GPIO3_C4, GPIO3_B3, GPIO4_C6, GPIO4_C5, GPIO4_C3 or GPIO4_C2.
- Install the DTBO using the overlay mechanism documented for the exact Radxa OS image and bootloader. Overlay directories and configuration syntax vary between Radxa OS, Armbian and other images.
- J5 requires the pinned `i2c3-pihat` behavior above. It intentionally disables access to the on-board FUSB302 at address 0x22 while I2C3 is remuxed from M1 to M0; USB-C behavior must therefore be validated separately.

## Runtime acceptance test

After rebooting with the overlay enabled:

```sh
i2cdetect -l
test -e /dev/i2c-10
test -e /dev/i2c-11
test -e /dev/i2c-12
sudo i2cdetect -y 10
sudo i2cdetect -y 11
sudo i2cdetect -y 12
```

Then connect a known 3.3 V Qwiic device to one connector at a time and perform at least one device-specific register read and write on each bus. Release acceptance requires:

1. aliases 10/11/12 enumerate consistently after cold boot;
2. the expected device address appears only on the connector being tested;
3. register reads and writes succeed without I2C timeout, arbitration or stuck-bus messages;
4. simultaneous traffic on J6/J7/J8 succeeds when identical-address devices are attached to separate buses;
5. J5, USB-C, Dynamixel UART and audio continue to operate with all required overlays enabled.

DTBO compilation proves syntax and fixup generation only. Runtime bus ownership, signal integrity and attached-device transfers remain EVT requirements.
