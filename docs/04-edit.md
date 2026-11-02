# 4. Editing in TunerPro

## Which XDF for which file

| Your file | Size | XDF |
|---|---|---|
| Tune file ("Read DME" without "Full Binary") | 118,784 bytes | `MS45_E60_520i_TuneFile.xdf` (recommended) |
| Full flash dump | 1,048,576 bytes | `MS45_E60_520i_FullFlash.xdf` |

The wrong combination shows wrong values: the addresses are shifted by `0x40000`.

**Expert XDFs** (`xdf/expert/`): the same two variants with all 1707 known parameters and nothing marked read only. Use them if you want to work on ignition, VANOS, DISA and the rest yourself. Entries inside the monitoring checksum area are marked **[ROM TEST]**: changing them breaks the checksum and the check script will always block that. Check expert files with `ms45_check.py --expert`.

## Open the file

1. **Copy** your read, for example `my_tune_v1.bin`. Only ever edit the copy.
2. TunerPro: **File, Open Bin**, select the copy.
3. **XDF, Select XDF**, select the matching XDF.
4. On the left you see the categories `01 Rev limiter` to `12 Monitoring`. Within each category, changeable entries come first, then **[CAUTION]**, then **[READ ONLY]**.

Check that it loaded correctly. Open *Rev limit, manual (above 55 km/h)*: you must see 9 columns labelled 0 to 8, all with 6520. If you see other numbers, the XDF does not match the file.

## Change values

1. Double-click a table.
2. Select cells (drag with the mouse, or click the header for a whole row or column).
3. Type the new value and press Enter. For many cells at once you can also use the function bar: select, choose **Offset (+/-)** or **Set**, enter the value, **Execute**.
4. **File, Save Bin.**

Each entry has a description (open the table, then the info/description view). It shows:

- Stock value and the range `ms45_check.py` accepts
- What the parameter does, a recipe, what it interacts with, and how to test it

## Reading the tables

- **Rows (Y axis)** and **columns (X axis)** are the input values, for example rpm and coolant temperature. The ECU interpolates between them.
- The rev limit tables have one cell per **gear**: column 0 = no gear detected (standing or neutral), 1-6 = gears, 7 and 8 are unused.
- Coolant temperature columns: everything up to 30 °C stays stock if you only change 60 and 90 °C. Between 30 and 60 °C the ECU interpolates.

## Rules that keep you safe

- **One idea per file.** For example the rev limit first, burbles in a second file. If a fault appears, you know where it came from.
- Name files by version: `tune_v1_revlimit.bin`, `tune_v2_burbles.bin`.
- With the standard XDF, do not edit **[READ ONLY]** entries. The tag is only a hint in TunerPro; the actual block is in `ms45_check.py`. If you know what you are doing, use the expert XDF and `--expert` instead.
- TunerPro does not need a checksum plugin. The flasher recalculates CRC and signature.
