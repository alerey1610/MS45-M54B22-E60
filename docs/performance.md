# Area 2: Performance

More power and better response from ignition, VANOS, mixture and intake. Read the first section before you buy anything.

| I want ... | Go to |
|---|---|
| to know what is realistic | [What to expect](#what-to-expect) |
| to know what it costs | [Costs](#costs) |
| to know what I must be able to measure | [Measuring: logging, knock, lambda, dyno](#measuring-logging-knock-lambda-dyno) |
| to know which tables matter | [Where power comes from](#where-power-comes-from) |
| to understand ignition values | [Reading ignition maps](#reading-ignition-maps) |
| a plan | [The three levels](#the-three-levels) |
| to edit everything myself | [Expert XDF](#expert-xdf) and [sensitive tables](#sensitive-tables-in-the-expert-xdf) |

---

## What to expect

The M54B22 is a naturally aspirated 2.2 litre with 170 hp. There is no turbo boost to turn up.

- Vendors and forums quote **around 7-10 %** for a "stage 1" on naturally aspirated M54 engines, so roughly **10-15 hp** on the 2.2. Turner quotes +7 hp for the M54 2.5.
- What you notice most is **throttle response**, not peak power. You also get used to it quickly.
- A higher rev limit gives **no** extra power: the M54B22 peaks around 6100 rpm.
- Intake and exhaust parts change mostly the **sound**, see [Sound and feel](sound.md#the-exhaust-decides-how-much-you-hear). Headers and high-flow cats are expensive, bring little on the 2.2 and cause emissions problems.
- Without measuring before and after, you will not know whether you gained or lost power. Hint: too much ignition advance damages pistons without warning.

For a lot more power the usual route is a bigger engine (M54B25/B30), not software.

## Costs

Rough prices, they vary by country and shop:

| What | Roughly | Needed for |
|---|---|---|
| K+DCAN cable | 20-40 € | everything |
| Battery charger / power supply | 30-80 € | everything |
| Dyno run, before and after | 80-200 € per session | any power tuning |
| Wideband lambda kit (sensor + gauge or logger) | 150-300 €, plus welding a sensor bung into the exhaust | full-load mixture |
| Sport rear silencer with EC approval | from about 300 € | sound |
| Legal approval of the tune (Germany: §21 individual approval) | several hundred to over 1,000 € | road use |

## Before you start

1. **The engine must be healthy.** No faults (step 3 of the [guide](guide.md#step-3-read-the-fault-memory-before-you-start)), good spark plugs and ignition coils, no vacuum leaks, VANOS working (no P0011/P0014, good solenoids and seals), clean MAF.
2. Use **RON 98** fuel for all tests. The ignition maps assume it.
3. Make the [sound](sound.md) changes first if you want them. Then you know the procedure, and you know your car runs fine with a modified file.

## Measuring: logging, knock, lambda, dyno

You need to see what the engine does. Three kinds of measurement:

**Live logging (rpm, load, ignition, knock).**
- INPA shows live values in the DME status screens. Good for a quick look, not for recording a full-throttle pull.
- For recordings, use a logger that reads EDIABAS values into a CSV file (for example the free *Test0*, or paid tools like ByteTuner).
- Log at least: rpm, load (air mass), ignition angle, **knock control retard per cylinder**, intake air temperature, coolant temperature.

**Knock.**
- The ECU has knock sensors. When it detects knock, it pulls ignition back on that cylinder. In the log that shows as a retard value above 0.
- If you add ignition and see retard in the cells you changed, the engine knocks there. Go back. More retard = less power and more risk.
- If you see no retard at all after a change, that does not prove it is safe, only that the sensors did not detect anything. Small steps.

**Lambda (mixture).**
- The stock sensors are **narrowband**: they can only tell rich or lean around lambda 1. They cannot measure the full-load mixture.
- For full-load changes you need a **wideband** sensor (installed in the exhaust or the one on the dyno).

**Dyno.**
- One run before you change anything, one after each bigger change. Same fuel, similar temperature, warm engine.
- If you gained nothing, flash the original back.

## Where power comes from

All these tables are in the XDF. The standard XDF lets you edit the ignition maps and full-load lambda (marked **[CAUTION]**). The others are **[READ ONLY]** there and editable in the [expert XDF](#expert-xdf).

| Area | Tables | What it does | What you need |
|---|---|---|---|
| **Ignition** | `ip_iga_bas_ron_98__n__maf` (`0x4AE64`) | Main ignition map. More advance = more torque, until knock starts | Knock logging, RON 98, small steps |
| | `ip_iga_bas_ron_91__n__maf` (`0x4AD24`) | Safe map for lower octane. Knock control interpolates between RON 98 and RON 91 | Hint: this is the safety net when knock is detected. Advancing it removes that margin |
| | `ip_iga_bas_add_min/max_ivvt__n__maf`, `ip_iga_bas__n__maf` | Offsets for valve overlap, fallback map on VANOS faults | Only relevant together with VANOS changes |
| **VANOS** | `ip_cam_sp_1_in_pl__n__maf_ivvt` (intake), `ip_cam_sp_1/2_ex_pl__n__maf_ivvt` (exhaust) | Cam timing in part load: torque curve, idle quality, emissions | Healthy VANOS, dyno |
| **Full-load mixture** | `ip_lamb_fl__n` (stock 0.89-0.96) | Lambda at full throttle. Richer protects, leaner can damage | Wideband sensor |
| Full-load detection | `ip_pv_max_fl__n` (stock 66 % pedal) | From which pedal position full-load enrichment applies. Not a pedal curve | Small changes only |
| **DISA** | `c_n_vim_l` (2200), `c_n_vim_h` (4100), `c_fac_maf_max_vim` (0.70) | Switching points of the intake manifold flap. Must match the intake model | Dyno. Small effect, easy to make worse |
| Coolant target | `id_tco_sp_ect`, `id_tco_sp_ect_acin` | Lower target = thermostat opens earlier, less knock, better filling | Costs fuel, slower warm-up, weaker heater, fan runs more. Healthy thermostat |
| **Throttle response** | `ip_fac_tq_req_driv` (pedal map) | The real pedal map: requested torque over rpm and pedal | **Unsolved.** The torque monitor has a copy (`ip_fac_tq_req_driv_mon`) inside the protected ROM test area. Changing the pedal map alone triggers a monitoring fault. A good project for someone |
| Anti-jerk filter | function `TQM_Torque_based_anti_jerk` in the A2L | Softens load changes ("lazy" feel) | Not analysed yet |

## Reading ignition maps

- Values are in **degrees crankshaft before top dead centre**. A positive number fires before the piston reaches the top.
- **Bigger number = earlier ignition (more advance).** Smaller or negative = later (retard).
- Rows are rpm, columns are load (air mass per stroke, mg/stroke). Full throttle is in the right-hand columns.
- The smallest step in the table is 0.375°. Change high-load cells by **0.75-1.5° at a time**, one rpm range at a time.
- More advance gives more torque only up to a point. After that it gives knock, which the ECU answers with retard: you lose power and stress the engine.
- Later ignition (smaller numbers) makes the exhaust hotter. That is what the [louder burbles](sound.md#louder-burbles) use on overrun; under load it only costs power.

## The three levels

Each level builds on the one before. Within a level: one change per file, log it, then the next change.

| | Level 1: Mild | Level 2: Strong | Level 3: Max |
|---|---|---|---|
| **Gain (rough)** | a few hp, better response at full throttle | up to about 7-10 % (10-15 hp) | what the 2.2 can give; beyond that only hardware |
| Ignition RON 98 | +0.75 to 1.5° in the full-load cells | further steps of 0.75° up to just below the knock limit | at the knock limit in every rpm range, measured |
| Ignition RON 91 | stock | stock | stock (safety net for bad fuel) |
| Full-load mixture `ip_lamb_fl__n` | stock | towards about 0.86-0.88, measured with a wideband | best value per rpm on the dyno |
| VANOS (expert XDF) | stock | stock | optimised on the dyno |
| DISA switching points (expert XDF) | stock | stock | matched on the dyno |
| Coolant target (expert XDF) | stock | stock | lower, if you accept more fuel use and a weaker heater |
| Rev limit | stock | 6700 | 7000 (no power gain, more room) |
| Hardware | none | sport exhaust, panel filter | intake without resonator, sport exhaust, headers and sport catalysts or decat |
| Measuring | knock log | knock log + wideband | knock log + wideband + dyno before and after |
| Check script | standard | standard | `--expert` |
| Hint | — | Wrong lambda or too much advance damages the engine | Decat: illegal on public roads, catalyst and lambda fault codes |

**How each level works in practice:**

1. Baseline: dyno run or at least a logged full-throttle pull in 3rd gear, warm engine, RON 98.
2. One change, one file, check, flash.
3. Same pull again, compare: knock retard, power, lambda.
4. Retard appears in the changed cells: go back one step.
5. No gain: back to the previous file.

The pedal map (throttle response) is still unsolved, see the table above.

## Expert XDF

`xdf/expert/` contains the same XDF for the tune file and for the 1 MB image, but with **all 1707 known parameters** and nothing marked read only. Entries inside the monitoring checksum area are marked **[ROM TEST]**.

Check expert files with:

```bat
py tools/ms45_check.py --expert stock_tune.bin tune_v1.bin
```

With `--expert` these become warnings instead of errors: read-only parameters, bytes without a known parameter, values outside the safe range, rev limit above 7000. These stay errors, because the ECU itself reacts to them: wrong software, changes outside the tune area or in the identification block, anything in the ROM test area, idle above the monitor limit, a signature that would crash the flasher.

Most of the 1707 parameters come straight from BMW's description file (A2L). Their names and descriptions are technical, a few are in German, and nobody has checked what all of them do.

## Sensitive tables in the expert XDF

| What | Examples | Why |
|---|---|---|
| Anything marked **[ROM TEST]** | `ip_tqi_ref_mon`, `ip_n_sp_is_mon_max_mon` | Breaks the monitoring checksum. The check script always blocks it |
| Torque path and torque limits | `ip_tqi_ref__n__maf`, `ip_maf_sp`, `id_tq_p_max_mt` | Tied to the torque monitor. Wrong values cause limp mode or monitoring faults |
| Monitoring copies | names ending in `_mon`, `_mon2` | Same as above |
| Checksum values and switches | `val_mo3_*` | Safety function |
| Logic switches | names starting with `lc_` | Turn whole functions on and off. Effects not traced |
| Sensor conversion curves | e.g. `ip_toil__v_toil` (voltage to temperature) | The ECU would read wrong temperatures, pressures or positions |
| Injector data | `ip_ti_add_dly` and similar | Only if you change injectors |

Rule of thumb: change a table when you know what it does and how you will measure the result.
