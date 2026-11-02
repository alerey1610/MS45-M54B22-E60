# 5. Checking and flashing

## Check

Always check the edited file against your original:

```bash
python3 tools/ms45_check.py my_read_tune.bin my_tune_v1.bin
```

With a 1 MB file you can add the MPC file as a third argument. Then the script also checks that flash and MPC belong together.

### Example: rev limit 6700

```
1. Size and origin
  OK       Original: software 0044560BN00S0QA0G, dataset CA456N0B
  OK       Modified: software 0044560BN00S0QA0G, dataset CA456N0B
  OK       Original is the known stock tune
  OK       Modified file is a tune file (118,784 bytes)
2. Differences
     id_n_max_h_mt  (Rev limit, manual (standing and up to 55 km/h))  0x46024  9 cells  [verified, free]
         col 0: 6520 rpm -> 6700 rpm  (raw 6520 -> 6700)
         ...
     id_n_max_mt  (Rev limit, manual (above 55 km/h))  0x46036  9 cells  [verified, free]
         ...
3. Area
  OK       Changes only in 0x40000-0x5CFFF
4. Parameters
  OK       Rev limit at most 6700 rpm
5. Monitoring checksum (the flasher does NOT fix it)
  OK       ROM test sum 012345E3FD21E55F matches
6. CRC and signature as the flasher writes them
  OK       New data CRC F356F595
  OK       Signature does not crash the flasher
7. Flash and MPC
  OK       Tune file: no program part. The flasher compares the program ID itself when loading.
8. For comparison after reading back
     ...
     SHA-256 0x40000-0x5CFFF: 00b1cc46...

Result: 0 errors, 0 warnings. No blocking problem found.
```

### What the messages mean

| Message | What to do |
|---|---|
| `ERROR software '...', expected 0044560BN00S0QA0G` | Wrong software, this XDF does not fit. Stop |
| `WARNING Original is not the known stock tune` | Fine if the original is your own earlier tune. Otherwise check that you are comparing against your untouched read |
| `ERROR ... bytes changed outside 0x40000-0x5CFFF` | You edited a 1 MB file outside the tune area. Flash Tune would not write it. Start again from a copy |
| `ERROR ... bytes changed that belong to no known parameter` | Something changed that is not in the XDF. Find out what before flashing |
| `ERROR <name> is read only` | You changed a [READ ONLY] entry. Undo it |
| `WARNING <name> is 'caution'` | Normal for burbles and the hard cut. Read it, then test carefully |
| `ERROR <name>: ... outside <min> to <max>` | Value outside the safe range. Correct it |
| `ERROR Rev limit ... above 7000` | Too high for the M54. Lower it |
| `WARNING id_n_max_mt and id_n_max_h_mt differ` | The two rev limit tables should normally be equal |
| `ERROR ... is not below the monitor limit` | Idle too high, the torque monitor would intervene. Lower it |
| `WARNING ... above 1.2 s` | Burble time longer than the torque monitor hold time. Only after a clean test with shorter times |
| `ERROR Signature starts with zero bytes` | The flasher would crash. Change any value by one step (e.g. 1.10 to 1.11 s) and check again |
| `ERROR ROM test sum does not match` | Something changed the monitoring area. Do not flash |

The script finds known problems. It cannot prove that a file is safe.

### Expert mode

```bash
python3 tools/ms45_check.py --expert my_read_tune.bin my_expert_tune.bin
```

For files made with the expert XDF. These become warnings instead of errors: read-only parameters, bytes without a known parameter, values outside the safe range, rev limit above 7000. These stay errors, because the ECU itself reacts to them: wrong software, changes outside the tune area or in the identification block, anything inside the monitoring checksum area, idle above the monitor limit, a signature that crashes the flasher.

## Flash

1. Charger on, ignition on, engine off, consumers off (see [setup](02-setup.md#before-every-session)).
2. MS45 Flasher: **Identify DME**.
3. **Untick "Full Binary".**
4. **Load File**, select your checked tune file.
   If the flasher says *"Loaded tune does not match DME's program"*, click **No**. It is the wrong file.
5. **Flash Tune.** Do not interrupt it. Do not touch the cable or the laptop.
6. Read the status line. If security access or erasing fails, the flasher may continue anyway. That is why you always read back afterwards.

## Verify

7. **Read DME** with "Full Binary" unticked.
8. Compare the SHA-256 of that read with the line `SHA-256 0x40000-0x5CFFF` from section 8 of the check:

   ```bash
   python3 tools/ms45_check.py read_back.bin
   ```

   On Windows you can also use `certutil -hashfile read_back.bin SHA256`.
9. Read and clear fault memory, start the engine, read fault memory again.
10. Test as described in the [recipe](06-recipes.md), warm engine, private ground.

## Back to stock

Flash your original tune file exactly the same way: Load File, Flash Tune. Do this before driving on public roads and before every inspection.

## Troubleshooting

| What happens | What to do |
|---|---|
| Flash stops halfway | Leave the ignition on, check the voltage, run Flash Tune again with the same file |
| Fault 28B1 or 28B2 (rev limiting) | Set `c_add_n_max_fcut` back to 50 |
| Engine stalls, ECU restarts, monitoring faults | Flash the original immediately |
| Revs hang when shifting | Sport mode off. If it stays, flash the original |
| Fuel keeps injecting over the whole overrun | Flash the original. Compare your file with `ms45_diff.py`: an overrun cut-off threshold was probably changed |
