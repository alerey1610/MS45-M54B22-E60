# 6. Recipes: what to enter for which goal

All values are for a warm engine and private ground. Check every file with `ms45_check.py` before flashing, and read the fault memory before and after each test.

**Good order:** first file with the rev limit and the hard cut only. Second file adds burbles. Louder burbles last, and only if needed. That way you always know which change caused a fault.

"Confirmed" means the ECU's original code was run in an emulator with this change. "Partial" means the code path is proven, but sound and feel only show in the car.

---

## Rev limit 6700 rpm (confirmed)

| Table | Cells | Stock | New |
|---|---|---|---|
| Rev limit, manual (above 55 km/h) `id_n_max_mt` | all 9 | 6520 | **6700** |
| Rev limit, manual (standing and up to 55 km/h) `id_n_max_h_mt` | all 9 | 6520 | **6700** |

**Always change both tables.** If you only change `id_n_max_mt`, the limit stays at 6520 below 55 km/h. If you only change `id_n_max_h_mt`, it goes back to 6520 above 55 km/h.

- Maximum 7000. Above that the MS4X wiki warns of engine damage, and at 7200 the over-rev counter starts.
- The M54B22 makes little extra power up there. This mainly gives you more room before shifting.
- Test: standing, warm, briefly to the limit. It should cut at 6700-6750.

## Harder limiter, "hard cut" feel (partial)

The stock limiter softly takes away torque and bounces about 1-2 times per second ("hummm"). A smaller threshold makes it bounce faster and harder ("d-d-d").

| Table | Stock | Mild | Clear | Hard |
|---|---|---|---|---|
| Limiter hardness `c_add_n_max_fcut` | 50 | **30** | **15** | **10** |

Bounce rate in the emulator model:

| Threshold | 3rd gear | 5th gear | Overshoot above the limit (3rd) |
|---|---|---|---|
| 50 (stock) | 1.6 /s | 0.8 /s | 53 rpm |
| 30 | 2.8 /s | 1.4 /s | 33 rpm |
| 15 | 5.2 /s | 2.8 /s | 18 rpm |
| 10 | 7.2 /s | 4.2 /s | 13 rpm |

- Not below 10, there is little extra effect.
- Optional for the hardest step: set *Limiter prediction time* `id_t_n_max_pred_mt__gear` to 0 in all cells.
- This cuts fuel, not ignition. It does not pop like a launch control. Real launch control or no-lift-shift would need a program patch and is not possible in the tune area.
- A hard limiter is a load spike on clutch, drivetrain and differential. Use it standing, only briefly in gear.
- Fault 28B1 or 28B2: back to 50.

## Separate limit when standing (partial)

In **both** rev limit tables, set **column 0 only** (= no gear detected) to **4500**. The engine then revs only to 4500 when standing in neutral.

This is not launch control. Whether the ECU sees "no gear" long enough while pulling away only shows in a log.

## Burbles when lifting off (partial)

After you lift off, the ECU keeps injecting for a short time before it cuts fuel. Longer time = more burbling.

**Step 1:**

| Table | Where | Stock | New |
|---|---|---|---|
| Burble duration, in gear `ip_t_min_pu__n__tco` | columns **60 and 90 °C** only, rows: | 0.22-0.28 | 1600 = **0.40**, 2400 = **0.70**, 3600 = **1.00**, 4800 = **1.10**, 6500 = **1.10** |
| Burble duration, standing `c_t_min_pu_vs` | single value | 0.18 | **1.10** |

**Step 2** (only if the fault memory stayed clean after step 1):

| Table | New |
|---|---|
| In gear, 60 and 90 °C | 1600 = 0.40, 2400 = 0.70, 3600 = 1.10, 4800 = 1.50, 6500 = 2.00 |
| Standing | 1.50 |

What happens, calculated with the original ECU code:

| Situation | Stock | Step 1 | Step 2 |
|---|---|---|---|
| Standing, 2500 rpm | 0.19 s | 0.50 s | 0.50 s |
| Standing, 4000 rpm | 0.19 s | 1.10 s | 1.10 s |
| Standing, 6000 rpm | 0.19 s | 1.11 s | 1.51 s |
| 3rd gear, 2000 rpm | 0.40 s | 0.50 s | 0.50 s |
| 3rd gear, 3500 rpm | 0.40 s | 0.90 s | 0.95 s |
| 3rd gear, 5500 rpm | 0.40 s | 1.11 s | 1.49 s |
| 3rd gear, cold (30 °C) | 0.40 s | 0.40 s | 0.40 s |
| Shifting (clutch pressed) | 0.11 s | 0.11 s | 0.11 s |

- Cold columns stay stock, so a cold engine behaves as before. Between 30 and 60 °C it interpolates, so test fully warm.
- Shifting stays stock, because a pressed clutch uses its own value.
- Less engine braking during that time is normal.
- Above 1.2 s the torque monitor hold time runs out. What happens after that is not fully known. That is why step 1 stays below 1.2 s.
- **Do not** raise the *overrun cut-off thresholds* for burbles. A high value there (often 255 raw / 8160 rpm in public files) means continuous injection on the whole overrun, not short burbles.

## Burbles only with the sport button (partial)

If your car has a sport button: put the step 1 values into *Burble duration in gear, sport mode* `ip_t_min_pu_rng_l__n__tco` instead, and leave the normal table stock. In gear, it then only burbles with sport mode on. Standing always uses the standing value.

Sport mode also changes the pedal feel, and in stock form the revs already hang about 1.2 s when shifting in sport mode.

## Louder burbles (partial, last step)

Only if the burbles are too quiet. *Latest ignition on overrun* `ip_iga_min_n_maf_pu`: a smaller number means later ignition, which is louder but makes the catalyst and the manifold hotter.

Only the first two columns (76 and 98 mg/stroke), only rows 2304-5792 rpm, at most 3 degrees less than stock:

| rpm | column 76 | column 98 |
|---|---|---|
| 2304 | -13.125 | -12.375 |
| 2816 | -10.125 | -8.625 |
| 3616 | -4.875 | -3.000 |
| 4800 | 3.750 | 5.250 |
| 5792 | 9.375 | 12.375 |

Test only briefly, never many times in a row, no long downhill runs. In stock form the ignition is later at low rpm than at high rpm, so burbles at high rpm are longer but quieter.

## Experiment: burbles via the A/C (partial)

Without a sport button there is no real switch for the burble time. The A/C switches something else: the rpm below which the ECU never cuts fuel on overrun.

*Overrun cut-off threshold, A/C on* `ip_n_accout_min_puc__tco__gr_mt`: rows **60 and 90 °C**, all columns **2400**. Leave the burble duration tables stock.

- A/C off: everything stock.
- A/C on, in gear: after lifting off, fuel is cut briefly, then injection resumes below 2400 rpm until idle (about 3 s in 3rd gear).

This is continuous injection below 2400, not a short burble. It only works if the ECU actually sees "compressor on". Test: with A/C on, less engine braking below 2400 rpm means it works. Not higher than 2400.

## Higher cold idle (partial)

*Idle speed, A/C off* `ip_n_sp_is` and *Idle speed, A/C on* `ip_acin_n_sp_is`, **same values in both**:

| °C | -30 | -20 | -10 | 10 | 30 | 60 | 90 | 105 |
|---|---|---|---|---|---|---|---|---|
| Stock | 1120 | 1040 | 960 | 840 | 740 | 680 | 660 | 660 |
| New | **1220** | **1140** | **1060** | **940** | 740 | 680 | 660 | 660 |
| Monitor limit | 1408 | 1346 | 1278 | 1174 | 1088 | 1056 | 1040 | 1032 |

The idle must stay below the monitor limit, which cannot be changed. `ms45_check.py` checks this. During catalyst heating right after a start, another table limits the idle.

## Top speed limiter (partial)

*Top speed limiter* `c_vs_max`, stock 235 km/h, maximum 255 (= off). Only up to your tyre speed rating. A 520i hardly reaches 235 anyway.
