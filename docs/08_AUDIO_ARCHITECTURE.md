# Audio Architecture — V1

Status: DESIGNING  
Date: 2026-09-09

## Goal

Preserve the useful audio capability of the Pollen Robot HAT while adapting it to Radxa ZERO 3W I2S3 and the current 5 V power architecture.

## Reference implementation

Upstream Pollen hardware uses:
- U2 `TLV320AIC3104IRHBR` audio codec
- U1 `PAM8406D` speaker amplifier
- Y1 12 MHz oscillator
- on-board MEMS microphone
- external speaker / microphone connectors

The exact analog component values and codec pin wiring must be recovered from upstream `audio.kicad_sch` before REVIEW rather than reconstructed from memory.

## Radxa host interface

Physical header allocation already reserved by the project:
- pin 12: `I2S3_BCLK`
- pin 35: `I2S3_LRCLK`
- pin 38: `I2S3_SDI` — codec/microphone data toward host
- pin 40: `I2S3_SDO` — host data toward codec
- pins 3/5: `I2C3_SDA` / `I2C3_SCL` for codec control
- pin 17/1: `+3V3` logic reference where appropriate

## V1 block diagram

```text
Radxa I2C3 ----------------------> TLV320AIC3104 control
Radxa I2S3 BCLK/LRCLK ----------> TLV320AIC3104 digital audio
Radxa I2S3 SDO ------------------> codec DAC path
Radxa I2S3 SDI <------------------ codec ADC path
                                      ^
                                      |
                                  MEMS / ext mic

codec line/headphone output -> PAM8406D -> speaker connector
```

## Clocking

Upstream BOM contains a 12 MHz oscillator. Current Radxa/MicroDuck notes also reference a fixed codec MCLK arrangement. V1 will preserve an explicit MCLK source option until the final Radxa I2S3 clocking/overlay is bench-verified.

Do not assume pin 13 MCLK alone is sufficient until the final device-tree/audio driver configuration is validated.

## Power partitioning

- Codec digital/control: 3.3 V-compatible domain as required by datasheet/reference design.
- Analog rails must follow the codec/reference design exactly.
- Speaker amplifier uses the robot 5 V system rail only after noise/current review.
- Audio return currents must not share a narrow path with servo branch returns.
- Use local ferrite/filtering where supported by the recovered reference circuit.

## Layout rules

- Codec and microphone live in the quiet side of the PCB, away from XT60/fuse/MOSFET and servo connectors.
- Keep microphone away from inductor/switching fields and speaker-current traces.
- Keep analog input traces short and guarded by ground where practical.
- Maintain a continuous reference plane; do not split ground blindly.
- Route I2S as short digital signals over solid ground and avoid long parallel runs beside DXL_DATA.
- Speaker traces are differential/high-current audio paths and should not pass through the microphone area.

## V1 priority

1. Codec control and bidirectional I2S.
2. On-board MEMS microphone.
3. Speaker amplifier/output.
4. External microphone connector.
5. Optional compatibility details not required by current MicroDuck software.

## Fabrication blockers

Before audio sheet can move to REVIEW:
- recover exact TLV320AIC3104 pin mapping from upstream source;
- recover codec power/decoupling/filter values;
- recover PAM8406D input/output network;
- verify MEMS microphone part/pinout and voltage domain;
- verify external 12 MHz oscillator topology;
- verify Radxa audio overlay / I2S3 clock roles;
- run KiCad ERC;
- perform analog-layout review after placement.
