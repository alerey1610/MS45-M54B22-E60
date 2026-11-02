#!/usr/bin/env python3
"""Gemeinsame Basis der MS45-Werkzeuge: Laden, CRC, Signatur, Parametertabelle.

CRC- und Signatur-Logik sind aus terraphantm/MS45-Flasher (Checksums_Signatures.cs, GPL-3.0)
uebertragen und am Original-Backup bestaetigt: Der Probelauf ergibt byte-identische Daten.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

FLASH_SIZE = 0x100000
MPC_SIZE = 0x70000
TUNE_START = 0x40000
TUNE_END = 0x5D000  # exklusiv: "Flash Tune" schreibt 0x40000-0x5CFFF
TUNE_SIZE = TUNE_END - TUNE_START  # so gross speichert "Read DME" ohne Haken
CRC_ADDR = 0x40100
SIG_ADDR = 0x40174
SIG_LEN = 64
ROM_TEST_START = 0x40240  # Ueberwachung: 64-Bit-Summe, die der Flasher nicht korrigiert
ROM_TEST_END = 0x407C8
ROM_TEST_HI = 0x457AC
ROM_TEST_LO = 0x457B0

FLASH_SHA256 = "7574f676c7490ad928c0b8ca5232dade9e12995ea5545a8f1d112ac801d8354e"
MPC_SHA256 = "6469caf1e3e49f98daea4d17f9d7db515d8d246a489d26e878e7c85a1d5a4f71"
TUNE_SHA256 = "85e76b3d3fe2c560b7f64dee385fde18aa8534e5656303a0376ccd538e90a0a1"  # 0x40000-0x5CFFF des Originals

# Oeffentlich im Quelltext des Flashers (SignMS45Parameters).
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


def load(path, size=None):
    data = Path(path).read_bytes()
    if size is not None and len(data) != size:
        sys.exit(f"FEHLER: {path}: {len(data)} Byte, erwartet {size}")
    return data


def load_image(path):
    """1-MB-Abbild oder Tune-Datei. Gibt (1-MB-Puffer, ist_tune) zurueck, die Tune-Datei liegt dann ab 0x40000."""
    data = load(path)
    if len(data) == FLASH_SIZE:
        return data, False
    if len(data) == TUNE_SIZE:
        return b"\xff" * TUNE_START + data + b"\xff" * (FLASH_SIZE - TUNE_END), True
    sys.exit(f"FEHLER: {path}: {len(data)} Byte. Erwartet {FLASH_SIZE} (1-MB-Abbild) oder {TUNE_SIZE} (Tune-Datei).")


def param_crc(flash):
    """Wie GetChecksum: Segmente aus 0x40104, Startwert aus 0x40110."""
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
    """.NET BigInteger.ToByteArray liefert bit_length//8 + 1 Byte. Der Flasher greift bis Index 63 zu."""
    return value.bit_length() // 8 + 1 < 64


def apply_flasher(flash):
    """Rechnet CRC und Signatur in der Reihenfolge des Flashers neu."""
    out = bytearray(flash)
    crc = param_crc(out)
    struct.pack_into(">I", out, CRC_ADDR, crc)
    value = param_signature(out)
    out[SIG_ADDR:SIG_ADDR + SIG_LEN] = signature_bytes(value)
    return bytes(out), crc, value


def rom_test_sum(flash):
    """Ueberwachungs-Summe wie im Programm bei 0xFFF785A8."""
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
    # Katalog-Eintraege zuletzt, damit sie bei Ueberschneidungen gewinnen
    for v in sorted(params.values(), key=lambda r: r["kuratiert"]):
        size = v["rows"] * v["cols"] * v["bits"] // 8
        for a in range(v["addr"], v["addr"] + size):
            m[a] = v
    return m


def read_cell(buf, v, i):
    n = v["bits"] // 8
    a = v["addr"] + i * n
    return int.from_bytes(buf[a:a + n], "big", signed=v["signed"])


def phys_cells(buf, v):
    return [read_cell(buf, v, i) * v["f"] + v["o"] for i in range(v["rows"] * v["cols"])]


def fmt_phys(v, val):
    return f"{val:.3f}".rstrip("0").rstrip(".") + (" " + v["unit"].strip() if v["unit"].strip() else "")


WORDS = [("unterstuetz", "unterstütz"), ("Lautstaerke", "Lautstärke"), ("gefuehl", "gefühl"), ("gelaende", "gelände"), ("Pruef", "Prüf"), ("pruef", "prüf"), ("Waehr", "Währ"), ("erfuell", "erfüll"), ("geklaert", "geklärt"), ("laedt", "lädt"), ("laenger", "länger"), ("staendig", "ständig"), ("waere", "wäre"), ("zaehl", "zähl"), ("Zuend", "Zünd"), ("zuend", "zünd"), ("Kuehl", "Kühl"), ("kuehl", "kühl"), ("Luefter", "Lüfter"), ("Ueber", "Über"), ("ueber", "über"),
         ("fuer", "für"), ("Fuer", "Für"), ("Rueck", "Rück"), ("rueck", "rück"), ("aender", "änder"), ("Aender", "Änder"), ("haeng", "häng"),
         ("faell", "fäll"), ("faehr", "fähr"), ("spaet", "spät"), ("Spaet", "Spät"), ("bestaetig", "bestätig"), ("geprueft", "geprüft"),
         ("zusaetz", "zusätz"), ("Zusaetz", "Zusätz"), ("naeher", "näher"), ("Annaeh", "Annäh"), ("waehr", "währ"), ("laeuft", "läuft"),
         ("Stuetz", "Stütz"), ("groess", "größ"), ("Groess", "Größ"), ("heiss", "heiß"), ("ausserhalb", "außerhalb"), ("laesst", "lässt"),
         ("moeglich", "möglich"), ("Oel", "Öl"), ("frueh", "früh"), ("schuetz", "schütz"), ("Stueck", "Stück"), ("erzoeger", "erzöger"),
         ("haert", "härt"), ("Haert", "Härt"), ("rhoeh", "rhöh"), ("hoeher", "höher"), ("fuehr", "führ"), ("Fuehr", "Führ"), ("ueberdeck", "überdeck"),
         ("Daempfer", "Dämpfer"), ("Traeg", "Träg"), ("gehoert", "gehört"), ("Gehoert", "Gehört"), ("ausloes", "auslös"), ("Saugrohr-Umschaltung", "Saugrohr-Umschaltung"),
         ("Gaenge", "Gänge"), ("abgebaut", "abgebaut"), ("Bestaet", "Bestät"), ("Dauer-Einspritzung", "Dauer-Einspritzung"), ("muessen", "müssen"), ("Muster", "Muster")]


def de(s):
    for a, b in WORDS:
        s = s.replace(a, b)
    return s
