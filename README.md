# MS45 DIY Tuning: BMW E60 520i (M54B22, manual)

Complete documentation for tuning the Siemens MS45.0 engine control unit yourself: read the ECU, edit the file in TunerPro, check it, flash it, test it, and get back to stock. With TunerPro definitions (XDF) and a script that checks every file before you flash it.

Most of what is online about the MS45 is scattered across forums and mixed up between software versions. Everything here was traced in the ECU code or checked against a real dump.

## Read this first

| | |
|---|---|
| **Fits** | E60 520i, M54B22, **manual gearbox**, MS45.0 with software **`0044560BN00S0QA0G`**. Other versions or automatic: [does not fit](docs/troubleshooting.md#faq) |
| **Power** | A naturally aspirated 2.2. Software gives roughly **10-15 hp** at most. [What to expect](docs/performance.md#what-to-expect) |
| **Sound** | Burbles, pops and bangs, hard limiter: all possible. How loud depends mostly on the **exhaust**. [Sound and feel](docs/sound.md) |
| **You need** | Windows laptop, K+DCAN cable, battery charger, a few free programs. [Step 1](docs/guide.md#step-1-download-and-install-the-programs) |
| **Risk** | A failed flash can leave the ECU unusable. Too much ignition can damage the engine. Pops and bangs heat the catalyst. Keep your original file and know how to flash it back |
| **Legal** | Changed ECU software and pops are not approved for public roads in most countries. [Legal](docs/troubleshooting.md#legal) |
| **Time** | 2-3 hours for the first complete run |

## Where do you want to go?

| I want to ... | Go to |
|---|---|
| do it from scratch, step by step | **[Step-by-step guide](docs/guide.md)** |
| more sound: burbles, pops, bangs, flames, hard limiter | **[Area 1: Sound and feel](docs/sound.md)** (3 levels) |
| more power and response | **[Area 2: Performance](docs/performance.md)** (3 levels) |
| fix an error or a fault code | [Problems, FAQ and limits](docs/troubleshooting.md) |
| understand the words | [Basics and glossary](docs/basics.md) |
| understand how the limiter and burbles work inside | [How it works](docs/how-it-works.md) |
| look up one parameter | [Parameter reference](docs/parameters.md) |

## The steps at a glance

1. [Download the programs](docs/guide.md#step-1-download-and-install-the-programs)
2. [Connect the cable](docs/guide.md#step-2-connect-the-cable)
3. [Read the fault memory](docs/guide.md#step-3-read-the-fault-memory-before-you-start) so you know what was there before
4. [Read the ECU](docs/guide.md#step-4-read-the-ecu-download-your-bin) (download your bin)
5. [Check your bin](docs/guide.md#step-5-check-your-bin)
6. [Dry run](docs/guide.md#step-6-dry-run-flash-the-unchanged-file) with the unchanged file
7. [Change the bin](docs/guide.md#step-7-change-the-bin-in-tunerpro)
8. [Check the changed bin](docs/guide.md#step-8-check-the-changed-bin)
9. [Flash](docs/guide.md#step-9-flash)
10. [Test and read the fault memory](docs/guide.md#step-10-test-and-read-the-fault-memory)

Is my read OK, and is it the right software?

```bat
py tools/ms45_check.py stock_tune.bin
```

May I flash my changed file? (0 errors = yes)

```bat
py tools/ms45_check.py stock_tune.bin tune_v1.bin
```

## The two areas

| Level | Area 1: Sound and feel | Area 2: Performance |
|---|---|---|
| **1 Mild** | Rev limit 6700, harder limiter, short burbles | Ignition +0.75-1.5° with knock log |
| **2 Strong** | "d-d-d" hard cut, burbles up to 2 s, slightly later overrun ignition, sport exhaust | Ignition to just below the knock limit, full-load mixture with wideband |
| **3 Extreme / Max** | No fuel cut on overrun, very late overrun ignition: pops and bangs, flames with an open exhaust | VANOS, DISA, coolant on the dyno, hardware |

## Repository contents

| Path | What it is |
|---|---|
| [`xdf/MS45_E60_520i_TuneFile.xdf`](xdf/) | TunerPro definition for the tune file (118,784 bytes, "Read DME" without "Full Binary"). **Start here** |
| [`xdf/MS45_E60_520i_FullFlash.xdf`](xdf/) | Same for a full 1 MB flash dump |
| [`xdf/expert/`](xdf/expert/) | Expert XDFs: all 1707 known parameters, nothing locked. Check with `--expert` |
| [`tools/ms45_check.py`](tools/ms45_check.py) | Checks a file before flashing, or identifies a single read |
| [`tools/ms45_tune.py`](tools/ms45_tune.py) | Cuts the tune file out of a 1 MB dump |
| [`tools/ms45_diff.py`](tools/ms45_diff.py) | Lists which parameters differ between two files |
| [`data/parameters.json`](data/parameters.json) | Address, scaling, stock value, safe range and notes for every known parameter |

Python 3 is the only requirement for the scripts. No ECU files are included.

Tried something? [Share your result](https://github.com/alerey1610/MS45-M54B22-E60/issues/new?template=test-report.md): which level, which exhaust, what you heard, which fault codes. That is how this guide gets better.

## Kurzfassung auf Deutsch

Vollständige Anleitung zum Selbst-Tunen der Siemens MS45.0 im E60 520i (M54B22, Handschalter, Software `0044560BN00S0QA0G`): auslesen, in TunerPro ändern, mit dem Skript prüfen, flashen, testen. Zwei Bereiche mit je drei Stufen: **Sound** (Begrenzer, Hardcut, Blubbern bis Knallen mit Flammen) und **Leistung** (Zündung, Gemisch, VANOS; realistisch 10-15 PS). Start: [Schritt-für-Schritt-Anleitung](docs/guide.md). Die Doku ist auf Englisch, Fragen und Issues gerne auch auf Deutsch.

## Credits

- [terraphantm/MS45-Flasher](https://github.com/terraphantm/MS45-Flasher): reads and flashes the ECU. The CRC and signature code in `tools/ms45_common.py` is ported from it.
- [pazi88/Siemens_ms45_RR-definitions](https://github.com/pazi88/Siemens_ms45_RR-definitions): RomRaider definitions and stock files. The stock tune of this software is identical to its `520ir.bin`.
- [MS4X wiki, Siemens MS45](https://www.ms4x.net/index.php?title=Siemens_MS45): background and parameter notes.
- [TunerPro](https://www.tunerpro.net): the editor.

## License

GPL-3.0, see [LICENSE](LICENSE). The checksum code is derived from the GPL-3.0 MS45-Flasher.
