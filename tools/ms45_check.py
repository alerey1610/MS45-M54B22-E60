#!/usr/bin/env python3
"""Prueft eine geaenderte Datei vor dem Flashen. Rot heisst: nicht flashen.

Aufruf: ms45_check.py <Original> <Geaendert> [MPC.bin]
        ms45_check.py <Geaendert>     (Original = archive/easy-route/Start_Original_Tune.bin)
Beide Dateien duerfen 1-MB-Abbilder oder Tune-Dateien (118.784 Byte) sein.
Ausgang: 0 = keine Fehler, 1 = mindestens ein Fehler.
"""
import sys
from pathlib import Path

from ms45_common import *  # noqa: F403
from ms45_diff import cell_changes, diff, report


class Result:
    def __init__(self):
        self.err = []
        self.warn = []

    def ok(self, text):
        print("  OK      ", text)

    def fail(self, text):
        print("  FEHLER  ", text)
        self.err.append(text)

    def warning(self, text):
        print("  WARNUNG ", text)
        self.warn.append(text)


def sum_table(params, name, buf):
    return phys_cells(buf, params[name])


def interlocks(new, params, touched, r):
    mt = sum_table(params, "id_n_max_mt", new)
    h = sum_table(params, "id_n_max_h_mt", new)
    if mt != h:
        r.warning("id_n_max_mt und id_n_max_h_mt sind verschieden. Bis 55 km/h gilt h_mt, danach mt.")
    if max(mt + h) > 7000:
        r.fail(f"Drehzahlgrenze {max(mt + h):.0f}/min ueber 7000. Das Wiki warnt ab 7000/min vor Motorschaden am M54.")
    elif "id_n_max_mt" in touched or "id_n_max_h_mt" in touched:
        r.ok(f"Drehzahlgrenze hoechstens {max(mt + h):.0f}/min")
    if min(mt + h) < 5000:
        r.warning(f"Drehzahlgrenze {min(mt + h):.0f}/min in mindestens einem Gang. Ein oeffentlicher Bericht nennt Neustarts der DME bei stark abgesenkter Grenze (MS45.1, Programm-Patch).")
    lim = sum_table(params, "c_n_lim_min", new)[0]
    if max(mt + h) >= lim:
        r.fail("Drehzahlgrenze erreicht den Ueberdrehzaehler c_n_lim_min.")

    mon = params["ip_n_sp_is_mon_max_mon"]
    xs = mon["x"]["vals"]
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
        for t, val in zip(v["x"]["vals"], phys_cells(new, v)):
            if val >= lim_at(t):
                r.fail(f"{name}: {val:.0f}/min bei {t:.0f} C liegt nicht unter der Ueberwachung {lim_at(t):.0f}/min.")

    fcut = sum_table(params, "c_add_n_max_fcut", new)[0]
    if fcut < 10:
        r.warning(f"c_add_n_max_fcut {fcut:.0f}/min: unter 10 bringt laut Modell kaum mehr und ist nicht untersucht.")

    for name in ("ip_n_min_puc__tco__gr_mt", "ip_n_accout_min_puc__tco__gr_mt"):
        if name in touched and max(phys_cells(new, params[name])) >= 6000:
            r.warning(f"{name}: Schwelle sehr hoch. Das bedeutet Dauer-Einspritzung im ganzen Schub, keine kurzen Burbles.")

    for name in ("ip_t_min_pu__n__tco", "ip_t_min_pu_rng_l__n__tco", "c_t_min_pu_vs"):
        if name not in touched:
            continue
        v = params[name]
        cells = phys_cells(new, v)
        if max(cells) > 1.2:
            r.warning(f"{name}: {max(cells):.2f} s. Ueber 1,2 s laeuft die Haltezeit der Momentenueberwachung ab (c_t_tqi_mon). Danach Fehlerspeicher besonders pruefen.")
        if v["rows"] == 1:
            continue
        orig = v["phys"]
        if any(abs(cells[row * v["cols"] + col] - orig[row * v["cols"] + col]) > 1e-6 for row in range(v["rows"]) for col in range(4)):
            r.warning(f"{name}: Auch kalte Spalten geaendert. Empfohlen sind nur 60 und 90 C (zwischen 30 und 60 C wird interpoliert).")


def main():
    r = Result()
    print("1. Groesse und Herkunft")
    args = sys.argv[1:]
    if len(args) == 1:
        args.insert(0, str(Path(__file__).resolve().parent.parent / "archive", "easy-route" / "Start_Original_Tune.bin"))
    a, a_tune = load_image(args[0])
    b, b_tune = load_image(args[1])
    mpc = load(args[2], MPC_SIZE) if len(args) > 2 else None
    # Eine Tune-Datei enthaelt nur 0x40000-0x5CFFF, der Rest kommt vom anderen Abbild
    if b_tune:
        b = a[:TUNE_START] + b[TUNE_START:TUNE_END] + a[TUNE_END:]
    if a_tune:
        a = b[:TUNE_START] + a[TUNE_START:TUNE_END] + b[TUNE_END:]
    if (sha256(a[TUNE_START:TUNE_END]) != TUNE_SHA256) if a_tune else (sha256(a) != FLASH_SHA256):
        r.fail("Das Referenz-Original hat nicht den bekannten SHA-256. Falsche Datei?")
    else:
        r.ok("Original ist das bekannte Backup" + (" (Tune-Teil)" if a_tune else ""))
    if b_tune:
        r.ok("Geaenderte Datei ist eine Tune-Datei (118.784 Byte)")
    if a == b:
        r.ok("Datei ist identisch mit dem Original (Probelauf)")

    print("2. Unterschiede")
    params = load_params()
    print("\n".join("     " + line for line in report(a, b, params)))
    touched, head, unknown = diff(a, b, params)

    print("3. Bereich")
    outside = [off for off in range(len(a)) if a[off] != b[off] and not TUNE_START <= off < TUNE_END]
    if outside:
        r.fail(f"{len(outside)} Byte ausserhalb 0x40000-0x5CFFF geaendert, z. B. 0x{outside[0]:05X}. Flash Tune schreibt das nicht.")
    else:
        r.ok("Aenderungen nur in 0x40000-0x5CFFF")
    if a[0x40000:0x40100] != b[0x40000:0x40100]:
        r.fail("Kennungsblock 0x40000-0x400FF geaendert.")
    if unknown:
        r.fail(f"{len(unknown)} Byte ohne Parameternamen geaendert. Nicht flashen, bis das geklaert ist.")

    print("4. Parameter")
    for name, v in touched.items():
        if v["aenderung"] == "ansehen":
            r.fail(f"{name} ist 'nur ansehen'.")
        elif v["aenderung"] == "vorsicht":
            r.warning(f"{name} ist 'vorsicht' (Wirkung {v['wirkung']}, Risiko {v['risiko']}).")
        if v["rom_test"]:
            r.fail(f"{name} liegt im ROM-Test der Ueberwachung.")
        cells = phys_cells(b, v)
        changed = {row * v["cols"] + col for row, col, _, _ in cell_changes(a, b, v)}
        for i in changed:
            if v["lo"] is not None and not v["lo"] <= cells[i] <= v["hi"]:
                r.fail(f"{name}: {fmt_phys(v, cells[i])} ausserhalb {v['lo']} bis {v['hi']}.")
                break
    interlocks(b, params, touched, r)

    print("5. Ueberwachungs-Summe (der Flasher korrigiert sie nicht)")
    if b[ROM_TEST_START:ROM_TEST_END] != a[ROM_TEST_START:ROM_TEST_END]:
        r.fail("Bereich 0x40240-0x407C7 geaendert.")
    hi, lo = rom_test_sum(b)
    if (hi, lo) != (u32(b, ROM_TEST_HI), u32(b, ROM_TEST_LO)):
        r.fail("ROM-Test-Summe stimmt nicht.")
    else:
        r.ok(f"ROM-Test-Summe {hi:08X}{lo:08X} stimmt")

    print("6. CRC und Signatur, wie der Flasher sie schreibt")
    final, crc, val = apply_flasher(b)
    r.ok(f"Neue Daten-CRC {crc:08X}")
    if flasher_crash_risk(val):
        r.fail("Signatur beginnt mit Null-Bytes. Der Flasher wuerde nach dem Loeschen abstuerzen. Einen Wert minimal aendern und neu pruefen.")
    else:
        r.ok("Signatur laesst den Flasher nicht abstuerzen")

    print("7. Flash und MPC")
    if a_tune or b_tune:
        r.ok("Tune-Datei: Programmteil nicht enthalten. Der Flasher vergleicht die Kennung beim Laden selbst.")
    elif mpc is None:
        r.warning("Keine MPC-Datei angegeben, Pruefung uebersprungen.")
    else:
        if sha256(mpc) != MPC_SHA256:
            r.warning("MPC ist nicht das bekannte Original.")
        fs, ms = b[0x60310:0x6031A].decode(), mpc[0x100:0x10A].decode()
        if int(fs) - int(ms) == 500:
            r.ok(f"Programmnummern passen ({fs} - {ms} = 500)")
        else:
            r.fail(f"Programmnummern passen nicht ({fs} - {ms}).")

    print("8. Zum Vergleich nach dem Zuruecklesen")
    print("     Dateigroesse Tune 0x1D000 Byte (Flasher: Read DME ohne Haken)")
    if b_tune:
        print("     Diese Datei direkt mit Load File und Flash Tune flashen, Haken Full Binary aus.")
    else:
        print("     Tune-Datei zum Flashen ohne Haken: python ms45_tune.py Datei.bin Datei_tune.bin")
    print("     SHA-256 0x40000-0x5CFFF:", sha256(final[TUNE_START:TUNE_END]))

    print(f"\nErgebnis: {len(r.err)} Fehler, {len(r.warn)} Warnungen.", "NICHT FLASHEN." if r.err else "Keine Sperre gefunden.")
    return 1 if r.err else 0


if __name__ == "__main__":
    sys.exit(main())
