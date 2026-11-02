#!/usr/bin/env python3
"""Vergleicht zwei Abbilder und nennt Parameternamen statt nackter Adressen.

Aufruf: ms45_diff.py <Original.bin> <Geaendert.bin>
"""
import sys

from ms45_common import *  # noqa: F403

HEADER = {"Daten-CRC": (CRC_ADDR, CRC_ADDR + 4), "Daten-Signatur": (SIG_ADDR, SIG_ADDR + SIG_LEN)}


def diff(a, b, params):
    """Gibt (Parameter-Aenderungen, Kopfbytes, unbekannte Adressen) zurueck."""
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
    if a and idx < len(a["vals"]):
        return f"{a['vals'][idx]:.5g}"
    return str(idx)


def report(a, b, params):
    touched, head, unknown = diff(a, b, params)
    lines = []
    for name, v in sorted(touched.items(), key=lambda kv: kv[1]["addr"]):
        ch = cell_changes(a, b, v)
        lines.append(f"{name}  ({v['titel']})  0x{v['addr']:05X}  {len(ch)} Zellen  [{v['status']}, {v['aenderung']}]")
        for r, c, ra, rb in ch[:96]:
            where = f"Zeile {label(v, 'y', r)}, Spalte {label(v, 'x', c)}" if v["rows"] > 1 else (f"Spalte {label(v, 'x', c)}" if v["cols"] > 1 else "Wert")
            lines.append(f"    {where}: {fmt_phys(v, ra * v['f'] + v['o'])} -> {fmt_phys(v, rb * v['f'] + v['o'])}  (roh {ra} -> {rb})")
    if head:
        lines.append("Kopf geaendert (macht der Flasher selbst): " + ", ".join(head))
    if unknown:
        g = []
        for off in unknown:
            if g and off - g[-1][1] <= 1:
                g[-1][1] = off
            else:
                g.append([off, off])
        lines.append("Adressen ohne Parameternamen: " + ", ".join(f"0x{s:05X}-0x{e:05X}" for s, e in g[:40]))
    if not lines:
        lines.append("Keine Unterschiede.")
    return lines


if __name__ == "__main__":
    print("\n".join(report(load(sys.argv[1], FLASH_SIZE), load(sys.argv[2], FLASH_SIZE), load_params())))
