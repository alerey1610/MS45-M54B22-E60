# MS45 DIY Tuning Guide: BMW E60 520i (M54B22, manual)

A guide for doing MS45 engine control unit (ECU) tuning yourself, with the full TunerPro definition file (XDF) containing all tables and parameters.

> **Risk.** An altered ECU can damage the engine, the catalytic converter, or the drivetrain, and it can affect the vehicle's operating permit and insurance. Work only on private ground. Keep the factory image and be ready to flash it back.

## Contents

| Path | What it is |
|---|---|
| [`xdf/`](xdf/) | Full TunerPro definition for the 1 MB flash image, all tables and parameters |
| [`tools/`](tools/) | Scripts to check an image before flashing: `ms45_info.py`, `ms45_diff.py`, `ms45_check.py` |
| [`data/`](data/) | Parameter data used by the check scripts |
| [`docs/`](docs/) | The guide, one page per topic |

## Check an image before flashing

```bash
python3 tools/ms45_check.py <original.bin> <modified.bin>
```

Exit code 0 means no errors. Do not flash on an error. The check does not guarantee the image is safe. It only catches known problems.

## Status

The guide is being written topic by topic. Factory and modified images will be added later.

## Useful tools and documentation

[MS45 definitions](https://github.com/pazi88/Siemens_ms45_RR-definitions/tree/master)(docs)
[MS45 tuning documentation](https://www.ms4x.net/index.php?title=Siemens_MS45)(docs)
[MS45 Flasher](https://github.com/terraphantm/MS45-Flasher)(for flashing and reading)
[TunerPro](https://www.tunerpro.net)(for tuning your file)
