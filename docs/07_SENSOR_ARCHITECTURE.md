# Sensor Architecture — V1

Status: DESIGNING  
Date: 2026-09-09

## Primary IMU path

For current MicroDuck compatibility, the primary robot orientation source is **not required to be an on-HAT BMI088**. Current MicroDuck software reads the `imu_to_dxl` node on the same DYNAMIXEL bus as all 15 XL330 servos.

Primary V1 path:

```text
Radxa UART2 / DXL_DATA
        |
        +---- 15 x XL330
        |
        `---- imu_to_dxl v2 (primary robot IMU)
```

The current MicroDuck `imu_to_dxl v2` software decoder targets an LSM6DSV16X-based node. The exact external board connector/power requirements must be verified against the hardware actually used before PCB connector lock.

## On-HAT IMU policy

The Pollen Robot HAT includes a BMI088 over I2C. In this Radxa-specific V1 it is reclassified as:

- optional compatibility sensor;
- diagnostic/development sensor;
- DNP-capable footprint/block if board area becomes constrained.

It is **not** part of the minimum current-MicroDuck control-loop requirement.

## I2C3 bus

Radxa physical pins 3/5 are allocated to I2C3 M0 by the MicroDuck-style overlay.

V1 I2C3 uses:
- audio codec control;
- Qwiic / sensor expansion;
- optional BMI088 compatibility block if retained.

Target bus rate: 400 kHz maximum for broad compatibility with the reference codec/sensor design.

Use one intentional pull-up pair for the physical I2C3 bus. Do not populate multiple strong parallel pull-up sets across codec, optional IMU and expansion connectors.

## Qwiic / expansion

Provide at least one compact 3.3 V I2C expansion connector if mechanical space permits:
- +3V3
- GND
- I2C3_SDA
- I2C3_SCL

The connector must not source 5 V onto I2C lines or into Radxa GPIO.

## Design decision

V1 priority order:
1. DXL connector for `imu_to_dxl` — mandatory for current MicroDuck compatibility.
2. I2C3 audio-codec control — mandatory when audio block is populated.
3. I2C expansion — desirable.
4. BMI088 on-HAT — optional/DNP.

This avoids spending scarce 65 x 30 mm board area on a sensor that current robot software does not require while preserving compatibility as a layout option if area permits.

## Validation

Before REVIEW:
- verify external `imu_to_dxl` connector pinout and required voltage;
- verify I2C3 overlay/pins 3/5 in the final Radxa software image;
- verify pull-up equivalent resistance with every populated I2C device;
- verify audio codec and optional BMI088 I2C addresses do not conflict;
- verify Qwiic connector mechanical orientation and 3.3 V labeling.
