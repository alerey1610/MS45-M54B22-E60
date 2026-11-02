#!/usr/bin/env python3
"""Shared code for the MS45 tools: loading images, CRC, signature, parameter table.

CRC and signature logic are ported from terraphantm/MS45-Flasher (Checksums_Signatures.cs, GPL-3.0)
and verified against a stock backup: a dry run produces byte-identical data.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

FLASH_SIZE = 0x100000
MPC_SIZE = 0x70000
TUNE_START = 0x40000
TUNE_END = 0x5D000  # exclusive: "Flash Tune" writes 0x40000-0x5CFFF
TUNE_SIZE = TUNE_END - TUNE_START  # size "Read DME" saves without "Full Binary"
CRC_ADDR = 0x40100
SIG_ADDR = 0x40174
SIG_LEN = 64
ROM_TEST_START = 0x40240  # monitoring: 64-bit sum that the flasher does NOT correct
ROM_TEST_END = 0x407C8
ROM_TEST_HI = 0x457AC
ROM_TEST_LO = 0x457B0
ID_BLOCK = (0x40000, 0x40100)

# The XDF and parameters.json are only valid for this software. Other software = other addresses.
SOFTWARE_ID = "0044560BN00S0QA0G"
SOFTWARE_ADDR = 0x40010
DATASET_ADDR = 0x40043
# 0x40000-0x5CFFF of the stock tune for this software (identical to 520ir.bin in pazi88/Siemens_ms45_RR-definitions)
STOCK_TUNE_SHA256 = "85e76b3d3fe2c560b7f64dee385fde18aa8534e5656303a0376ccd538e90a0a1"

# Public in the flasher source code (SignMS45Parameters).
RSA_N = 8470472580328006956677424405159809178175955696534718361218518906571634405286747173565502454089691240931470915432212928785673566143706092135925769557255439
RSA_D = 7260405068852577391437792347279836438436533454172615738187301919918543775959908116508429649500721130520546364846625732843778800986047617824899475327781303

_POLY = 0x04C11DB7
_TABLE = []
for _i in range(256):
    _c = _i << 24
    for _ in range(8):
        _c = ((_c << 1) ^ _POLY) & 0xFFFFFFFF if _c & 0x80000000 else (_c << 1) & 0xFFFFFFFF
    _TABLE.append(_c)


def crc32_ms45(data, init=0xFFFFFFFF):
    crc = init
    for b in data:
        crc = ((crc << 8) & 0xFFFFFFFF) ^ _TABLE[((crc >> 24) ^ b) & 0xFF]
    return crc


def u32(buf, off):
    return struct.unpack_from(">I", buf, off)[0]


def sha256(data):
    return hashlib.sha256(bytes(data)).hexdigest()


def text(buf, start, length):
    return bytes(buf[start:start + length]).decode("ascii", errors="replace")


def software_id(buf):
    return text(buf, SOFTWARE_ADDR, len(SOFTWARE_ID))


def load(path, size=None):
    try:
        data = Path(path).read_bytes()
    except OSError as e:
        sys.exit(f"ERROR: {path}: {e.strerror}")
    if size is not None and len(data) != size:
        sys.exit(f"ERROR: {path}: {len(data)} bytes, expected {size}")
    return data


def load_image(path):
    """1 MB image or tune file. Returns (1 MB buffer, is_tune). A tune file is placed at 0x40000."""
    data = load(path)
    if len(data) == FLASH_SIZE:
        return data, False
    if len(data) == TUNE_SIZE:
        return b"\xff" * TUNE_START + data + b"\xff" * (FLASH_SIZE - TUNE_END), True
    sys.exit(f"ERROR: {path}: {len(data)} bytes. Expected {FLASH_SIZE} (1 MB image) or {TUNE_SIZE} (tune file).")


def param_crc(flash):
    """Like GetChecksum: segments from 0x40104, start value from 0x40110."""
    crc = u32(flash, 0x40110)
    for i in range(u32(flash, 0x40104)):
        start = u32(flash, 0x40108 + 8 * i) - 0xFFE00000
        end = u32(flash, 0x4010C + 8 * i) - 0xFFE00000
        crc = crc32_ms45(flash[start:end + 1], crc)
    return crc


def sign_segments(flash):
    out = []
    for i in range(u32(flash, 0x40130)):
        out.append((u32(flash, 0x40134 + i * 8) - 0xFFF00000, u32(flash, 0x40144 + i * 4)))
    return out


def param_signature(flash):
    h = hashlib.md5()
    for start, length in sign_segments(flash):
        h.update(flash[start:start + length])
    return pow(int.from_bytes(h.digest(), "little"), RSA_D, RSA_N)


def signature_bytes(value):
    le = value.to_bytes(64, "little")
    out = bytearray(64)
    for i in range(16):
        out[4 * i:4 * i + 4] = le[4 * i:4 * i + 4][::-1]
    return bytes(out)


def flasher_crash_risk(value):
    """.NET BigInteger.ToByteArray returns bit_length//8 + 1 bytes. The flasher reads up to index 63."""
    return value.bit_length() // 8 + 1 < 64


def apply_flasher(flash):
    """Recalculates CRC and signature in the same order as the flasher."""
    out = bytearray(flash)
    crc = param_crc(out)
    struct.pack_into(">I", out, CRC_ADDR, crc)
    value = param_signature(out)
    out[SIG_ADDR:SIG_ADDR + SIG_LEN] = signature_bytes(value)
    return bytes(out), crc, value


def rom_test_sum(flash):
    """Monitoring sum as computed by the program at 0xFFF785A8."""
    hi, lo = 0x01234567, 0x89ABCDEF
    for off in range(ROM_TEST_START, ROM_TEST_END, 4):
        lo += u32(flash, off)
        if lo >> 32:
            hi = (hi + (lo >> 32)) & 0xFFFFFFFF
            lo &= 0xFFFFFFFF
    return hi, lo


def load_params():
    p = Path(__file__).resolve().parent.parent / "data" / "parameters.json"
    return json.loads(p.read_text())


def build_addr_map(params):
    m = {}
    # Curated entries last so they win where ranges overlap
    for v in sorted(params.values(), key=lambda r: r["curated"]):
        size = v["rows"] * v["cols"] * v["bits"] // 8
        for a in range(v["addr"], v["addr"] + size):
            m[a] = v
    return m


def read_cell(buf, v, i):
    n = v["bits"] // 8
    a = v["addr"] + i * n
    return int.from_bytes(buf[a:a + n], "big", signed=v["signed"])


def phys_cells(buf, v):
    return [read_cell(buf, v, i) * v["factor"] + v["offset"] for i in range(v["rows"] * v["cols"])]


def fmt_phys(v, val):
    unit = v["unit"] if v["unit"] not in ("", "-") else ""
    return f"{val:.3f}".rstrip("0").rstrip(".") + (" " + unit if unit else "")
