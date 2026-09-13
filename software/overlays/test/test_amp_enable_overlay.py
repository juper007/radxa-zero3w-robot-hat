#!/usr/bin/env python3
"""Compile/apply the opt-in amplifier overlay; this is not a hardware test."""

from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "radxa-zero3w-robot-hat-amp.dts"


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.PIPE).strip()


def main() -> None:
    assert OVERLAY.is_file(), "default-off amplifier overlay is missing"
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        # Keep the existing Qwiic fixture untouched. Model only the external
        # audio overlay's target node; actual codec/OS bring-up remains EVT.
        base = (ROOT / "test/rk3566-symbols-base.dts").read_text()
        base = base.rsplit("};", 1)[0] + '\n\tsound-aic3104 { compatible = "simple-audio-card"; };\n};\n'
        (work / "base.dts").write_text(base)
        run("cpp", "-nostdinc", "-I", str(ROOT / "include"), "-undef",
            "-x", "assembler-with-cpp", str(OVERLAY), str(work / "amp.pp.dts"))
        run("dtc", "-@", "-I", "dts", "-O", "dtb", "-o", str(work / "amp.dtbo"), str(work / "amp.pp.dts"))
        run("dtc", "-@", "-I", "dts", "-O", "dtb", "-o", str(work / "base.dtb"), str(work / "base.dts"))
        merged = str(work / "merged.dtb")
        run("fdtoverlay", "-i", str(work / "base.dtb"), "-o", merged, str(work / "amp.dtbo"))

        def prop(node: str, name: str, kind: str = "s") -> str:
            return run("fdtget", "-t", kind, merged, node, name)

        amp = "/robot-hat-amplifier"
        assert prop(amp, "compatible") == "simple-audio-amplifier"
        assert prop(amp, "status") == "okay"
        gpio = prop("/gpio@fe760000", "phandle", "u")
        assert prop(amp, "enable-gpios", "u") == f"{gpio} 1 0", "AMP_ENABLE must be GPIO3_A1 active high"
        assert prop(amp, "sound-name-prefix") == "HAT AMP"
        assert prop("/sound-aic3104", "simple-audio-card,aux-devs", "u") == prop(amp, "phandle", "u")
        assert prop("/sound-aic3104", "simple-audio-card,routing") == (
            "HAT AMP INL LLOUT HAT AMP INR RLOUT HAT Speaker HAT AMP OUTL HAT Speaker HAT AMP OUTR"
        )
        assert prop("/sound-aic3104", "simple-audio-card,widgets") == "Speaker HAT Speaker"
        pin = "/pinctrl/robot-hat-amplifier/amp-enable-pins"
        bias = prop("/pinctrl/robot-hat-amp-pull-down", "phandle", "u")
        assert prop(pin, "rockchip,pins", "u") == f"3 1 0 {bias}"
        assert prop(amp, "pinctrl-0", "u") == prop(pin, "phandle", "u")
        run("fdtget", merged, "/pinctrl/robot-hat-amp-pull-down", "bias-pull-down")
        assert prop("/robot-hat-amp-5v", "regulator-min-microvolt", "u") == "5000000"
        assert prop(amp, "VCC-supply", "u") == prop("/robot-hat-amp-5v", "phandle", "u")
        # Applying without the external audio card must fail, not create an
        # unbound phantom sound node and appear to have enabled the amplifier.
        run("dtc", "-@", "-I", "dts", "-O", "dtb", "-o", str(work / "no-audio.dtb"),
            str(ROOT / "test/rk3566-symbols-base.dts"))
        result = subprocess.run(["fdtoverlay", "-i", str(work / "no-audio.dtb"), "-o",
                                 str(work / "bad.dtb"), str(work / "amp.dtbo")], capture_output=True)
        assert result.returncode != 0, "overlay must require the existing audio card"
    print("AMP OVERLAY COMPILE/APPLY TEST: PASS (synthetic base; hardware/runtime not tested)")


if __name__ == "__main__":
    main()
