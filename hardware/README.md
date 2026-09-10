# Hardware

Hardware design source lives under this directory.

## Structure

- `kicad/` - KiCad 9 schematics and PCB source
- `libraries/` - project-specific symbols/footprints
- `mechanical/` - board outline, mounting and enclosure references

## KiCad hierarchy

Planned top-level project:

- `radxa_zero3w_robot_hat.kicad_pro`
- `radxa_zero3w_robot_hat.kicad_sch`
- `radxa_zero3w_robot_hat.kicad_pcb`
- `host_interface.kicad_sch`
- `power.kicad_sch`
- `dynamixel.kicad_sch`
- `sensors.kicad_sch`
- `audio.kicad_sch`

## Current implementation status

`kicad/power.kicad_sch` now exists as the first KiCad 9 source skeleton for the V1 power design. It captures the frozen topology and values but does **not yet contain the final symbol placement and electrical wiring**. The authoritative net-level implementation contract is `kicad/power_v1_connectivity.csv`.

Next hardware action is to populate the power sheet with the actual LM74700-Q1, MOSFET, TPS259470A, protection passives, branch capacitors, connector symbols, test points and net labels, then run KiCad ERC.

No hardware file in this repository should be considered fabrication-ready unless `docs/PROJECT_STATUS.md` explicitly marks the revision as a fabrication candidate.
