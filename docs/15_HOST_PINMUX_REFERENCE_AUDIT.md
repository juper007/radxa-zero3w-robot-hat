# 15 — Host header and pinmux reference audit

## Disposition

Reference source: `e1e0c2874f83040acaa332591e51280cd8e7147a`.
This review compares the official ZERO 3W V1.11 and V1.12 schematic publications,
the official web header table, freshly regenerated HAT netlist, and pinned
vendor-family device-tree sources. No connected physical host, board revision
photo, OS image, live DTB or boot log was supplied. **Fabrication-ready: no.**

All 40 numbered J4 contacts were enumerated (MP is separate). No active HAT
pin allocation conflict was found against these references. The evidence
snapshot is [host_pin_reference_audit.json](../validation/strict_port/host_pin_reference_audit.json):
exact PDF URLs/hashes, netlist hash, every pin and its directly connected nodes.
It is an audit snapshot, not a new executable CI gate or physical continuity test.
PDF sheet 20 was text-extracted; it was not used to approve mating orientation
or mechanical pin-1 registration. The actual purchased host must still be identified.

## Header allocation

GPIO signals use the documented 3.3 V domain; the public documentation gives
3.63 V as GPIO maximum. This is not permission for 5 V signaling or an approved
power-off injection limit. Rails, startup behavior and available current remain
separate electrical gates.

| J4 contacts | Reference host identity / selected function | HAT use |
|---|---|---|
| 1, 17 | VCC3V3_SYS | +3V3 sensor/logic supply, not just a sense input |
| 2, 4 | +5V_INPUT | HAT +5V supplies host; no simultaneous USB-C/battery power |
| 6, 9, 14, 20, 25, 30, 34, 39 | GND | Common ground |
| 3 / 5 | GPIO1_A0 / A1, I2C3 M0, mux 1 | SDA / SCL to J5, U2, U11 |
| 7 / 29 | GPIO3_C4 / B3 | J6 SDA / SCL through populated R18/R19 |
| 8 / 10 | GPIO0_D1 / D0, UART2 M0, mux 1 | Dynamixel TX / RX |
| 11 | GPIO3_A1 | Active-HIGH AMP_ENABLE through R45; no second owner |
| 12 / 35 | GPIO3_A3 / A4, I2S3 M0, mux 4 | U2 BCLK / WCLK |
| 15 | GPIO3_B0 | U11 INT1 through populated R25; not a spare output |
| 19 / 23 | GPIO4_C3 / C2 | J8 SDA / SCL |
| 24 / 21 | GPIO4_C6 / C5 | J7 SDA / SCL |
| 27 / 28 | GPIO4_B2 / B3, I2C4 M0, mux 1 | Preserved DNP EEPROM path |
| 31 | GPIO3_B4 | Battery presence: LOW=present, host-referenced Q3 collector |
| 38 / 40 | GPIO3_A6 / A5, I2S3 M0, mux 4 | U2 DOUT→host SDI / host SDO→U2 DIN |
| 13, 16, 18, 22, 26, 32, 33, 36, 37 | HAT intentionally unconnected | No new peripheral allocation |

### Source limitations and discrepancies

- The current web table lists UART3 but omits I2C3 on pins 3/5. The pinned
  vendor pinctrl source independently establishes GPIO1_A0/A1 as I2C3 M0,
  function 1. A missing table entry is not proof that hardware I2C is unavailable.
- The web table calls pin 26 NC; both reference schematic sheet-20 publications
  name GPIO4_D1. HAT pin 26 is explicitly unconnected, so this disagreement
  does not affect the present port. Do not allocate it without resolving the
  actual host revision and population.
- Pins 27/28 can be physically reassigned to USB2 HOST2 by changing host
  R32/R39 versus R45/R46. This port assumes factory I2C/GPIO routing; software
  mux changes cannot undo that solder modification.
- Matching these two reference documents does not identify the user's physical
  board or prove all host revisions equivalent.

## I2C3 and USB-C ownership

The pinned vendor board DTS selects `i2c3m1_xfer`, GPIO3_B5/B6, mux 4,
with `fusb302@22`. The pinned MicroDuck `i2c3-pihat` overlay selects M0,
sets 400000 Hz, and disables the exact path
`/i2c@fe5c0000/fusb302@22`. These are alternative pin groups of **one controller**,
not two independent I2C buses. Do not leave the M1 device probing the HAT bus.

The path and symbols are base-tree-specific. MicroDuck's comments report
working default-5-V USB-C behavior on its tested vendor 6.1.115 image; that is
not validation of this HAT, the user's image, all Type-C roles, orientation,
or every charger. Disabling FUSB302 is not a reverse-current safeguard and
never relaxes the USB-C/HAT-battery mutual-exclusion rule.

Before installation, compile/apply the complete selected overlay set to the
**actual image DTB**, then read back I2C3 status, 400000 clock, resolved M0
pin tuples, disabled FUSB302, and any Type-C endpoint/extcon references.
Reject a missing target or unresolved symbol; do not silently skip a fragment.
Runtime rise-time/transfer testing is required before approving 400 kHz.

## UART2, auxiliary GPIO buses and audio

- Vendor `uart2-m0` enables UART2 with `uart2m0_xfer` and disables
  `fiq_debugger`. It does not prove the bootloader, kernel `console=` and
  userspace getty have released that UART. Confirm all three before 1 Mbps
  Dynamixel traffic; disabling getty alone is insufficient.
- J6/J7/J8 require GPIO ownership, not hardware I2C5 or SPI3/I2S3 M1 ownership.
  Pin 29 is also an I2C5 candidate, but pin 31 is battery sensing; do not enable
  I2C5 M0 on this HAT. Keep aliases 10/11/12 and all three populated ports.
- `aic3104-i2c3` enables `i2s3_2ch` but relies on the base tree for its pinctrl.
  Confirm resolved M0 pins 12/35/38/40 on the actual merged DTB; enabling the
  controller alone is not proof of correct mux selection.
- The HAT already has **Y1, 12 MHz**, whose OUT pin 3 directly drives U2 MCLK
  pin 1. J4 pin 13 is unconnected. The overlay describes this physical source
  with a 12000000-Hz fixed clock and separately requests 12288000 Hz for the
  CPU DAI system clock. These are different clocks, not a frequency typo.
  CPU DAI is bit/frame master. Codec PLL configuration, capture/playback,
  sample rate and physical clock frequencies still require runtime evidence.
- AMP_ENABLE remains opt-in on corrected Stage 2 hardware. Pin 15 is the IMU
  interrupt route, not an available substitute amplifier GPIO.

## Executed checks

- KiCad 10.0.6 native strict-port regeneration: **PASS**, no tracked evidence
  drift, zero DRC findings. Existing accepted ERC/parity policy remains intact.
- `hardware/kicad/test_qwiic_functional_parity.py`: **PASS**.
- `software/overlays/test/test_amp_enable_overlay.py`, DTC 1.7.0:
  **PASS**, synthetic base including missing-card rejection.
- The existing CI Qwiic cpp/dtc/fdtoverlay sequence and compatible/alias
  readback: **PASS**, synthetic base. This is not a real-image integration pass.

The stopped `strict-ci-linux-34786194068` container was restarted to run the
Linux checks. No OS image was installed, no hardware files were changed,
and no manufacturer release was generated.

## Remaining acceptance evidence

| Gate | Classification | Required evidence |
|---|---|---|
| Reference header and selected mux identities | Digitally checked within stated reference scope | Snapshot and pinned sources below |
| Exact purchased host revision / assembly orientation | External identification + physical verification pending | Board marking/photo, SKU, connector pin-1 continuity |
| Actual image DTB + complete overlay set | Runtime/firmware validation pending | Image/kernel hashes, merged DTB readback, pin ownership |
| I2C3/J5 and J6/J7/J8 | Runtime + physical measurement pending | Per-port known-device transfers, rise times, no conflicts |
| UART2 / I2S3 / amplifier | Runtime + physical measurement pending | Console-free 1 Mbps traffic, audio clocks/capture/playback, scoped safe enable |
| USB-C after FUSB302 disable | Runtime + physical measurement pending | Role/orientation/source behavior under single-source power |
| J4 land and full connector/spacer stack | External approval + physical measurement pending | Vendor/assembler acceptance, qualified stack; 4 mm CAD case remains rejected |

## Sources

1. [Official hardware interface](https://docs.radxa.com/en/zero/zero3/hardware-design/hardware-interface), including GPIO voltage and optional USB resistor routing.
2. [ZERO 3W V1.11 schematic, 20250116 publication](https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_schematic_v1.11_20250116.pdf), sheet 20; SHA-256 in snapshot.
3. [ZERO 3W V1.12 schematic, 20250116 publication](https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_schematic_v1.12_20250116.pdf), sheet 20; SHA-256 in snapshot.
4. [Vendor-family RK3568 pinctrl](https://github.com/armbian/linux-rockchip/blob/bd032d59a096344a1f29acf9965d8c46f9a847a8/arch/arm64/boot/dts/rockchip/rk3568-pinctrl.dtsi), shared pinctrl reference used for RK3566.
5. [Vendor ZERO3 board DTS](https://github.com/armbian/linux-rockchip/blob/bd032d59a096344a1f29acf9965d8c46f9a847a8/arch/arm64/boot/dts/rockchip/rk3566-radxa-zero3.dtsi). This commit is an independent reference, not an identified deployed kernel.
6. [Vendor UART2 M0 overlay](https://github.com/armbian/linux-rockchip/blob/bd032d59a096344a1f29acf9965d8c46f9a847a8/arch/arm64/boot/dts/rockchip/overlay/rk3568-uart2-m0.dts).
7. [Pinned MicroDuck I2C3 overlay](https://github.com/pollen-robotics/microduck/blob/6507d2e960417aaa4ecd38eccf59b2dcf586ecd2/deploy/audio/i2c3-pihat.dts).
8. [Pinned MicroDuck audio overlay](https://github.com/pollen-robotics/microduck/blob/6507d2e960417aaa4ecd38eccf59b2dcf586ecd2/deploy/audio/aic3104-i2c3.dts).
