#!/usr/bin/env python3
"""Compares two images and names the changed parameters instead of raw addresses.

Usage: ms45_diff.py <original.bin> <modified.bin>
Both files can be 1 MB images or tune files (118,784 bytes).
"""
import sys

from ms45_common import *  # noqa: F403

HEADER = {"data CRC": (CRC_ADDR, CRC_ADDR + 4), "data signature": (SIG_ADDR, SIG_ADDR + SIG_LEN)}


def diff(a, b, params):
    """Returns (changed parameters, changed header fields, unknown addresses)."""
    amap = build_addr_map(params)
    touched = {}
    head = {}
    unknown = []
    for off in range(min(len(a), len(b))):
        if a[off] == b[off]:
            continue
        for name, (s, e) in HEADER.items():
            if s <= off < e:
                head[name] = True
                break
        else:
            v = amap.get(off)
            if v:
                touched.setdefault(v["name"], v)
            else:
                unknown.append(off)
    return touched, head, unknown


def cell_changes(a, b, v):
    out = []
    for i in range(v["rows"] * v["cols"]):
        ra, rb = read_cell(a, v, i), read_cell(b, v, i)
        if ra != rb:
            out.append((i // v["cols"], i % v["cols"], ra, rb))
    return out


def label(v, ax, idx):
    a = v.get(ax)
    if a and idx < len(a["values"]):
        return f"{a['values'][idx]:.5g}"
    return str(idx)


def report(a, b, params):
    touched, head, unknown = diff(a, b, params)
    lines = []
    for name, v in sorted(touched.items(), key=lambda kv: kv[1]["addr"]):
        ch = cell_changes(a, b, v)
        lines.append(f"{name}  ({v['title']})  0x{v['addr']:05X}  {len(ch)} cells  [{v['status']}, {v['access']}]")
        for r, c, ra, rb in ch[:96]:
            where = f"row {label(v, 'y', r)}, col {label(v, 'x', c)}" if v["rows"] > 1 else (f"col {label(v, 'x', c)}" if v["cols"] > 1 else "value")
            lines.append(f"    {where}: {fmt_phys(v, ra * v['factor'] + v['offset'])} -> {fmt_phys(v, rb * v['factor'] + v['offset'])}  (raw {ra} -> {rb})")
    if head:
        lines.append("Header changed (the flasher rewrites this anyway): " + ", ".join(head))
    if unknown:
        g = []
        for off in unknown:
            if g and off - g[-1][1] <= 1:
                g[-1][1] = off
            else:
                g.append([off, off])
        lines.append("Addresses without a parameter name: " + ", ".join(f"0x{s:05X}-0x{e:05X}" for s, e in g[:40]))
    if not lines:
        lines.append("No differences.")
    return lines


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__.strip())
    a, a_tune = load_image(sys.argv[1])
    b, b_tune = load_image(sys.argv[2])
    if a_tune != b_tune:
        # Compare only the tune area if one side is a tune file
        a = b"\xff" * TUNE_START + a[TUNE_START:TUNE_END] + b"\xff" * (FLASH_SIZE - TUNE_END)
        b = b"\xff" * TUNE_START + b[TUNE_START:TUNE_END] + b"\xff" * (FLASH_SIZE - TUNE_END)
    print("\n".join(report(a, b, load_params())))


if __name__ == "__main__":
    main()
