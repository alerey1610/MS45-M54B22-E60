# 1. How the MS45 stores its data

You do not need to understand everything here to follow the guide. It explains why the steps are what they are.

## Two files: flash and MPC

The MS45 has two memories:

| File | Size | Contents |
|---|---|---|
| Flash | 1 MB (`0x100000`) | Program part and calibration data (the "tune") |
| MPC | 448 KB (`0x70000`) | Internal memory of the main processor, with more program code |

A full read with the MS45 Flasher gives you both. For tuning you only touch one part of the flash.

## The tune area

All maps and constants live in **`0x40000`-`0x5CFFF`** of the flash, 118,784 bytes. The MS45 Flasher handles this area on its own:

- **Read DME** with "Full Binary" unticked saves exactly this area as a *tune file*.
- **Flash Tune** writes exactly this area back.

Working with the tune file is the safest way. The button that rewrites the program ("Flash Program") stays locked, so you cannot overwrite the program by mistake. That is why this guide recommends the tune file and `MS45_E60_520i_TuneFile.xdf`.

The first 256 bytes (`0x40000`-`0x400FF`) identify the data: software `0044560BN00S0QA0G` at `0x40010`, dataset `CA456N0B` at `0x40043`. Never change them.

## Three integrity checks

The ECU checks the tune area in three ways. Two of them the flasher fixes on its own, one it does not:

| Check | Where | Fixed by the flasher? |
|---|---|---|
| Data CRC | `0x40100` | yes |
| RSA signature | `0x40174`, 64 bytes | yes |
| **ROM test sum of the torque monitor** | covers `0x40240`-`0x407C7`, target at `0x457AC` | **no** |

The ROM test only covers a small area that holds monitoring tables. None of the tuning parameters lies inside it. If it is changed anyway, the ECU logs a fault or restarts. `ms45_check.py` refuses any file that touches that area.

There is a rare flasher bug: if the new signature happens to start with zero bytes, the flasher crashes *after* erasing the ECU. That happens in roughly 1 out of 300 files. `ms45_check.py` calculates the signature in advance and warns you. Then change any value by the smallest step and check again.

## Why the software version matters

An XDF is only a list of addresses and formulas. If your ECU runs different software, the same address holds a different table, and TunerPro shows nonsense without warning. Writing that back can make the engine run badly or not at all.

Check your version before anything else:

```bash
python3 tools/ms45_check.py my_read.bin
```

The first line must say `software 0044560BN00S0QA0G`. If it shows anything else, this XDF does not fit your car. The definitions from [pazi88](https://github.com/pazi88/Siemens_ms45_RR-definitions) cover other versions.

## What the labels mean

Every parameter in the XDF and in [`parameters.json`](../data/parameters.json) has these labels:

| Label | Values | Meaning |
|---|---|---|
| access | `free`, `caution`, `read_only` | Whether you may change it. `read_only` is blocked by the check script |
| confidence | `confirmed`, `partial`, `unclear` | Whether the effect is proven. `confirmed` = the original ECU code was run in an emulator |
| status | `verified`, `plausible`, `guess` | Whether address and scaling are proven (all curated ones are `verified`) |
| risk | `low`, `medium`, `high` | What can go wrong if the value is bad |
