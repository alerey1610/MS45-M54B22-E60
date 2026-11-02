# 8. Tips: exhaust, power, what works, what does not

Things that were learned along the way and that you will not find in one place elsewhere.

## The exhaust decides how much you hear

The tune only decides *how long* fuel keeps flowing after you lift off. How much of that you actually hear depends mostly on the exhaust.

- The stock E60 520i exhaust has catalysts plus a middle and a rear silencer, built to be quiet. It swallows a lot. With the stock exhaust, burbles are often only faint, even with the step 2 recipe.
- A **sport exhaust** or a sport rear silencer makes the same tune clearly more audible. If you want burbles you can hear, an exhaust change does more than any extra value in the tune.
- Try the exhaust before you reach for later ignition on overrun. Later ignition makes it louder too, but it heats the catalyst and the manifold. A freer exhaust does not.
- Keep the catalysts. Removing them is illegal on public roads, triggers faults, and this guide deliberately does not touch the catalyst and lambda monitoring.
- An exhaust leak (manifold, flex pipe, clamps) sounds like popping too. Rule that out before judging the tune.

## The car must be healthy first

- Read the fault memory before you start. VANOS faults (for example P0011) must be fixed before you touch anything; with a sick VANOS, ignition and VANOS tables behave differently anyway.
- Old spark plugs, weak ignition coils and vacuum leaks show up as misfires and rough running. A tune does not fix that, and it makes it harder to tell what caused what.
- Test with a fully warm engine (coolant 90 °C). Between 30 and 60 °C the ECU interpolates, so a half-warm engine gives half the effect.

## Rev limit: more room, not more power

The M54B22 makes its peak power around 6100 rpm and falls off above. A higher limit (6700) gives you more room before shifting, not more power. 7000 is the upper end; above that the valvetrain is at risk and the over-rev counter starts at 7200.

## Hard cut is a fuel cut, not a bang

The hard cut in this software cuts fuel. It gives a dry, fast "d-d-d", not the bangs of a launch control. Those come from an ignition cut, which this software has no parameter for. A hard limiter is still a load spike on clutch, drivetrain and differential: use it standing, only briefly in gear.

## Burbles: time, not threshold

The most common mistake in public "pops and bangs" files for the MS45 is to raise the overrun cut-off threshold (often to 255 raw = 8160 rpm). Then the ECU never cuts fuel on overrun at all: continuous injection on every lift-off, a hot catalyst and higher fuel consumption. The time tables in the [recipes](06-recipes.md) give short, controlled burbles instead.

Other things worth knowing:

- In gear the burble time gets shorter as the revs fall, because the table is read with the current rpm.
- At high rpm the ECU injects longest but with the earliest ignition: longer, but usually quieter than in the mid range.
- Less engine braking during the burble time is normal.
- The A/C reacts to "compressor on", not to the button. On a car where the compressor does not engage, the A/C trick does nothing.
- Not every E60 has a sport button. Check yours before you use the sport-mode table.

## Always test the same way

- One change per file. Name files by version (`tune_v1_revlimit.bin`, `tune_v2_burbles.bin`).
- Fault memory before and after every test.
- Same conditions every time: warm, same place, same gears and rpm.
- Short note per test: file, what you did, what you heard, which faults appeared. After a few files that note is worth more than any table here.
- **Live logging** (rpm, overrun state, ignition angle) is the best value for effort. With a log you can see what the ECU really does instead of guessing by ear.

## More power: what is realistic

The M54B22 is a naturally aspirated 2.2 litre with 170 hp. There is no turbo boost to turn up, so software alone brings little:

- Vendors and forums quote **around 7-10 %** for a "stage 1" on naturally aspirated M54 engines, so roughly **10-15 hp** on the 2.2. Turner quotes +7 hp for the 2.5.
- What you feel most is not peak power but **throttle response**. That is also what gets used to fastest.
- Without a dyno before and after, you will not know whether you gained or lost.

### Where power comes from in the tune

All of these are in the XDF. The standard XDF lets you edit the ignition maps and full-load lambda (marked [CAUTION]). VANOS, DISA, coolant and pedal are only editable in the [expert XDF](../xdf/expert/).

| Area | Tables | What it does | What you need |
|---|---|---|---|
| **Ignition** | `ip_iga_bas_ron_98__n__maf` (`0x4AE64`), `ip_iga_bas_ron_91__n__maf` (`0x4AD24`) | Main ignition maps. Knock control interpolates between the RON 98 map and the safer RON 91 map. More advance = more torque until knock starts | **Knock logging**, RON 98 fuel, small steps (0.75-1.5°), one area at a time. Never advance the RON 91 map |
| Ignition offsets | `ip_iga_bas_add_min/max_ivvt__n__maf`, `ip_iga_bas__n__maf` (without VANOS) | Offsets for valve overlap, fallback map on VANOS faults | Leave unless you know why |
| **VANOS** | `ip_cam_sp_1_in_pl__n__maf_ivvt` (intake), `ip_cam_sp_1/2_ex_pl__n__maf_ivvt` (exhaust) | Cam timing in part load: torque curve, idle quality, emissions | A healthy VANOS (no P0011/P0014, good solenoids and seals), dyno |
| **Full-load lambda** | `ip_lamb_fl__n` (stock 0.89-0.96) | Mixture at full throttle. Richer protects, leaner can damage | An external **wideband lambda sensor**. The stock sensors are narrowband and cannot measure this |
| Full-load detection | `ip_pv_max_fl__n` (stock 66 % pedal) | From which pedal position full-load enrichment applies. Not a pedal curve | Only small changes |
| **DISA** | `c_n_vim_l` (2200), `c_n_vim_h` (4100), `c_fac_maf_max_vim` (0.70) | Switching points of the intake manifold flap. Must match the intake model | Only on a dyno, the effect is small and easy to make worse |
| Coolant target | `id_tco_sp_ect`, `id_tco_sp_ect_acin` | Lower target = thermostat opens earlier, less knock, better filling | Costs fuel, slower warm-up, weaker heater, fan runs more. Only with a healthy thermostat |
| **Throttle response** | `ip_fac_tq_req_driv` (pedal map) | The real pedal map: requested torque over rpm and pedal | The torque monitor has a copy (`_mon`) inside the ROM test area. Changing the pedal map alone triggers a monitoring fault. Unsolved, a good project for someone |
| Anti-jerk filter | function `TQM_Torque_based_anti_jerk` in the A2L | Makes load changes soft ("lazy" feel) | Not analysed yet |

The torque path (`ip_tqi_ref__n__maf`, `ip_maf_sp`, `id_tq_p_max_mt`) is tied to the monitoring. Leave it alone.

### Order that makes sense for power

1. Healthy engine: no faults, good plugs and coils, no vacuum leaks, VANOS working.
2. Baseline: dyno run or at least logs of a full-throttle pull.
3. Ignition in small steps with knock logging.
4. Full-load lambda only with a wideband sensor.
5. VANOS and DISA only on a dyno.
6. Dyno again. If you gained nothing, flash back.

## Hardware: intake and exhaust

Parts change the **sound** much more than the power. From experience on this engine:

- **Intake snorkel** in front of the airbox removed: noticeably more intake sound inside the car, especially under load from about 60 % throttle at low rpm. No measurable power. Keep the snorkel for heavy rain, deep water and inspections.
- **Panel filter** (e.g. Pipercross) in the stock airbox: fine, little effect. Open cone filters suck in hot engine bay air.
- **Resonator between MAF and throttle** (part `13 71 7 521 035`): removing it gives more intake sound. Everything after the MAF must stay airtight, otherwise the MAF reading is wrong (unmetered air). Keep the small hose to the idle control valve. No aluminium flex pipe there; flex pipe only makes sense before the airbox.
- **Rear silencer with an EC type approval** (sport silencer): the most effective change for burbles and sound. On the M54, drone around **3,500-4,000 rpm** is often reported. Combined with an open intake it can be too much on long trips, so change one thing and drive it for a few weeks.
- **Resonator or muffler delete** (straight pipe): loud, drones, attracts attention and is illegal on public roads in most countries. Not recommended.
- **Headers, high-flow cats:** expensive, small gains on the 2.2, and emissions problems.

## Legal (Germany as an example)

- There is practically no type approval (ABE) for ECU software. Legal only with an individual approval (§21 StVZO) with emissions and noise measurement, which costs several hundred euros or more.
- Burbles and pops are not approvable on public roads: changed overrun behaviour affects emissions and noise (§19, §30 StVZO). The registration can lapse and insurance can refuse to pay.
- Offers advertised as "undetectable" are not legal either.
- Other countries have similar rules. Check yours.

## Not possible without a program patch

| Idea | Note |
|---|---|
| Launch control with ignition cut | Needs a program patch. No public recipe for this MS45 software |
| No-lift-shift | Program patch, high gearbox load |
| "Popcorn" limiter (bangs at the limiter) | No parameter found, and the worst option for the catalyst |
| Switching between tunes in the car | Only exists for the MS45.1 and needs a program patch |
| Automatic blipping on downshifts | Missing input and program code |
| Anti-lag | Only useful on turbo engines |

## Deliberately not covered

Turning off the catalyst, lambda or secondary air monitoring, OBD, or "flame" tunes. They are illegal on public roads, can cause fires or damage, and are not part of this project. None of the XDFs, including the expert one, contains diagnostic switches for the catalyst, lambda sensors, secondary air or OBD.

## Before public roads

Flash your original tune back before driving on public roads and before every inspection. Keep the original file where you can always reach it, including on the laptop you flash with.
