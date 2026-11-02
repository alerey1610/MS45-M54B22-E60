# Expert XDFs

| File | For |
|---|---|
| `MS45_E60_520i_TuneFile_Expert.xdf` | Tune file (118,784 bytes) |
| `MS45_E60_520i_FullFlash_Expert.xdf` | Full 1 MB flash dump |

All 1707 known parameters of software `0044560BN00S0QA0G`, nothing marked read only. Entries inside the monitoring checksum area are marked **[ROM TEST]**; changing them always fails the check.

- 67 parameters are documented in detail (same as the standard XDF). The rest come straight from BMW's A2L description: technical names, a few German descriptions, effects unknown.
- Check files with `py tools/ms45_check.py --expert stock_tune.bin my_tune.bin`.
- Sensitive tables (torque path, monitoring copies, logic switches, sensor curves): see [Performance, sensitive tables](../../docs/performance.md#sensitive-tables-in-the-expert-xdf).
- Loading 1707 entries takes TunerPro a moment longer than the standard XDF.
