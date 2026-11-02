# 3. Reading the ECU and making a backup

## Full backup (do this once)

1. Open the MS45 Flasher and select the COM port.
2. **Identify DME.** The status line shows the software version.
3. Tick **Full Binary** and click **Read DME**. You get a 1 MB flash file and the MPC file.
4. Copy both files to two places, for example a USB stick and a cloud folder. Make them read-only.

This backup is your way back if anything goes wrong.

## Tune file (for editing)

5. Untick **Full Binary** and click **Read DME** again. You get the tune file with 118,784 bytes.

If you only have the 1 MB file, you can cut the tune file out of it:

```bash
python3 tools/ms45_tune.py my_full_read.bin my_read_tune.bin
```

## Check the read

```bash
python3 tools/ms45_check.py my_full_read.bin my_mpc.bin
```

Expected output:

```
  OK       File: software 0044560BN00S0QA0G, dataset CA456N0B
  OK       Tune area is the known stock tune for this software
  OK       ROM test sum 012345E3FD21E55F is correct
  OK       Data CRC 71EF2540 is correct
  OK       Program numbers match (6577365630 - 6577365130 = 500)

Result: 0 errors, 0 warnings. No blocking problem found.
```

| Line | Meaning |
|---|---|
| `software ...` must be `0044560BN00S0QA0G` | Otherwise stop: the XDF does not fit (see [basics](01-basics.md#why-the-software-version-matters)) |
| `known stock tune` | Your ECU has never been tuned. If it says "differs", someone changed it before. Then your read is still your original, but not stock |
| `ROM test sum` and `Data CRC` correct | The read is complete and not corrupted |
| `Program numbers match` | Flash and MPC belong together (only with the 1 MB file and the MPC) |

## First flash: a dry run

Before your first real change, flash your **unchanged** tune file once (see [step 5](05-check-and-flash.md)). That way you practise the procedure with a file that cannot do any harm. The engine must run exactly as before.

The MS45 Flasher can leave the ECU unusable if a flash is interrupted. Recovery over OBD only works as long as the ECU still responds. Practising with the original is the cheapest insurance.
