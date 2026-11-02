#!/usr/bin/env python3
"""Checks an MS45 image before flashing. ERROR means: do not flash.

Usage:
  ms45_check.py [--expert] <original.bin> <modified.bin> [mpc.bin]   check a modified file against its original
  ms45_check.py <file.bin> [mpc.bin]                                 only identify a file and check its integrity

Images can be 1 MB flash dumps or tune files (118,784 bytes, "Read DME" without "Full Binary").
--expert (for the expert XDF): read-only parameters, unknown bytes and values outside the safe
range become warnings. ROM test, signature, area and software checks stay errors.
Exit code: 0 = no errors, 1 = at least one error.
"""
import sys
from pathlib import Path

from ms45_common import *  # noqa: F403
from ms45_diff import cell_changes, diff, report


class Result:
    def __init__(self, expert=False):
        self.err = []
        self.warn = []
        self.expert = expert

    def ok(self, text):
        print("  OK      ", text)

    def fail(self, text):
        print("  ERROR   ", text)
        self.err.append(text)

    def warning(self, text):
        print("  WARNING ", text)
        self.warn.append(text)

    def policy(self, text):
        """A rule of this guide, not a technical limit: an error normally, a warning with --expert."""
        if self.expert:
            self.warning(text + " (accepted with --expert)")
        else:
            self.fail(text)

    def summary(self):
        verdict = "DO NOT FLASH." if self.err else "No blocking problem found."
        print(f"\nResult: {len(self.err)} errors, {len(self.warn)} warnings. {verdict}")
        return 1 if self.err else 0


def check_software(r, buf, label):
    sw = software_id(buf)
    if sw == SOFTWARE_ID:
        r.ok(f"{label}: software {sw}, dataset {text(buf, DATASET_ADDR, 8)}")
        return True
    r.fail(f"{label}: software '{sw}', expected {SOFTWARE_ID}. The XDF and this check only fit {SOFTWARE_ID}.")
    return False


def check_mpc(r, flash, mpc):
    fs, ms = text(flash, 0x60310, 10), text(mpc, 0x100, 10)
    if fs.isdigit() and ms.isdigit() and int(fs) - int(ms) == 500:
        r.ok(f"Program numbers match ({fs} - {ms} = 500)")
    else:
        r.fail(f"Program numbers do not match ({fs} / {ms}). Wrong MPC file?")


def interlocks(old, new, params, touched, r):
    mt = phys_cells(new, params["id_n_max_mt"])
    h = phys_cells(new, params["id_n_max_h_mt"])
    if mt != h:
        r.warning("id_n_max_mt and id_n_max_h_mt differ. Up to 55 km/h h_mt applies, above that mt.")
    if max(mt + h) > 7000:
        r.policy(f"Rev limit {max(mt + h):.0f} rpm is above 7000. The MS4X wiki warns of engine damage on the M54 above 7000 rpm.")
    elif "id_n_max_mt" in touched or "id_n_max_h_mt" in touched:
        r.ok(f"Rev limit at most {max(mt + h):.0f} rpm")
    if min(mt + h) < 5000:
        r.warning(f"Rev limit {min(mt + h):.0f} rpm in at least one gear. A public report mentions ECU restarts with a strongly lowered limit (MS45.1, program patch).")
    lim = phys_cells(new, params["c_n_lim_min"])[0]
    if max(mt + h) >= lim:
        r.policy("Rev limit reaches the over-rev counter c_n_lim_min.")

    mon = params["ip_n_sp_is_mon_max_mon"]
    xs = mon["x"]["values"]
    ys = phys_cells(new, mon)

    def lim_at(t):
        if t <= xs[0]:
            return ys[0]
        for x0, x1, y0, y1 in zip(xs, xs[1:], ys, ys[1:]):
            if t <= x1:
                return y0 + (y1 - y0) * (t - x0) / (x1 - x0)
        return ys[-1]

    for name in ("ip_n_sp_is", "ip_acin_n_sp_is"):
        v = params[name]
        for t, val in zip(v["x"]["values"], phys_cells(new, v)):
            if val >= lim_at(t):
                r.fail(f"{name}: {val:.0f} rpm at {t:.0f} C is not below the monitor limit {lim_at(t):.0f} rpm.")

    fcut = phys_cells(new, params["c_add_n_max_fcut"])[0]
    if fcut < 10:
        r.warning(f"c_add_n_max_fcut {fcut:.0f} rpm: below 10 the model shows little extra effect, and it is untested.")

    for name in ("ip_n_min_puc__tco__gr_mt", "ip_n_accout_min_puc__tco__gr_mt"):
        if name in touched and max(phys_cells(new, params[name])) >= 6000:
            r.warning(f"{name}: threshold very high. That means continuous injection on the whole overrun, not short burbles.")

    for name in ("ip_t_min_pu__n__tco", "ip_t_min_pu_rng_l__n__tco", "c_t_min_pu_vs"):
        if name not in touched:
            continue
        v = params[name]
        cells = phys_cells(new, v)
        if max(cells) > 1.2:
            r.warning(f"{name}: {max(cells):.2f} s. Above 1.2 s the torque monitor hold time (c_t_tqi_mon) runs out. Check fault memory carefully afterwards.")
        if v["rows"] == 1:
            continue
        orig = phys_cells(old, v)
        if any(abs(cells[row * v["cols"] + col] - orig[row * v["cols"] + col]) > 1e-6 for row in range(v["rows"]) for col in range(4)):
            r.warning(f"{name}: cold columns changed too. Recommended: only 60 and 90 C (30-60 C is interpolated).")


def integrity(r, buf, is_tune):
    hi, lo = rom_test_sum(buf)
    if (hi, lo) == (u32(buf, ROM_TEST_HI), u32(buf, ROM_TEST_LO)):
        r.ok(f"ROM test sum {hi:08X}{lo:08X} is correct")
    else:
        r.fail("ROM test sum is wrong. The ECU would log a fault or restart.")
    stored, calc = u32(buf, CRC_ADDR), param_crc(buf)
    if stored == calc:
        r.ok(f"Data CRC {stored:08X} is correct")
    else:
        print(f"  INFO     Data CRC stored {stored:08X}, calculated {calc:08X} (the flasher fixes this when flashing)")


def info(paths):
    """Mode with one image: identify it and check integrity, e.g. right after reading the ECU."""
    r = Result()
    buf, is_tune = load_image(paths[0])
    print(f"File: {paths[0]} ({'tune file' if is_tune else '1 MB image'})")
    check_software(r, buf, "File")
    tune_sha = sha256(buf[TUNE_START:TUNE_END])
    if tune_sha == STOCK_TUNE_SHA256:
        r.ok("Tune area is the known stock tune for this software")
    else:
        print("  INFO     Tune area differs from the known stock tune (already modified, or another dataset)")
    print("  INFO     SHA-256 0x40000-0x5CFFF:", tune_sha)
    integrity(r, buf, is_tune)
    if len(paths) > 1:
        if is_tune:
            r.warning("Tune file has no program part, MPC check skipped.")
        else:
            check_mpc(r, buf, load(paths[1], MPC_SIZE))
    return r.summary()


def main():
    args = sys.argv[1:]
    expert = "--expert" in args
    args = [a for a in args if a != "--expert"]
    if not 1 <= len(args) <= 3 or args[0] in ("-h", "--help"):
        sys.exit(__doc__.strip())
    # Second argument with MPC size: info mode for one image plus its MPC
    if len(args) == 1 or (len(args) == 2 and Path(args[1]).is_file() and Path(args[1]).stat().st_size == MPC_SIZE):
        return info(args)

    r = Result(expert)
    if expert:
        print("EXPERT MODE: rules of this guide are only warnings. You are on your own.\n")
    print("1. Size and origin")
    a, a_tune = load_image(args[0])
    b, b_tune = load_image(args[1])
    mpc = load(args[2], MPC_SIZE) if len(args) > 2 else None
    # A tune file only holds 0x40000-0x5CFFF, the rest is taken from the other image
    if b_tune:
        b = a[:TUNE_START] + b[TUNE_START:TUNE_END] + a[TUNE_END:]
    if a_tune:
        a = b[:TUNE_START] + a[TUNE_START:TUNE_END] + b[TUNE_END:]
    ok_a = check_software(r, a, "Original")
    ok_b = check_software(r, b, "Modified")
    if not (ok_a and ok_b):
        print("\nWrong software: addresses differ, a check would be meaningless.")
        return r.summary()
    if sha256(a[TUNE_START:TUNE_END]) == STOCK_TUNE_SHA256:
        r.ok("Original is the known stock tune")
    else:
        r.warning("Original is not the known stock tune. Fine if it is your own earlier tune, otherwise compare against your untouched backup.")
    if b_tune:
        r.ok("Modified file is a tune file (118,784 bytes)")
    if a == b:
        r.ok("File is identical to the original (dry run)")

    print("2. Differences")
    params = load_params()
    print("\n".join("     " + line for line in report(a, b, params)))
    touched, head, unknown = diff(a, b, params)

    print("3. Area")
    outside = [off for off in range(len(a)) if a[off] != b[off] and not TUNE_START <= off < TUNE_END]
    if outside:
        r.fail(f"{len(outside)} bytes changed outside 0x40000-0x5CFFF, e.g. 0x{outside[0]:05X}. Flash Tune does not write them.")
    else:
        r.ok("Changes only in 0x40000-0x5CFFF")
    if a[ID_BLOCK[0]:ID_BLOCK[1]] != b[ID_BLOCK[0]:ID_BLOCK[1]]:
        r.fail("Identification block 0x40000-0x400FF changed.")
    if unknown:
        r.policy(f"{len(unknown)} bytes changed that belong to no known parameter. Do not flash until that is clear.")

    print("4. Parameters")
    for name, v in touched.items():
        if v["access"] == "read_only":
            r.policy(f"{name} is read only.")
        elif v["access"] == "caution":
            r.warning(f"{name} is 'caution' (risk {v['risk']}).")
        if v["rom_test"]:
            r.fail(f"{name} is inside the monitoring ROM test.")
        cells = phys_cells(b, v)
        changed = {row * v["cols"] + col for row, col, _, _ in cell_changes(a, b, v)}
        for i in sorted(changed):
            if v["safe_min"] is not None and not v["safe_min"] <= cells[i] <= v["safe_max"]:
                r.policy(f"{name}: {fmt_phys(v, cells[i])} outside {v['safe_min']} to {v['safe_max']}.")
                break
    interlocks(a, b, params, touched, r)

    print("5. Monitoring checksum (the flasher does NOT fix it)")
    if b[ROM_TEST_START:ROM_TEST_END] != a[ROM_TEST_START:ROM_TEST_END]:
        r.fail("Area 0x40240-0x407C7 changed.")
    hi, lo = rom_test_sum(b)
    if (hi, lo) != (u32(b, ROM_TEST_HI), u32(b, ROM_TEST_LO)):
        r.fail("ROM test sum does not match.")
    else:
        r.ok(f"ROM test sum {hi:08X}{lo:08X} matches")

    print("6. CRC and signature as the flasher writes them")
    final, crc, val = apply_flasher(b)
    r.ok(f"New data CRC {crc:08X}")
    if flasher_crash_risk(val):
        r.fail("Signature starts with zero bytes. The flasher would crash after erasing. Change one value minimally and check again.")
    else:
        r.ok("Signature does not crash the flasher")

    print("7. Flash and MPC")
    if a_tune or b_tune:
        r.ok("Tune file: no program part. The flasher compares the program ID itself when loading.")
    elif mpc is None:
        r.warning("No MPC file given, check skipped.")
    else:
        check_mpc(r, b, mpc)

    print("8. For comparison after reading back")
    print("     Tune file size 0x1D000 bytes (flasher: Read DME without 'Full Binary')")
    if b_tune:
        print("     Flash this file directly: Load File, Flash Tune, 'Full Binary' unticked.")
    else:
        print("     Make a tune file first: python3 tools/ms45_tune.py file.bin file_tune.bin")
    print("     SHA-256 0x40000-0x5CFFF:", sha256(final[TUNE_START:TUNE_END]))

    return r.summary()


if __name__ == "__main__":
    sys.exit(main())
