# Area 1: Sound and feel

Rev limiter, hard cut, burbles, and the hardware that decides how much you actually hear. None of this adds power.

| I want ... | Go to |
|---|---|
| to rev higher | [Rev limit](#rev-limit) |
| a hard "d-d-d" limiter | [Hard cut](#hard-cut) |
| a lower limit when standing | [Standing limiter](#standing-limiter) |
| burbles when lifting off | [Burbles](#burbles) |
| burbles only on a button | [Sport button](#burbles-only-with-the-sport-button) or [A/C](#experiment-burbles-via-the-ac) |
| louder burbles | [Louder burbles](#louder-burbles) and [Exhaust](#the-exhaust-decides-how-much-you-hear) |
| more intake sound | [Intake](#intake) |
| higher cold idle, no top speed limit | [Idle and top speed](#idle-and-top-speed) |
| pops and bangs, flames | [Level 3: Extreme](#level-3-extreme-pops-bangs-and-flames) |
| everything in levels | [The three levels](#the-three-levels) |

All values are starting points. How it sounds depends on your exhaust, mileage and condition, so test every change yourself, warm and on private ground. How to edit, check and flash: [step-by-step guide](guide.md#step-7-change-the-bin-in-tunerpro).

---

## The three levels

Each level builds on the one before. Within a level, make one file per change: flash, test, read the fault memory, then the next change.

| | Level 1: Mild | Level 2: Strong | Level 3: Extreme |
|---|---|---|---|
| **Sounds like** | Soft crackle when lifting off, harder limiter | Clear burbles and pops, "d-d-d" limiter | Loud bangs on every lift-off, flames with an open exhaust |
| Rev limit | 6700 | 6700-7000 | 7000 |
| Hard cut `c_add_n_max_fcut` | 30 | 15 → 10, prediction 0 | 10, prediction 0 |
| Burble time (in gear / standing) | step 1: up to 1.10 s / 1.10 s | step 2: up to 2.00 s / 1.50 s | 2.00-2.50 s / 1.50 s |
| Overrun cut-off threshold | stock | stock | raised up to 8160 rpm = no fuel cut on overrun |
| Overrun ignition `ip_iga_min_n_maf_pu` | stock | up to 3° later | much later, wider range |
| Exhaust | stock | sport rear silencer | open exhaust / no catalysts for flames |
| Check script | 0 errors, warnings normal | warnings above 1.2 s | warnings; `--expert` if you go past the safe ranges |
| Hint | — | Catalyst gets warmer | Catalyst and exhaust get very hot, more fuel, illegal on public roads |

Details for each change are in the sections below.

---

## Rev limit

| Table | Cells | Stock | New |
|---|---|---|---|
| Rev limit, manual (above 55 km/h) `id_n_max_mt` | all 9 | 6520 | **6700** |
| Rev limit, manual (standing and up to 55 km/h) `id_n_max_h_mt` | all 9 | 6520 | **6700** |

- **Always change both tables.** Changing only `id_n_max_mt` keeps 6520 below 55 km/h. Changing only `id_n_max_h_mt` brings 6520 back above 55 km/h.
- The 9 columns are gears: 0 = no gear detected (standing, neutral), 1-6 = gears, 7 and 8 unused.
- Maximum **7000**. Above that the MS4X wiki warns of engine damage on the M54, and at 7200 the over-rev counter starts.
- The M54B22 makes its peak power around 6100 rpm. A higher limit gives more room before shifting, not more power.
- **Test:** warm, standing, briefly to the limit. It should cut at 6700-6750.

## Hard cut

The stock limiter softly takes away torque and bounces about 1-2 times per second ("hummm"). A smaller threshold makes it bounce faster and harder ("d-d-d").

| Table | Stock | Mild | Clear | Hard |
|---|---|---|---|---|
| Limiter hardness `c_add_n_max_fcut` | 50 | **30** | **15** | **10** |

Bounce rate when the original ECU code runs in an emulator with a simple engine model:

| Threshold | 3rd gear | 5th gear | Overshoot above the limit (3rd) |
|---|---|---|---|
| 50 (stock) | 1.6 /s | 0.8 /s | 53 rpm |
| 30 | 2.8 /s | 1.4 /s | 33 rpm |
| 15 | 5.2 /s | 2.8 /s | 18 rpm |
| 10 | 7.2 /s | 4.2 /s | 13 rpm |

- Not below 10, there is little extra effect.
- Hardest step: additionally set *Limiter prediction time* `id_t_n_max_pred_mt__gear` to 0 in all cells.
- This is a **fuel cut**, not an ignition cut. It sounds dry and fast, it does not bang like a launch control.
- Hint: a hard limiter is a load spike on clutch, drivetrain and differential.
- Fault 28B1 or 28B2 appears: back to 50.
- **Test:** warm, standing, steps 30, 15, 10. Fault memory after each step.

## Standing limiter

In **both** rev limit tables, set **only column 0** (= no gear detected) to **4500**. The engine then only revs to 4500 when standing in neutral.

This is not a launch control. Whether the ECU sees "no gear" long enough while pulling away only shows when you try it.

## Burbles

After you lift off, the ECU keeps injecting for a short time before it cuts fuel. Longer time = more burbling. The fuel burns in the exhaust and makes the sound.

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

How long the ECU keeps injecting, calculated with the original ECU code:

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

- Cold columns stay stock, so a cold engine behaves as before. Between 30 and 60 °C the ECU interpolates: test **fully warm**.
- Shifting stays stock, because a pressed clutch uses its own value.
- Less engine braking during that time is normal.
- In gear the time gets shorter as the revs fall, because the table is read with the current rpm.
- At high rpm the ECU injects longest but with the earliest ignition: longer, but usually quieter than in the mid range.
- Above 1.2 s the torque monitor hold time runs out. That is why step 1 stays below 1.2 s.
- Raising the *overrun cut-off thresholds* is a different method: fuel is then not cut at all below that rpm (continuous injection, loud bangs). That is [level 3](#level-3-extreme-pops-bangs-and-flames).
- **Test:** warm, private ground. Standing: 2500, 4000, 6000 rpm and let go. 3rd gear: lift off at 2000, 3500, 5500 rpm.

## Burbles only with the sport button

Not every E60 has a sport button. If yours has one: put the step 1 values into *Burble duration in gear, sport mode* `ip_t_min_pu_rng_l__n__tco` instead, and leave the normal table stock. In gear, it then only burbles in sport mode. Standing always uses the standing value.

Sport mode also changes the pedal feel, and in stock form the revs already hang about 1.2 s when shifting in sport mode.

## Louder burbles

A freer exhaust (next section) makes it louder without extra heat. Later ignition on overrun also makes it louder, and heats the catalyst and the manifold.

*Latest ignition on overrun* `ip_iga_min_n_maf_pu`: a smaller number means later ignition. Only the first two columns (76 and 98 mg/stroke), only rows 2304-5792 rpm, at most 3 degrees less than stock:

| rpm | column 76 | column 98 |
|---|---|---|
| 2304 | -13.125 | -12.375 |
| 2816 | -10.125 | -8.625 |
| 3616 | -4.875 | -3.000 |
| 4800 | 3.750 | 5.250 |
| 5792 | 9.375 | 12.375 |

How to read ignition values: [glossary, ignition angle](basics.md#glossary). Hint: short tests, the catalyst gets hot on long downhill runs. More: [level 3](#level-3-extreme-pops-bangs-and-flames).

## Experiment: burbles via the A/C

Without a sport button there is no real switch for the burble time. The A/C switches something else: the rpm below which the ECU never cuts fuel on overrun.

*Overrun cut-off threshold, A/C on* `ip_n_accout_min_puc__tco__gr_mt`: rows **60 and 90 °C**, all columns **2400**. Leave the burble duration tables stock.

- A/C off: everything stock.
- A/C on, in gear: after lifting off, fuel is cut briefly, then injection resumes below 2400 rpm until idle (about 3 s in 3rd gear).
- This is continuous injection below 2400, not a short burble. Not higher than 2400.
- The ECU reacts to "compressor on", not to the button. If the compressor does not engage (cold weather, defect), nothing happens.
- **Test:** with A/C on, less engine braking below 2400 rpm means it works.

## Level 3: Extreme (pops, bangs and flames)

Levels 1 and 2 only *delay* the fuel cut. Level 3 is the classic "pops and bangs" method described on the MS4X wiki: the ECU **stops cutting fuel on overrun** in an rpm range, and late ignition on overrun makes the fuel explode in the exhaust.

> Hint: continuous injection on overrun with late ignition makes the catalysts and the exhaust very hot, uses more fuel and wears the catalysts quickly. Flames under the car can damage heat shields, lines and the underbody. Not approvable for public roads.

**1. No fuel cut on overrun.** *Overrun cut-off threshold, A/C off* `ip_n_min_puc__tco__gr_mt`: below this rpm the ECU keeps injecting on overrun.

| Variant | Rows | Value | Effect |
|---|---|---|---|
| Up to 3000 rpm | 60 and 90 °C | 3008 (raw 94) | Bangs on overrun below 3000 rpm |
| Up to 4000 rpm | 60 and 90 °C | 4000 (raw 125) | Bangs in most everyday overrun |
| Always | 60 and 90 °C | **8160** (raw 255) | No fuel cut at all on overrun, warm engine |

- Cold rows stay stock, so a cold engine behaves as before.
- In the emulator, 8160 meant more than 5 s of injection down to idle on a single lift-off.
- **Switchable via A/C:** put the values into *Overrun cut-off threshold, A/C on* `ip_n_accout_min_puc__tco__gr_mt` instead and leave the A/C-off table stock. Then it only bangs with the A/C compressor running.
- The check script shows a warning "threshold very high". That is expected here.

**2. Later ignition on overrun.** *Latest ignition on overrun* `ip_iga_min_n_maf_pu` decides how loud it gets. Level 2 uses 3° later. For level 3:

- Go later in steps of 1.5°, test after each step.
- Use the low-load columns (76 and 98 mg/stroke, then the next ones) and the rows from about 1600 rpm up.
- The check script accepts down to -35°. Below that you need `--expert`.
- Whether the ECU really fires as late as this table allows on overrun has not been traced to the ignition output. If it does not get louder after a step, the ECU limits it elsewhere.

**3. Burble time at the maximum:** in gear up to 2.50 s, standing 1.50 s (see [Burbles](#burbles)).

**4. Flames.** Flames at the tailpipe need unburnt fuel to reach the end of the exhaust and ignite there.

- With **catalysts**, the fuel burns inside them. You get heat and bangs, but rarely visible flames.
- Flames practically need **no catalysts** (decat or test pipes) and a short, open exhaust. That also triggers catalyst and lambda fault codes; this repository does not contain switches to turn those diagnostics off.
- The larger the amount of fuel (threshold 8160) and the later the ignition, the more flames.
- No separate overrun enrichment table has been identified in this software, so the amount of fuel per injection on overrun stays the ECU's own.

**Test:** warm engine, private ground, short series with breaks to let the exhaust cool. Read the fault memory after each series.

---

## The exhaust decides how much you hear

The tune only decides *how long* fuel keeps flowing. How much you hear depends mostly on the exhaust.

- The stock E60 520i exhaust has catalysts, a middle and a rear silencer, built to be quiet. It swallows a lot. With it, burbles are often only faint, even with step 2.
- A **sport rear silencer with an EC type approval** makes the same tune clearly more audible. It does more for burbles than any extra value in the tune, without heating the catalyst. On the M54, drone around **3,500-4,000 rpm** is often reported. Change one thing at a time and drive it for a few weeks.
- **Resonator or muffler delete** (straight pipe): the loudest option. Hint: drones a lot and is illegal on public roads in most countries.
- **Catalysts** swallow a lot of the bangs and turn the fuel into heat. Without them it gets much louder and flames become possible (level 3). Hint: illegal on public roads, causes catalyst and lambda fault codes.
- An **exhaust leak** (manifold, flex pipe, clamps) also pops. Rule it out before judging the tune.

## Intake

- **Snorkel** in front of the airbox removed: noticeably more intake sound inside, especially under load from about 60 % throttle at low rpm. Keep the snorkel for heavy rain, deep water and inspections.
- **Panel filter** (e.g. Pipercross) in the stock airbox: fine. Open cone filters suck in hot engine bay air.
- **Resonator between MAF and throttle** (BMW part `13 71 7 521 035`): removing it gives more intake sound. Everything after the MAF must stay airtight, otherwise the MAF reading is wrong. Keep the small hose to the idle control valve. No aluminium flex pipe there; flex pipe only makes sense before the airbox.
- More intake sound plus a sport exhaust can be too much on long trips.

## Idle and top speed

**Higher cold idle.** *Idle speed, A/C off* `ip_n_sp_is` and *Idle speed, A/C on* `ip_acin_n_sp_is`, **same values in both**:

| °C | -30 | -20 | -10 | 10 | 30 | 60 | 90 | 105 |
|---|---|---|---|---|---|---|---|---|
| Stock | 1120 | 1040 | 960 | 840 | 740 | 680 | 660 | 660 |
| New | **1220** | **1140** | **1060** | **940** | 740 | 680 | 660 | 660 |
| Monitor limit | 1408 | 1346 | 1278 | 1174 | 1088 | 1056 | 1040 | 1032 |

The idle must stay below the monitor limit, which cannot be changed. The check script checks this. Right after a cold start, catalyst heating limits the idle with another table.

**Top speed limiter.** *Top speed limiter* `c_vs_max`, stock 235 km/h, maximum 255 (= off). Only up to your tyre speed rating. A 520i hardly reaches 235 anyway.
