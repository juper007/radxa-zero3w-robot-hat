# Hardware

## Active strict-port design

The active KiCad project is a single-board derivative of Pollen Robotics' `elec_RPI_Robot_HAT` at upstream commit `23eab11927f95ceca0dfa35bf182caeb7db39ea0`.

- `kicad/radxa_zero3w_robot_hat.kicad_pro` — project
- `kicad/radxa_zero3w_robot_hat.kicad_sch` — top-level schematic
- `kicad/radxa_zero3w_robot_hat.kicad_pcb` — routed 65.00 × 30.90 mm Edge.Cuts-centerline PCB (approximately 65 × 31 mm)
- Fixed order stackup — 4-layer FR-4, 1.0 mm, 70/35/35/70 µm copper, ENIG
- `kicad/main.kicad_sch` — 40-pin header and board integration
- `kicad/power.kicad_sch` / `pwr_supply_charge.kicad_sch` — upstream single-board power concept with local C45 input-bypass correction
- `kicad/dynamixel.kicad_sch` — upstream TTL/RS-485 interface and connectors
- `kicad/sensors.kicad_sch` — upstream BMI088 and Qwiic circuitry
- `kicad/audio.kicad_sch` — upstream codec, microphone and speaker circuitry

There is no active power daughterboard. The earlier split design is isolated on `archive/v027-split-hat`.

## Applied host changes

Critical nets retain their upstream physical header pins and routed copper while using Radxa names:

- pins 3/5 — `I2C3_SDA_M0` / `I2C3_SCL_M0`
- pins 8/10 — `UART2_TX_M0` / `UART2_RX_M0`
- pins 12/35/38/40 — `I2S3_SCLK_M0` / `I2S3_LRCK_M0` / `I2S3_SDI_M0` / `I2S3_SDO_M0`

U4 remains DNP. J6/J7/J8 and R18/R19/R20/R21/R34/R35/R38/R39 are DNP so that the unqualified Raspberry Pi auxiliary-I2C options do not pull Radxa GPIOs. J5 remains the primary I2C/Qwiic connector.

## Validation

See `../validation/strict_port/` and `kicad/check_strict_port.py`.

The adapted design has 48 ERC warnings: eight upstream footprint-link findings are resolved by the vendored project-local libraries, and one exact C45 `lib_symbol_mismatch` remains approved pending symbol-library cleanup. It retains 110 remaining `Datasheet` field parity warnings; one inherited J4 field mismatch was resolved by correcting the manufacturing identity. All 49 upstream DRC findings are resolved, so current native DRC contains zero findings and zero unconnected items. C45 adds 10 µF / 50 V X7R input bypass; C21/C22 metadata correctly states 22 µF / 10 V, and the local U9/D1/C22 routing plus filled zone are hash-locked. The current board has 128 footprints and 1,013 track/via items. Twelve exact footprint definitions and `fp-lib-table` are hash-locked by `vendored_footprints_manifest.json`. J4 vendor/prototype approval, C45's ≥4.0 mm PCB gap and ≥0.5 mm residual-clearance gate, the 2 A EVT load/thermal envelope, antenna policy and single-source power rule remain fabrication gates.

## Upstream libraries

The 12 footprint definitions needed for `Library_Pollen`, `LCSC_parts_lib` and the board-used `Package_TO_SOT_SMD` subset are vendored under `kicad/*.pretty/` and mapped by `kicad/fp-lib-table`. `kicad/vendored_footprints_manifest.json` pins the exact file inventory and hashes. This removes all native DRC footprint-library findings without changing the embedded PCB, placement, pads, nets or routing. Some 3D-model paths still retain upstream names for traceability and may require later model vendoring for complete assembly rendering.
