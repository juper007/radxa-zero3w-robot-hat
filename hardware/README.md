# Hardware

Hardware design source lives under this directory.

## Planned structure

- `kicad/` - KiCad 9 schematics and PCB source
- `libraries/` - project-specific symbols/footprints
- `mechanical/` - board outline, mounting and enclosure references

## Planned KiCad hierarchy

- `radxa_zero3w_robot_hat.kicad_pro`
- `radxa_zero3w_robot_hat.kicad_sch`
- `radxa_zero3w_robot_hat.kicad_pcb`
- `host_interface.kicad_sch`
- `power.kicad_sch`
- `dynamixel.kicad_sch`
- `sensors.kicad_sch`
- `audio.kicad_sch`

No hardware file in this repository should be considered fabrication-ready unless the project status explicitly marks a revision as a fabrication candidate.
