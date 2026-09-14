# Verified exact J4 STEP model placement (native KiCad 10.0.6)

For current J4 B.Cu at PCB `(103.3975,79.64)`, angle `-90`:

```scheme
(offset (xyz 0 -4.19905533063427 0.302503373819))
(scale (xyz 1 1 1))
(rotate (xyz -90 0 90))
```

Use only the acquired exact `REF-182665-01.step`, SHA256
`d5503fca60b62f7d24dcaec78bbc2f76d75032de7a299e5beee15c5749f0aad5`.
Do not apply these settings to the unrelated old FH-00339 model.

Native STEP export of a scratch-only PCB confirmed peg axes at STEP
`(80.53750000037,-79.64)` and `(126.257500000366,-79.64)`;
these correspond to the actual two PCB peg-hole centers `(80.5375,79.64)` and
`(126.2575,79.64)`. Model peg diameter 1.5875 mm, pitch 45.72 mm.
Native placed envelope: X 77.99749990037–128.797500100366,
Y -82.9293–-76.3507, Z -3.777600099981–0.997600000019 mm.
The 40 solder lead seating faces are at native STEP Z=-0.12 mm, matching
KiCad's bottom component placement datum (includes native assembly offset;
not a physically measured solder thickness). Body faces point **below**
the HAT; the pegs point into the board, as required for a B.Cu assembly.

Raw STEP axes: X along connector length, Y body height, Z across rows.
Raw lead seating Y=-0.302503373819; raw body top Y=3.355096626181,
giving 3.6576 mm body height. Row/lead span 6.5786 mm and length 50.8 mm.
A native export/import established this orientation; it was not inferred
from visual plausibility alone. Pin-1 electrical mapping and supplier
land/stencil signoff still require independent verification.

**Warning:** actual official host male-header plastic reaches Z=2.5 mm.
The 4 mm surface gap previously proposed for C45 is not automatically a
valid mated connector stack. See CAD_REPORT.md and j4_evidence.json for
actual interference results. Do not treat this model restoration as
fabrication or full-assembly approval.

Licensed exact STEP and scratch candidate/export remain under user Temp,
not in this repository. No existing PCB was modified by this analysis.
