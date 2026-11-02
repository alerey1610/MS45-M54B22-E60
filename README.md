# MS45 DIY Tuning: BMW E60 520i (M54B22, manual)

A step-by-step guide to tuning the Siemens MS45.0 engine control unit yourself: read the ECU, edit the file in TunerPro, check it, flash it, and get back to stock. It includes a lean TunerPro definition (XDF) with every tuning option that has been worked out for this software, and a script that checks a file before you flash it.

Most of what is online about the MS45 is scattered across forums and mixed up between software versions. Everything here was traced in the ECU code or checked against a real dump, and every parameter states how sure that is.

> [!WARNING]
> **This only fits software `0044560BN00S0QA0G`** (dataset `CA456N0B`). Other software versions have their tables at other addresses. Run `ms45_check.py` on your dump first (step 3 of the guide). It tells you whether your ECU matches.
>
> A modified ECU can damage the engine, the catalytic converter or the drivetrain, and it can affect your vehicle's registration and insurance. Use it on private ground only. Keep your original dump and know how to flash it back.

## What you can change

| Goal | Parameters |
|---|---|
| Higher or lower rev limit, per gear | `id_n_max_mt`, `id_n_max_h_mt` |
| Harder limiter (hard cut feel) | `c_add_n_max_fcut` |
| Separate limit when standing | column 0 of both rev limit tables |
| Burbles when lifting off, in gear and standing | `ip_t_min_pu__n__tco`, `c_t_min_pu_vs` |
| Burbles only with the sport button | `ip_t_min_pu_rng_l__n__tco` |
| Louder burbles (later ignition on overrun) | `ip_iga_min_n_maf_pu` |
| Higher cold idle | `ip_n_sp_is`, `ip_acin_n_sp_is` |
| Top speed limiter | `c_vs_max` |

How it sounds and feels depends on your car: exhaust, mileage, condition. Test it yourself, one change at a time. Starting values are in the [recipes](docs/06-recipes.md). What else makes a difference, for example a sport exhaust, is in the [tips](docs/08-tips.md).

The standard XDF also shows the related tables you should not change (VANOS, lambda, pedal, torque, monitoring) as **[READ ONLY]**, so you can see the context. The check script refuses any file that changes them.

**Want to go further?** This is open source. The [expert XDFs](xdf/expert/) contain every known parameter (1707) with nothing locked, including ignition, VANOS, lambda, DISA and coolant for power tuning. Check those files with `ms45_check.py --expert`: the rules of this guide become warnings, but the checks that would brick or upset the ECU (monitoring checksum, signature, wrong software) still block. What is realistic for more power is in the [tips](docs/08-tips.md#more-power-what-is-realistic).

## Guide

1. [How the MS45 stores its data](docs/01-basics.md)
2. [Hardware and software you need](docs/02-setup.md)
3. [Reading the ECU and making a backup](docs/03-read.md)
4. [Editing in TunerPro](docs/04-edit.md)
5. [Checking and flashing](docs/05-check-and-flash.md)
6. [Recipes: what to enter for which goal](docs/06-recipes.md)
7. [How the limiter and the overrun fuel cut work](docs/07-how-it-works.md)
8. [Tips: exhaust, power, what works, what does not](docs/08-tips.md)
9. [Parameter reference](docs/parameters.md)

## Quick start

```bash
# 1. Is my dump the right software, and is it intact?
python3 tools/ms45_check.py my_read.bin

# 2. Edit a copy in TunerPro with xdf/MS45_E60_520i_TuneFile.xdf, save it

# 3. Check the edited copy against the original. Exit code 0 = no errors
python3 tools/ms45_check.py my_read.bin my_tune_v1.bin
```

If you see an `ERROR`, do not flash.

## Repository contents

| Path | What it is |
|---|---|
| [`xdf/MS45_E60_520i_TuneFile.xdf`](xdf/) | TunerPro definition for the tune file (118,784 bytes, "Read DME" without "Full Binary"). **Recommended.** |
| [`xdf/MS45_E60_520i_FullFlash.xdf`](xdf/) | Same definition for a full 1 MB flash dump |
| [`xdf/expert/`](xdf/expert/) | **Expert XDFs** (tune file and 1 MB): all 1707 known parameters, nothing locked. Check with `ms45_check.py --expert` |
| [`tools/ms45_check.py`](tools/ms45_check.py) | Checks a file before flashing. Also identifies a single dump |
| [`tools/ms45_tune.py`](tools/ms45_tune.py) | Cuts the tune file out of a 1 MB dump |
| [`tools/ms45_diff.py`](tools/ms45_diff.py) | Shows which parameters differ between two files |
| [`data/parameters.json`](data/parameters.json) | Address, scaling, stock value, safe range and notes for every known parameter. The scripts read it |

The scripts need Python 3 and nothing else. No ECU files are included in this repository.

## Credits

- [terraphantm/MS45-Flasher](https://github.com/terraphantm/MS45-Flasher): reads and flashes the ECU. The CRC and signature code in `tools/ms45_common.py` is ported from it.
- [pazi88/Siemens_ms45_RR-definitions](https://github.com/pazi88/Siemens_ms45_RR-definitions): RomRaider definitions and stock files. The stock tune of this software is identical to its `520ir.bin`.
- [MS4X wiki, Siemens MS45](https://www.ms4x.net/index.php?title=Siemens_MS45): background and parameter notes.
- [TunerPro](https://www.tunerpro.net): the editor.

## License

GPL-3.0, see [LICENSE](LICENSE). The checksum code is derived from the GPL-3.0 MS45-Flasher.
