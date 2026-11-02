# Basics and glossary

You do not need to understand everything here to follow the [guide](guide.md). It explains the words and why the steps are what they are.

## Glossary

| Word | Meaning |
|---|---|
| **DME / ECU** | Engine control unit. BMW calls it DME (Digitale Motor-Elektronik). Here: Siemens MS45.0 |
| **Bin** | A file with the raw memory content of the ECU |
| **Flash / MPC** | The two memories of the MS45. You only edit a part of the flash |
| **Tune file** | The 118,784-byte part of the flash that holds all maps and constants. What "Read DME" saves without "Full Binary" |
| **XDF** | Definition file for TunerPro: tells it where each table is in the bin and how to convert the numbers |
| **A2L** | BMW's internal description of all ECU parameters. The parameter names (`id_n_max_mt` …) come from it |
| **Map / table** | A grid of values the ECU looks up, e.g. ignition over rpm and load. Between the grid points it interpolates |
| **Constant** | A single value, e.g. the hard cut threshold |
| **Axis** | The row and column labels of a table: rpm, load, coolant temperature, gear |
| **rpm** | Engine revolutions per minute |
| **Load (mg/stroke)** | Air mass per cylinder and stroke. High = much throttle |
| **Overrun** | Lifting off while the car is moving: the engine is driven by the wheels |
| **Fuel cut / overrun cut-off** | On overrun the ECU stops injecting to save fuel. Burbles come from delaying it |
| **Burbles / pops** | Fuel that burns in the exhaust after lifting off |
| **Rev limiter** | Stops the engine revving higher than a set rpm |
| **Hard cut** | A limiter that cuts hard and fast instead of softly |
| **Ignition angle** | When the spark fires, in degrees of crankshaft rotation before top dead centre. Bigger number = earlier |
| **Knock** | Uncontrolled combustion that damages pistons. The ECU detects it and pulls ignition back |
| **RON** | Octane rating of the fuel. RON 98 = Super Plus |
| **Lambda** | Air-fuel ratio. 1 = exactly enough air; below 1 = rich (more fuel), above 1 = lean |
| **Narrowband / wideband sensor** | Lambda sensors. Narrowband (stock) only says rich or lean, wideband measures the exact value |
| **VANOS** | BMW's variable camshaft timing |
| **DISA** | Flap in the intake manifold that changes the intake length |
| **MAF** | Mass air flow sensor, measures the air going into the engine |
| **Fault memory** | Error codes stored by the ECU. Read with INPA |
| **Checksum / CRC / signature** | Numbers that prove the data is intact and genuine. The flasher recalculates two of them, the check script checks the third |
| **Limp mode** | Emergency mode with reduced power after a serious fault |
| **K+DCAN cable** | USB-to-OBD cable for BMW diagnostics |
| **EDIABAS / INPA** | BMW's communication layer and diagnostic program |
| **Dyno** | Test bench that measures the power at the wheels |

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
py tools/ms45_check.py my_read.bin
```

The first line must say `software 0044560BN00S0QA0G`. If it shows anything else, this XDF does not fit your car. The definitions from [pazi88](https://github.com/pazi88/Siemens_ms45_RR-definitions) cover other versions.

## What the labels mean

Every parameter in the XDF and in [`parameters.json`](../data/parameters.json) has these labels:

| Label | Values | Meaning |
|---|---|---|
| access | `free`, `caution`, `read_only` | Whether you may change it. `read_only` is blocked by the check script |
| status | `verified`, `plausible`, `guess` | Whether address and scaling are proven (all curated ones are `verified`) |
| risk | `low`, `medium`, `high` | What can go wrong if the value is bad |
