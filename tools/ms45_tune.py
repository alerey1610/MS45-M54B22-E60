#!/usr/bin/env python3
"""Cuts the tune file for the flasher out of a 1 MB image (0x40000-0x5CFFF, 118,784 bytes).

Why: with "Full Binary" unticked, the flasher keeps the "Flash Program" button locked.
Usage: ms45_tune.py <flash.bin> <target_tune.bin>
"""
import sys
from pathlib import Path

from ms45_common import FLASH_SIZE, TUNE_END, TUNE_START, load, sha256, software_id


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__.strip())
    if Path(sys.argv[2]).resolve() == Path(sys.argv[1]).resolve():
        sys.exit("ERROR: source and target are the same file.")
    flash = load(sys.argv[1], FLASH_SIZE)
    tune = flash[TUNE_START:TUNE_END]
    Path(sys.argv[2]).write_bytes(tune)
    print(f"{sys.argv[2]}: {len(tune)} bytes, software {software_id(flash)}")
    print("SHA-256:", sha256(tune), "(the flasher recalculates CRC and signature anyway)")


if __name__ == "__main__":
    main()
