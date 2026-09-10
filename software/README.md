# Software

Host configuration and hardware validation software for Radxa ZERO 3W.

Planned structure:

- `overlays/` - RK3566/Radxa device-tree overlays
- `setup/` - host configuration scripts
- `test/` - I2C, UART/Dynamixel and audio bring-up utilities

Software must track the hardware revision it was validated against. In particular, UART2 console ownership and I2C3/I2S3 pinmux configuration are part of successful HAT bring-up.
