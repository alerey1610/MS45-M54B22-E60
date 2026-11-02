# Step-by-step guide

From zero to a flashed and tested tune. Do the steps in order. Every step says what you should see and what to do if you do not.

**Time:** plan 2-3 hours for the first complete run (step 1-3 once, then about 30 minutes per tune).

| Step | What | Done once or every time |
|---|---|---|
| [0](#step-0-check-that-your-car-fits) | Check that your car fits | once |
| [1](#step-1-download-and-install-the-programs) | Download and install the programs | once |
| [2](#step-2-connect-the-cable) | Connect the cable | every session |
| [3](#step-3-read-the-fault-memory-before-you-start) | Read the fault memory before you start | every session |
| [4](#step-4-read-the-ecu-download-your-bin) | Read the ECU, download your bin | once (backup), later for verification |
| [5](#step-5-check-your-bin) | Check your bin | once |
| [6](#step-6-dry-run-flash-the-unchanged-file) | Dry run: flash the unchanged file | once |
| [7](#step-7-change-the-bin-in-tunerpro) | Change the bin in TunerPro | every tune |
| [8](#step-8-check-the-changed-bin) | Check the changed bin | every tune |
| [9](#step-9-flash) | Flash | every tune |
| [10](#step-10-test-and-read-the-fault-memory) | Test and read the fault memory | every tune |

Words you do not know are explained in the [glossary](basics.md#glossary).

---

## Step 0: Check that your car fits

This guide is only for:

- BMW E60 520i with the **M54B22** engine
- **Manual gearbox.** Automatic cars use other rev limit tables, and the check script does not know them. Automatic is not supported here.
- Siemens **MS45.0** ECU with software **`0044560BN00S0QA0G`**

You only see the software version after step 4 ("Identify DME"). If it is different, stop there: the addresses in the XDF would be wrong. You have only spent money on the cable by then. Other software versions: see the [pazi88 definitions](https://github.com/pazi88/Siemens_ms45_RR-definitions); this guide cannot help with those.

## Step 1: Download and install the programs

You need a **Windows laptop**. The flasher, INPA and TunerPro only run on Windows. On a Mac, use a Windows PC or Boot Camp; a virtual machine often has trouble with the USB cable timing.

| # | Program | Where | What for |
|---|---|---|---|
| 1 | Driver for the cable (FTDI VCP driver) | [ftdichip.com](https://ftdichip.com/drivers/vcp-drivers/) | Makes the cable a COM port |
| 2 | **BMW Standard Tools** (EDIABAS, INPA, NCS Expert) | Usually comes with the K+DCAN cable or from BMW coding communities | INPA reads the fault memory. EDIABAS is the communication layer the flasher uses |
| 3 | ECU description file **`MS450DS0.prg`** | Part of the Standard Tools / SP-Daten. Must be in `C:\Ediabas\ECU` | Without it, EDIABAS cannot talk to the MS45 |
| 4 | **.NET Framework 4.5.2** or newer | [microsoft.com](https://dotnet.microsoft.com/download/dotnet-framework) (already on most Windows 10/11 PCs) | Needed by the flasher |
| 5 | **MS45 Flasher** | [terraphantm/MS45-Flasher](https://github.com/terraphantm/MS45-Flasher), "Releases" on the right | Reads and flashes the ECU |
| 6 | **TunerPro RT** | [tunerpro.net](https://www.tunerpro.net), Downloads | Editing the bin with the XDF |
| 7 | **Python 3** | [python.org](https://www.python.org/downloads/). In the installer tick **"Add python.exe to PATH"** | Runs the check script |
| 8 | **This repository** | Green "Code" button at the top of the [repository page](https://github.com/alerey1610/MS45-M54B22-E60), "Download ZIP", unpack it, e.g. to `C:\MS45` | XDF and check script |

Windows SmartScreen may warn about the flasher or TunerPro ("unknown publisher"). That is normal for small open-source tools: "More info", "Run anyway".

### How to run the check script

Open the folder `C:\MS45` in Explorer, click into the address bar, type `cmd` and press Enter. A black window opens in that folder. Commands in this guide look like this:

```bat
py tools/ms45_check.py my_read.bin
```

- On Windows the command is **`py`**. `python3` often opens the Microsoft Store instead. On macOS and Linux use `python3`.
- Instead of typing a file name, you can drag the file from Explorer into the black window. Windows then inserts the full path.
- Paths with spaces need quotes: `py tools/ms45_check.py "C:\My Files\read.bin"`.

Test it once: `py tools/ms45_check.py --help` must print the usage text.

## Step 2: Connect the cable

Every session:

1. **Charger or power supply on the battery, 13.5-14 V.** The voltage must not drop while flashing. Do not rely on the battery alone. A running donor car with jump leads works if it is connected before you start and nothing is touched during the flash.
2. Laptop on mains power. Windows sleep and standby off (Settings, System, Power).
3. Plug the cable into the OBD port (driver footwell, left, under the dashboard) and into the laptop.
4. **Ignition on, engine off.** Lights, radio, fan and other consumers off.

Once, the first time:

5. Device Manager, Ports (COM & LPT), "USB Serial Port", Properties, Port Settings, Advanced:
   - **COM port number: COM1** (EDIABAS uses COM1 by default)
   - **Latency Timer: 1 ms**
6. Cable with a switch: set it as the seller describes for your car's build date. If the flasher cannot identify the DME later, try the other position.

**Test:** start INPA. The battery and ignition indicators at the top must be filled (black). If ignition stays empty: check ignition, COM port and the switch on the cable.

## Step 3: Read the fault memory before you start

You need to know which faults were there **before** you changed anything. Otherwise you cannot tell later whether a fault comes from your tune.

1. INPA, choose the series (E60), then engine, then the DME (MS45).
2. Open the fault memory (usually **F4**) and read it.
3. **Take a photo or screenshot** of all entries. Write the date next to it.
4. Do not delete anything yet.

What it tells you:

| You see | Meaning |
|---|---|
| No entries | Good starting point |
| VANOS faults (e.g. P0011, P0014, camshaft) | Fix them first. With a sick VANOS, ignition and VANOS changes behave differently and power tuning makes no sense |
| Misfires, lambda, MAF, vacuum leak | Fix them first. A tune does not repair this, and it hides what your changes do |
| Battery or voltage faults from earlier work | Usually harmless, note them |

A generic OBD2 reader only shows standard P-codes. BMW-specific codes need INPA or a similar BMW tool.

## Step 4: Read the ECU (download your bin)

1. Close INPA (it blocks the COM port).
2. Start the MS45 Flasher.
3. Click **Identify DME**. The window shows DME type, hardware and software reference.
   - It must say **MS45.0** and software **`0044560BN00S0QA0G`**. Otherwise stop (see step 0).
   - If nothing happens: check EDIABAS, `MS450DS0.prg`, COM1, latency, cable switch.
4. **Full backup:** tick **Full Binary**, click **Read DME**. Do not touch anything until it is done (a few minutes). You get two files: `..._Flash.bin` (1 MB) and `..._MPC.bin` (448 KB).
5. **Read it a second time** into different file names (e.g. add `_2`). You compare both reads in step 5.
6. **Tune file:** untick **Full Binary**, click **Read DME** again. You get the tune file with 118,784 bytes. This is the file you will edit.
7. Copy all files to two other places (USB stick, cloud). Right-click, Properties, tick "Read-only".

Name the files so you recognise them, e.g. `stock_flash.bin`, `stock_flash_2.bin`, `stock_mpc.bin`, `stock_tune.bin`.

## Step 5: Check your bin

In the black window in `C:\MS45`:

```bat
py tools/ms45_check.py stock_flash.bin stock_mpc.bin
```

You should see:

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
| `software 0044560BN00S0QA0G` | Your ECU fits. Anything else: stop |
| `known stock tune` | Never tuned before. "differs" means someone changed it already; then your read is your original, but not stock |
| `ROM test sum`, `Data CRC` correct | The read is complete |
| `Program numbers match` | Flash and MPC belong together |

Compare the two full reads:

```bat
py tools/ms45_check.py stock_flash.bin stock_flash_2.bin
```

It must say `File is identical to the original (dry run)` and `No differences`. If not, read again; the cable connection was not stable.

Check the tune file as well:

```bat
py tools/ms45_check.py stock_tune.bin
```

## Step 6: Dry run: flash the unchanged file

Before your first real change, flash your **unchanged** `stock_tune.bin` once, exactly as in [step 9](#step-9-flash). That way you practise the procedure with a file that cannot do any harm. The engine must run exactly as before.

The flasher can leave the ECU unusable if a flash is interrupted. Practising with the original is the cheapest insurance.

## Step 7: Change the bin in TunerPro

1. **Copy** `stock_tune.bin`, e.g. to `tune_v1.bin`. Only ever edit the copy.
2. TunerPro: **File, Open Bin**, select `tune_v1.bin`.
3. **XDF, Select XDF**, select `xdf/MS45_E60_520i_TuneFile.xdf`.
   - For a 1 MB file use `MS45_E60_520i_FullFlash.xdf` instead. The wrong combination shows wrong values.
4. On the left you see categories like `01 Rev limiter`. Double-click an entry to open the table.
5. **Check that it loaded correctly:** *Rev limit, manual (above 55 km/h)* must show 9 columns labelled 0 to 8, all with 6520.
6. Change values:
   - Select cells with the mouse (or click a row or column header).
   - Type the new value, press Enter.
   - For many cells: select them, in the toolbar choose the function (**Set** or **Offset (+/-)**), enter the value, **Execute**.
7. Each entry has a description with stock value, allowed range, recipe and test. In the table window, open the item properties or info view (the "i" / properties button, depending on the TunerPro version).
8. **File, Save Bin.**

What to change: see the two areas, [Sound and feel](sound.md) and [Performance](performance.md).

Rules:

- **One idea per file.** Rev limit first, burbles in the next file. If a fault appears, you know where it came from.
- Name files by version: `tune_v1_revlimit.bin`, `tune_v2_burbles.bin`.
- If TunerPro asks for a checksum plugin: ignore it. The flasher calculates CRC and signature.

## Step 8: Check the changed bin

```bat
py tools/ms45_check.py stock_tune.bin tune_v1.bin
```

- **0 errors:** you may flash. Read the warnings anyway.
- **Any `ERROR`: do not flash.** The [error table](troubleshooting.md#check-script-messages) explains every message.
- Note the line `SHA-256 0x40000-0x5CFFF: ...` at the end. You need it in step 9.

Files made with the expert XDF: `py tools/ms45_check.py --expert stock_tune.bin tune_v1.bin` (see [Performance](performance.md#expert-xdf)).

## Step 9: Flash

1. Everything from [step 2](#step-2-connect-the-cable): charger, laptop on mains, ignition on, engine off, consumers off. INPA closed.
2. MS45 Flasher: **Identify DME**.
3. **Untick "Full Binary".**
4. **Load File**, select your checked file.
   - If the flasher says *"Loaded tune does not match DME's program"*: click **No**. Wrong file.
5. **Flash Tune.** Wait. Do not touch the cable, the laptop or the car.
6. Read the status line at the end. If something failed (security access, erase), the flasher may continue anyway. So always do the next step.
7. **Read back:** untick Full Binary, **Read DME**, save as e.g. `readback_v1.bin`.
8. Check the read back:

   ```bat
   py tools/ms45_check.py readback_v1.bin
   ```

   The `SHA-256 0x40000-0x5CFFF` line must be identical to the one from step 8. Then the ECU contains exactly your file.

Never use **Flash Program**. It rewrites the program part and is much riskier. You never need it for tuning.

If the flash stops halfway: see [Recovery](troubleshooting.md#the-flash-failed-or-the-ecu-does-not-respond).

## Step 10: Test and read the fault memory

1. INPA: read the fault memory, compare with your photo from step 3, then **delete** it.
2. Start the engine. Let it idle for a minute. Rough idle or warning lights: switch off, flash the original.
3. Drive until the engine is **fully warm** (coolant around 90 °C, usually 15-20 minutes). Many changes only act when warm.
4. Test on **private ground**, as described for each change in [Sound](sound.md) or [Performance](performance.md).
5. INPA: read the fault memory again. New entries? Look them up in the [fault code table](troubleshooting.md#fault-codes-you-may-see).
6. Write a short note: file, what you changed, what you noticed, which faults appeared. Sharing it helps others: [report your result](https://github.com/alerey1610/MS45-M54B22-E60/issues/new?template=test-report.md).

**Back to stock:** flash `stock_tune.bin` exactly like step 9. Do this before driving on public roads and before every inspection.
