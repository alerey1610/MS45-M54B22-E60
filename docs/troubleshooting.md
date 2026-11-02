# Problems, FAQ and limits

| Topic | Go to |
|---|---|
| The check script shows an error | [Check script messages](#check-script-messages) |
| A fault code appeared after flashing | [Fault codes](#fault-codes-you-may-see) |
| The car runs strangely after flashing | [After flashing](#after-flashing) |
| The flash failed or the ECU does not answer | [Recovery](#the-flash-failed-or-the-ecu-does-not-respond) |
| Will it work on my car? Can anyone see it? | [FAQ](#faq) |
| Launch control, pops at the limiter | [What is not possible](#what-is-not-possible) |
| Pops and bangs, flames | [Sound, level 3](sound.md#level-3-extreme-pops-bangs-and-flames) |
| Is it legal? | [Legal](#legal) |

---

## Check script messages

| Message | What to do |
|---|---|
| `ERROR software '...', expected 0044560BN00S0QA0G` | Wrong software, this XDF does not fit. Stop |
| `WARNING Original is not the known stock tune` | Fine if the original is your own earlier tune. Otherwise check that you compare against your untouched read |
| `ERROR ... bytes changed outside 0x40000-0x5CFFF` | You edited a 1 MB file outside the tune area. Flash Tune would not write it. Start again from a copy |
| `ERROR Identification block 0x40000-0x400FF changed` | Never change it. Start again from a copy |
| `ERROR ... bytes changed that belong to no known parameter` | Something changed that is not in the XDF. Find out what before flashing (`py tools/ms45_diff.py old.bin new.bin` lists it) |
| `ERROR <name> is read only` | You changed a [READ ONLY] entry. Undo it, or use the [expert XDF](performance.md#expert-xdf) knowingly |
| `WARNING <name> is 'caution'` | Normal for burbles, hard cut and ignition. Read it, then test carefully |
| `ERROR <name>: ... outside <min> to <max>` | Value outside the safe range. Correct it |
| `ERROR Rev limit ... above 7000` | Too high for the M54. Lower it |
| `WARNING id_n_max_mt and id_n_max_h_mt differ` | The two rev limit tables should normally be equal |
| `ERROR ... is not below the monitor limit` | Idle too high, the torque monitor would intervene. Lower it |
| `WARNING ... above 1.2 s` | Burble time longer than the torque monitor hold time. Only after a clean test with shorter times |
| `WARNING cold columns changed too` | Burbles would also act on a cold engine. Recommended: only 60 and 90 °C |
| `WARNING ... threshold very high` | Continuous injection on the whole overrun, not short burbles |
| `ERROR ... is inside the monitoring ROM test` / `ROM test sum does not match` | Something changed the monitoring area. Never flash this |
| `ERROR Signature starts with zero bytes` | The flasher would crash after erasing. Change any value by one step (e.g. 1.10 to 1.11 s), save, check again. Happens in roughly 1 of 300 files |
| `ERROR Program numbers do not match` | Flash and MPC file are not from the same ECU |
| `ERROR: ... bytes. Expected ...` | Wrong file size. Use the 1 MB flash or the 118,784-byte tune file |

The check finds known problems. It cannot prove that a file is safe.

## Fault codes you may see

BMW-specific codes are shown by INPA with a number and a text. Codes that are related to the changes in this guide:

| Code or text | Likely cause | What to do |
|---|---|---|
| **28B1, 28B2** (rev limiting) | Hard cut too hard | `c_add_n_max_fcut` back to 50 |
| Torque monitoring, plausibility of torque | Burble time too long, or a monitored table changed | Shorter burble times, or flash the original |
| Misfire after burble tests | Usually an existing ignition problem that shows up now | Check plugs and coils |
| Catalyst or lambda codes | Long burbles or late ignition on overrun, or an existing problem | Back to shorter values, check the exhaust |
| VANOS, camshaft (P0011, P0014, …) | Not caused by these changes | Fix the VANOS before tuning |

Compare with your photo from [step 3](guide.md#step-3-read-the-fault-memory-before-you-start). A code that was already there before is not from your tune.

## After flashing

| What happens | What to do |
|---|---|
| Engine stalls, ECU restarts, monitoring faults | Flash the original immediately |
| Revs hang when shifting | Sport mode off. If it stays, flash the original |
| Fuel keeps injecting over the whole overrun | Flash the original. Compare your file with `ms45_diff.py`: an overrun cut-off threshold was probably changed |
| Burbles hardly audible | Normal with the stock exhaust, see [exhaust](sound.md#the-exhaust-decides-how-much-you-hear) |
| Idle a bit rough for the first minutes | The ECU keeps its learned adaptations through a Flash Tune. Whether resetting them helps after these changes has not been tested. If it does not settle after a few drives, reset the adaptations in INPA or flash the original |

## The flash failed or the ECU does not respond

What helps here: **Flash Tune only erases and writes the data area (`0x40000`-`0x5FFFF`). The boot loader and the program stay untouched.** So after a failed tune flash the ECU usually still answers and can be flashed again over OBD. This is how the flasher is written; a real failed flash on this car has not been tested.

1. **Do not panic and do not unplug anything.** Leave the ignition on.
2. Check the voltage (charger connected? at least 13 V?).
3. Close and restart the flasher. **Identify DME.**
4. If it answers: **Flash Tune** again with the same checked file, or with `stock_tune.bin`.
5. If it does not answer: ignition off, wait one minute, ignition on, check cable, COM port and latency, try Identify again.
6. If it still does not answer: the engine will not start. Do not keep trying for hours with a weak battery. Specialists can recover an MS45 on the bench (opened ECU, direct connection); Bimmerlabs, for example, lists recovery for the MS45. That costs money, which is why the [dry run](guide.md#step-6-dry-run-flash-the-unchanged-file) and a stable voltage matter.

## FAQ

**Does this work on a 525i or 530i?** Not with these files. Those engines use other software with other addresses. Check yours with Identify DME. The [pazi88 definitions](https://github.com/pazi88/Siemens_ms45_RR-definitions) cover several versions.

**Does it work with an automatic gearbox?** No. Automatic cars use other rev limit tables, the check script does not know them, and the gearbox control unit can disturb the flash.

**My 520i shows a different software version.** Then do not use these XDFs. Even small differences (BN00 vs BN02) can move tables.

**Can I use a ready-made tune from the internet?** Only if it was made for exactly your software version. Check it with `py tools/ms45_check.py stock_tune.bin downloaded.bin` first: the check names every changed table and shows if something changes the overrun thresholds or protected areas.

**Can a dealer or inspector see that the ECU was changed?** Assume yes. The software can be read out and compared with the stock one. Do not rely on "undetectable".

**How often can I flash?** Flash memory has a limited number of erase cycles, but it is far beyond what tuning needs. The real risk is a failed flash, not wear.

**Can I go back to stock?** Yes, any time: flash `stock_tune.bin` exactly like a tune. Keep that file safe.

**Do I need a tune after fitting a sport exhaust or intake parts?** No. The ECU measures the air with the MAF and adapts. A tune only changes behaviour, the parts change sound.

**Can I do this on a Mac?** The flasher, INPA and TunerPro need Windows. The check script runs anywhere with Python (`python3` instead of `py`).

**TunerPro asks for a checksum plugin.** Ignore it. The flasher calculates CRC and signature.

**Why is everything in English?** So that people from other countries can use it too. Issues and questions in German are fine.

## What is not possible

These would need changes to the ECU program (a program patch), not to the tune data. Not covered here:

| Idea | Note |
|---|---|
| Launch control with ignition cut | No public recipe for this MS45 software |
| No-lift-shift | Program patch, high gearbox load |
| "Popcorn" limiter (bangs at the limiter) | No parameter found for it in this software |
| Switching between tunes in the car | Only exists for the MS45.1, with a program patch |
| Automatic blipping on downshifts | Missing input and program code |
| Anti-lag | Only useful on turbo engines |

Pops, bangs and flames from overrun fuel are possible in the tune data, see [Sound, level 3](sound.md#level-3-extreme-pops-bangs-and-flames).

Not in this repository: switches to turn off catalyst, lambda or secondary air diagnostics or OBD. The parameter data contains none of them, so a decat will show fault codes.

## Legal

Germany as an example; other countries have similar rules.

- There is practically no type approval (ABE) for ECU software. Legal only with an individual approval (§21 StVZO) with emissions and noise measurement, which costs several hundred euros or more.
- Burbles and pops cannot be approved for public roads: changed overrun behaviour affects emissions and noise (§19, §30 StVZO). The registration can lapse, and insurance can refuse to pay.
- Offers advertised as "undetectable" are not legal either.
- Flash your original back before driving on public roads and before every inspection.
