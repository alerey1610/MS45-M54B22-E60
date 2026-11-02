#!/usr/bin/env python3
"""Zeigt Kennung und Integritaet eines Abbilds.

Aufruf: ms45_info.py <Flash.bin> [MPC.bin]
"""
import sys

from ms45_common import *  # noqa: F403


def main():
    flash = load(sys.argv[1], FLASH_SIZE)
    mpc = load(sys.argv[2], MPC_SIZE) if len(sys.argv) > 2 else None
    print("Kennung     ", flash[0x40010:0x40021].decode(errors="replace"), flash[0x40043:0x4004F].decode(errors="replace"))
    print("Programm    ", flash[0x60302:0x6030C].decode(errors="replace"))
    print("SHA-256     ", sha256(flash), "(Original)" if sha256(flash) == FLASH_SHA256 else "(geaendert)")
    stored, calc = u32(flash, CRC_ADDR), param_crc(flash)
    print(f"Daten-CRC    gespeichert {stored:08X}, gerechnet {calc:08X}", "OK" if stored == calc else "(der Flasher korrigiert das)")
    _, _, val = apply_flasher(flash)
    same = signature_bytes(val) == flash[SIG_ADDR:SIG_ADDR + SIG_LEN]
    print("Signatur    ", "passt" if same or stored != calc else "passt nicht (der Flasher korrigiert das)")
    hi, lo = rom_test_sum(flash)
    ok = (hi, lo) == (u32(flash, ROM_TEST_HI), u32(flash, ROM_TEST_LO))
    print(f"ROM-Test     {hi:08X}{lo:08X}", "OK" if ok else "FALSCH: DME meldet einen Fehler oder startet neu")
    if mpc:
        print("MPC-SHA-256 ", sha256(mpc), "(Original)" if sha256(mpc) == MPC_SHA256 else "(anders)")
        fs, ms = flash[0x60310:0x6031A].decode(), mpc[0x100:0x10A].decode()
        print(f"Flash<->MPC  {fs} - {ms} = {int(fs) - int(ms)}", "OK" if int(fs) - int(ms) == 500 else "PASST NICHT")


if __name__ == "__main__":
    main()
