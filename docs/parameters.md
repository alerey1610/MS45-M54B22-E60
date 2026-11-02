# 8. Parameter reference

All curated parameters in the XDF, generated from [`data/parameters.json`](../data/parameters.json). Addresses are 1 MB flash addresses; in the tune file subtract `0x40000`.

The JSON also lists 1650 further parameters from the A2L (categories starting with `90 Reference`). They are not in the XDF. The check script knows them only to name them in a diff, and it blocks any change to them.

## 01 Rev limiter

### Rev limit, manual (above 55 km/h)

`id_n_max_mt` · `0x46036` · 1 × 9 · rpm · **free** · risk medium

Stock: 6520 · allowed: 3500 to 7000

Engine speed where the limiter starts to act. One cell per detected gear: column 0 = no gear detected (standing, neutral), 1-6 = gears, 7 and 8 are unused.

**Recipe:** Higher limit: all 9 cells 6700. Same values in id_n_max_h_mt. Never above 7000.

Only active above 55 km/h plus 2 s. Below that, id_n_max_h_mt applies. Emulator: the limit follows the table value in each gear.

**Together with:** Always set to the same values as id_n_max_h_mt. Above 7000 rpm it collides with the over-rev counter c_n_lim_min (7200).

**Test:** Warm engine, standing, briefly hit the limiter. Read fault memory afterwards.

### Rev limit, manual (standing and up to 55 km/h)

`id_n_max_h_mt` · `0x46024` · 1 × 9 · rpm · **free** · risk medium

Stock: 6520 · allowed: 3500 to 7000

Second limit curve. Applies when standing and up to 55 km/h plus 2 s, then id_n_max_mt takes over. Stock: same as the main curve.

**Recipe:** Same values as id_n_max_mt. Standing limiter: column 0 = 4500 in both tables (test whether the ECU sees 'no gear' long enough when pulling away).

Emulator: changing only id_n_max_mt to 6700 still limits at 6520 below 55 km/h. Changing only this curve limits at 6520 again above 55 km/h.

**Together with:** Set to the same values as id_n_max_mt.

**Test:** Same as id_n_max_mt.

### Limiter I gain, manual

`id_fac_n_max_i_mt__gear` · `0x45EC8` · 1 × 9 · Nm/rpm · **caution** · risk medium

Stock: 0.00647 to 0.03503 · allowed: 0 to 0.2

Integral gain of the limiter torque controller per gear.

Same as the P gain.

**Together with:** See P gain.

**Test:** Log rpm at the limiter.

### Limiter P gain, manual

`id_fac_n_max_p_mt__gear` · `0x41A20` · 1 × 9 · Nm/rpm · **caution** · risk medium

Stock: 0.1562 to 0.2812 · allowed: 0 to 2

Proportional gain of the limiter torque controller per gear.

No measurable effect on bouncing in the model. In the car probably responsible for the soft approach to the limit.

**Together with:** Only change together with the I gain, and only after trying the hard cut threshold.

**Test:** Log rpm at the limiter.

### Limiter hardness (hard cut threshold)

`c_add_n_max_fcut` · `0x457D4` · constant · rpm · **caution** · risk medium

Stock: 50 · allowed: 0 to 100

How far the engine may go above the rev limit before the controller sets the torque request to 0.

**Recipe:** Stock 50. 30 = slightly harder, 15 = clearly harder, 10 = hard. Not below 10. Fault 28B1/28B2: back to 50.

Code 0x545A0: rpm > limit + value sets the request to 0 until rpm <= limit. This is the bounce width: smaller = faster, harder bouncing (d-d-d instead of a soft hum). Cylinder cut at 0 Nm is traced close to the injector output. Runs in the 10 ms task.

**Together with:** Works together with P/I gain and prediction time. Harder bouncing loads drivetrain and bearings more.

**Test:** Warm, standing, in steps 30, 15, 10. Below 15 there is little extra effect. Read fault memory after each step.

### Limiter prediction time, manual

`id_t_n_max_pred_mt__gear` · `0x41CAB` · 1 × 9 · s · **caution** · risk low

Stock: 0.03125 to 0.1875 · allowed: 0 to 0.3

The controller predicts rpm this far ahead and intervenes earlier.

**Recipe:** Hard cut step 3: set all cells to 0 together with threshold 10.

Code 0x544DC: used for the predicted rpm. 0 = intervene only at the real limit. Little effect on bounce frequency in the model.

**Together with:** Smaller makes the limiter entry more abrupt.

**Test:** Log rpm at the limiter.

### Duration of the second limit curve

`id_t_n_max_h_mt` · `0x41C99` · 1 × 9 · s · **read only** · risk low

Stock: 2

How long the second limit curve stays active. No effect as long as both curves are equal.

### Limiter torque return rate

`c_tqi_n_max_inc` · `0x45D76` · constant · Nm · **read only** · risk low

Stock: 5

Limits how fast the controller output rises again. Stock 5 Nm per 10 ms.

No effect on bouncing in the model, but a second review thinks it may affect the return. Therefore not released.

### Limp-home rev limit

`c_n_max_mtc_lih` · `0x45A92` · constant · rpm · **read only** · risk high

Stock: 1312

Limit used when a throttle or safety fault is detected. Do not change.

### Lower floor of the rev limit

`c_n_max_thd_min` · `0x45A94` · constant · rpm · **read only** · risk low

Stock: 1312

The effective limit never drops below this value (code 0xFFF91E2C).

### Oil temperature red zone (cluster)

`ip_n_max_2__toil` · `0x46CCA` · 1 × 4 · rpm · **read only** · risk low

Stock: 5600 to 6600

According to the A2L, the 'red band' limit depending on oil temperature. Not read by the limiter code, probably only used by the instrument cluster.

### Over-rev counter threshold

`c_n_lim_min` · `0x45A7C` · constant · rpm · **read only** · risk high

Stock: 7200

Above this speed the ECU counts an over-rev event (stock 7200). According to the MS4X wiki it closes the throttle and stores the event.

Do not change. Revving higher needs different valve springs/damper anyway.

### Ramp step from second to main limit

`id_n_dec_n_max_h_mt` · `0x45FCA` · 1 × 9 · rpm · **read only** · risk low

Stock: 10

Ramp from the second limit curve down to the main curve. No effect as long as both curves are equal.

### Speed threshold for the second limit curve

`c_vs_thd_n_max_h_mt` · `0x418FF` · constant · km/h · **read only** · risk low

Stock: 55

Vehicle speed where the switch between the two limit curves happens (stock 55 km/h).

### Switch: cylinder cut in limiter

`lc_inh_fcut_n_max` · `0x44A00` · constant · no unit · **read only** · risk high

Stock: 0

Logic switch in the cylinder cut path. Stock 0. Do not change.

### Switch: total fuel cut in limiter

`lc_ena_fcut_tot_n_max` · `0x449E8` · constant · no unit · **read only** · risk high

Stock: 0

Logic switch in the cylinder cut path. Stock 0. Effect not fully traced, do not change.

### Time window after speed threshold

`c_t_max_n_max_h_mt` · `0x4177C` · constant · s · **read only** · risk low

Stock: 2

Time window for the second (h_mt) limit curve.

## 02 Overrun and burbles

### Burble duration in gear, sport mode

`ip_t_min_pu_rng_l__n__tco` · `0x50AB0` · 8 × 6 · s · **caution** · risk medium

Stock: 0.2 to 0.41 · allowed: 0 to 2.5

In-gear delay used when the flag LV_RNG_L is set. The flag follows the sport mode switch and also switches the pedal map.

**Recipe:** Burbles only with sport button: put the in-gear recipe here and leave ip_t_min_pu__n__tco stock.

Emulator: with the flag set, this map is used instead of the normal one. That makes the sport button a burble switch in gear. Whether a car has the button and the ECU sees it must be tested.

**Together with:** Pedal feel also changes in sport mode. Standing always uses c_t_min_pu_vs, no switch there.

**Test:** Compare button on and off. Note the stock pedal feel first.

### Burble duration, in gear

`ip_t_min_pu__n__tco` · `0x50A50` · 8 × 6 · s · **caution** · risk medium

Stock: 0.22 to 0.47 · allowed: 0 to 2.5

How long the ECU keeps injecting after lifting off in gear, over rpm and coolant temperature.

**Recipe:** Only columns 60 and 90 C. Step 1: 1600 = 0.40, 2400 = 0.70, 3600 = 1.00, 4800 = 1.10, 6500 = 1.10. Step 2 (only after a clean step 1): 0.40 / 0.70 / 1.10 / 1.50 / 2.00. Above 1.2 s the torque monitor hold time runs out.

Emulator: fuel cut after this time if rpm stays above the threshold. The map is read with the current rpm, so the time gets shorter as rpm falls. While torque is not reduced, a floor of 1.21 s applies. Between 30 and 60 C it interpolates, so a change at 60 C already partly applies from 30 C.

**Together with:** Not used with the clutch pressed (c_t_min_pu applies there). The threshold ip_n_min_puc limits it from below. Sound needs later ignition (ip_iga_min_n_maf_pu).

**Test:** Warm, private ground, lift off from 2000, 3500, 5500 rpm. Less engine braking for the set time is normal.

### Burble duration, standing

`c_t_min_pu_vs` · `0x45C48` · constant · s · **caution** · risk medium

Stock: 0.18 · allowed: 0 to 1.5

Fuel cut delay when the car is standing or rolling below 6 km/h. One single value, any temperature.

**Recipe:** Stock 0.18. Step 1: 1.10. Step 2: 1.50 (only if fault memory stayed clean). Max 1.50.

Emulator: fuel cut after this time. With a short blip the revs drop below the cut-off threshold earlier, so it acts rpm-dependent as long as the value is longer than the fall time.

**Together with:** Takes priority over the clutch value and the in-gear map. Not temperature-dependent: also active when cold.

**Test:** Warm, standing, rev to 2500 and 4000 rpm and let go.

### Overrun cut-off threshold, A/C off

`ip_n_min_puc__tco__gr_mt` · `0x4B2FE` · 6 × 13 · rpm · **caution** · risk high

Stock: 992 to 1824 · allowed: 800 to 8160

Below this rpm the ECU keeps injecting on overrun. Rows coolant temperature, columns gear.

Emulator: 1216 rpm standing warm, 1184 rpm in 3rd, 1056 rpm in 5th. 8160 means never cut, i.e. continuous injection on every overrun.

**Together with:** Not suitable for short burbles. Leave stock for the time-based method.

**Test:** Only compare. Do not change without a reason.

### Overrun cut-off threshold, A/C on

`ip_n_accout_min_puc__tco__gr_mt` · `0x4B262` · 6 × 13 · rpm · **caution** · risk high

Stock: 1440 to 1760 · allowed: 800 to 8160

Same as the A/C-off threshold, but used while the A/C compressor runs. Below this rpm fuel is never cut on overrun.

**Recipe:** Experiment: rows 60 and 90 C, all columns 2400. Not higher. Leave the burble duration tables stock. Only works if the ECU actually sees 'compressor on'.

Emulator: 1440 rpm when warm. The time path is the same with A/C on and off, only the threshold changes. A value of 8160 means fuel is never cut: continuous injection on every overrun with A/C on (a common mistake in public 'pops and bangs' files).

**Together with:** Can be used as an A/C-button switch (experiment). Not for short burbles.

**Test:** Compare engine braking with A/C on and off below the new threshold.

### Overrun delay with clutch pressed

`c_t_min_pu` · `0x45C42` · constant · s · **caution** · risk medium

Stock: 0.1 · allowed: 0 to 0.5

Fuel cut delay while coasting with the clutch pressed, i.e. mostly while shifting. Stock 0.10 s.

Emulator: 0.11 s. More time means the revs hang longer when shifting. Leave stock for burbles.

**Together with:** Affects every gear change directly.

**Test:** Upshift under load, watch for rev hang.

### Max wait for torque reduction in gear

`c_t_max_pu` · `0x45C28` · constant · s · **read only** · risk medium

Stock: 1.2

While torque is not yet reduced, the ECU does not cut fuel in gear before this time (stock 1.20 s). This is a floor, not an upper limit for the delay map.

Emulator: without reduced torque the ECU cuts after 1.21 s, regardless of the map.

### Overrun cut-off hysteresis

`id_n_hys_max_puc__gr_mt` · `0x41B77` · 1 × 13 · rpm · **read only** · risk low

Stock: 480

Extra margin above the cut-off threshold. The active value changes: 480 right after a cut-off, then 96; after a cold start up to 5600. So shortly after a cut-off the threshold is higher.

### Overrun delay with clutch, sport mode

`c_t_min_pu_rng_l` · `0x45C46` · constant · s · **read only** · risk low

Stock: 1.2

Like c_t_min_pu, but when the flag LV_RNG_L is set, which follows the sport mode switch (code 0x57850, 0x5BEB4). Stock 1.20 s, so revs already hang longer when shifting in sport mode.

### Speed for 'car is moving'

`c_vs_min_run` · `0x418F1` · constant · km/h · **read only** · risk low

Stock: 6

Below this speed the standing value c_t_min_pu_vs applies (stock 6 km/h).

### Wait after drag torque control

`c_t_min_pu_msr` · `0x45C44` · constant · s · **read only** · risk low

Stock: 1

Minimum time after an engine drag torque control intervention (stock 1.00 s).

## 03 Ignition

### Base ignition RON 91

`ip_iga_bas_ron_91__n__maf` · `0x4AD24` · 20 × 16 · °CRK · **caution** · risk high

Stock: -16.5 to 42.38 · allowed: -35 to 60

Safety map for lower octane fuel.

Do not advance.

**Together with:** Partner of the RON 98 map.

**Test:** Only with knock logging.

### Base ignition RON 98

`ip_iga_bas_ron_98__n__maf` · `0x4AE64` · 20 × 16 · °CRK · **caution** · risk high

Stock: -13.5 to 42.38 · allowed: -35 to 60

Main ignition map in normal operation (RON 98).

Code 0x59200 and RomRaider 4560BN00 confirm the address. More advance only with knock logs.

**Together with:** Interpolated with the RON 91 map by knock control.

**Test:** Only with knock logging, one change at a time.

### Latest ignition on overrun (burble volume)

`ip_iga_min_n_maf_pu` · `0x4320E` · 8 × 6 · °CRK · **caution** · risk high

Stock: -24.38 to 16.5 · allowed: -35 to 30

Lower limit of the ignition angle while the overrun path is active. This is the lever for burble volume without touching the driving maps.

**Recipe:** Only the first two columns (76 and 98 mg/stroke), rows 2304-5792 rpm, at most 3 degrees less than stock. Example (col 76 / col 98): 2304 = -13.125 / -12.375, 2816 = -10.125 / -8.625, 3616 = -4.875 / -3.000, 4800 = 3.750 / 5.250, 5792 = 9.375 / 12.375.

Code 0x59884/0x59968: this map applies when the overrun cut-off condition is met. Not traced all the way to the ignition output whether ignition really goes down to this limit.

**Together with:** Later ignition with fuel heats exhaust and catalyst a lot. Small steps only, and only together with a short delay.

**Test:** Test 3 degrees later, never for long periods. Only when the time-based burbles alone are too quiet.

### Base ignition without VANOS

`ip_iga_bas__n__maf` · `0x4A964` · 20 × 16 · °CRK · **read only** · risk medium

Stock: -9 to 41.62

Used on a VANOS fault. Stays conservative.

### Ignition offset, max valve overlap

`ip_iga_bas_add_max_ivvt__n__maf` · `0x4AAA4` · 20 × 16 · °CRK · **read only** · risk medium

Stock: 0

Offset depending on valve overlap.

### Ignition offset, min valve overlap

`ip_iga_bas_add_min_ivvt__n__maf` · `0x4ABE4` · 20 × 16 · °CRK · **read only** · risk medium

Stock: 0

Offset depending on valve overlap.

### Latest ignition, normal

`ip_iga_min_n_maf` · `0x431AE` · 8 × 6 · °CRK · **read only** · risk high

Stock: -22.5 to 21

Lower limit outside the overrun path. Do not change.

## 04 VANOS

### VANOS exhaust setpoint 1

`ip_cam_sp_1_ex_pl__n__maf_ivvt` · `0x4A454` · 16 × 12 · °CRK · **read only** · risk high

Stock: -104.9 to -92.12

Exhaust cam target in part load. Only change with a healthy VANOS (no P0011/P0014 type faults).

### VANOS exhaust setpoint 2

`ip_cam_sp_2_ex_pl__n__maf_ivvt` · `0x4A5D4` · 16 × 12 · °CRK · **read only** · risk high

Stock: -104.9 to -81.62

Second exhaust table. Switching condition not known.

### VANOS intake setpoint 1

`ip_cam_sp_1_in_pl__n__maf_ivvt` · `0x4A514` · 16 × 12 · °CRK · **read only** · risk high

Stock: 92.25 to 119.2

Intake cam target in part load. Only change with a healthy VANOS (no P0011/P0014 type faults).

## 05 Idle

### Idle speed, A/C off

`ip_n_sp_is` · `0x46CE6` · 1 × 8 · rpm · **caution** · risk low

Stock: 660 to 1120 · allowed: 600 to 1400

Idle target over coolant temperature.

**Recipe:** Slightly higher cold idle: -30 = 1220, -20 = 1140, -10 = 1060, 10 = 940, rest stock. Never at or above the monitor limit.

Table selection confirmed in code. During catalyst heating ip_n_sp_ch can limit it; the end ramp is not emulated.

**Together with:** Change ip_acin_n_sp_is the same way. Must stay below the monitor ip_n_sp_is_mon_max_mon (ms45_check.py checks this).

**Test:** Watch a cold start, read idle target with INPA.

### Idle speed, A/C on

`ip_acin_n_sp_is` · `0x461EE` · 1 × 8 · rpm · **caution** · risk low

Stock: 660 to 1120 · allowed: 600 to 1400

Idle target over coolant temperature with A/C on.

**Recipe:** Same values as ip_n_sp_is.

See ip_n_sp_is.

**Together with:** Keep equal to ip_n_sp_is.

**Test:** Same as ip_n_sp_is.

### Idle target in part load

`ip_n_sp_is_pl` · `0x4F280` · 6 × 6 · rpm · **read only** · risk medium

Stock: 690 to 880

Target in part load. Wiki: raise together with the idle target.

### Max idle during catalyst heating

`ip_n_sp_ch` · `0x4F200` · 8 × 8 · rpm · **read only** · risk high

Stock: 660 to 1100

Limits idle in the first seconds after start. Part of catalyst heating, do not change.

### Pull-away assist, manual

`ip_n_sp_is_cs` · `0x46CF6` · 1 × 8 · rpm · **read only** · risk medium

Stock: 820 to 1120

According to the MS4X wiki the rpm target for the pull-away assist. 'cs' is the clutch switch path, not cold start.

## 06 Fuel and lambda

### Lambda full load

`ip_lamb_fl__n` · `0x46ADC` · 1 × 12 · no unit · **caution** · risk high

Stock: 0.8916 to 0.96 · allowed: 0.82 to 1.0

Lambda target at full load. Stock 0.89-0.96.

Address confirmed in code. Cannot be verified without a wideband sensor; the stock sensors are narrowband.

**Together with:** Richer at full load protects, leaner damages.

**Test:** Only with an external wideband sensor.

### Injector dead time

`ip_ti_add_dly` · `0x51330` · 8 × 6 · ms · **read only** · risk high

Stock: 0.04 to 3.628

Only relevant with different injectors.

### Lambda part load 1

`ip_lamb_bas_1` · `0x4E438` · 8 × 8 · no unit · **read only** · risk high

Stock: 1

Base lambda in part load. Part of the emissions strategy, do not change.

### Lambda part load 2

`ip_lamb_bas_2` · `0x4E4B8` · 8 × 8 · no unit · **read only** · risk high

Stock: 1

Base lambda in part load. Part of the emissions strategy, do not change.

## 07 Pedal, load, torque

### Max torque at the clutch

`id_tq_p_max_mt` · `0x46144` · 1 × 13 · Nm · **read only** · risk high

Stock: 999

Torque limit per gear. Do not touch.

### Pedal map (driver demand)

`ip_fac_tq_req_driv` · `0x4DC28` · 12 × 12 · no unit · **read only** · risk high

Stock: 0 to 1

The real pedal map: factor on requested torque over rpm and pedal. The monitor has copies (ip_fac_tq_req_driv_mon, _mon2). Changing it alone can trigger a monitoring fault.

Found, but not released: the _mon partner sits in the ROM test area and cannot simply be changed with it.

### Pedal map, sport mode

`ip_fac_tq_req_driv_rng_l` · `0x4DD48` · 12 × 12 · no unit · **read only** · risk high

Stock: 0 to 1

Second pedal map for the flag LV_RNG_L. Do not change.

### Pedal value for full-load detection

`ip_pv_max_fl__n` · `0x439EB` · 1 × 16 · % · **read only** · risk medium

Stock: 66.02

Above this pedal value (stock 66 %) full load enrichment applies. Not a pedal curve.

### Reference torque

`ip_tqi_ref__n__maf` · `0x52378` · 16 × 12 · Nm · **read only** · risk high

Stock: 10.47 to 330.4

Torque path. Do not touch.

### Target air mass from torque

`ip_maf_sp` · `0x4ED20` · 16 × 12 · mg/stroke · **read only** · risk high

Stock: 47.92 to 563.4

Torque path. Do not touch.

## 08 DISA

### DISA load threshold

`c_fac_maf_max_vim` · `0x458E8` · constant · no unit · **read only** · risk medium

Stock: 0.7

Load threshold of the intake manifold flap.

### DISA lower rpm threshold

`c_n_vim_l` · `0x45AC6` · constant · rpm · **read only** · risk medium

Stock: 2200

Switching zone of the intake manifold flap. Wiki: must match the intake model.

### DISA upper rpm threshold

`c_n_vim_h` · `0x45AC2` · constant · rpm · **read only** · risk medium

Stock: 4100

Switching zone of the intake manifold flap. Wiki: must match the intake model.

## 09 Cooling and fan

### Electric fan stage

`ip_n_ecf` · `0x438ED` · 1 × 6 · no unit · **read only** · risk medium

Stock: 0 to 15

Stage of the electric fan. View only.

### Target coolant temperature, A/C off

`id_tco_sp_ect` · `0x4A364` · 12 × 6 · °C · **read only** · risk medium

Stock: 87 to 102

Map thermostat target. View only.

### Target coolant temperature, A/C on

`id_tco_sp_ect_acin` · `0x4A3AC` · 12 × 6 · °C · **read only** · risk medium

Stock: 80.25 to 102

Map thermostat target with A/C on. View only.

## 10 Top speed

### Top speed limiter

`c_vs_max` · `0x418D4` · constant · km/h · **caution** · risk high

Stock: 235 · allowed: 100 to 255

Speed limiter (stock 235 km/h). Wiki: 255 removes it.

**Recipe:** Only up to your tyre speed rating.

Code 0xFFF91CB8 and RomRaider confirm the address. Little practical use, a 520i hardly reaches 235 km/h.

**Together with:** Respect the tyre speed rating and the chassis.

**Test:** Do not test if the tyre speed rating does not allow it.

## 11 Cold start and warm-up

### Warm-up fuel factor

`ip_fac_ti_tco_wup` · `0x42A08` · 1 × 8 · no unit · **caution** · risk medium

Stock: 1 · allowed: 0 to 2

Extra fuel during warm-up. Wiki: for rough running in the first 30 seconds.

Address confirmed in code, effect not emulated.

**Together with:** Affects cold start emissions.

**Test:** Only for a real problem. Log the cold start.

### Cranking fuel

`ip_mff_cst` · `0x46BE4` · 3 × 8 · mg/stroke · **read only** · risk medium

Stock: 19.2 to 310.3

Base value of the cranking fuel mass. Only relevant for E85 or starting problems.

## 12 Monitoring (do not change)

### Monitor: max idle speed

`ip_n_sp_is_mon_max_mon` · `0x404D0` · 1 × 5 · rpm · **read only** · risk high

Stock: 1024 to 1408

Upper limit of the torque monitor for the idle target. Inside the ROM test area, a change is detected. Idle must stay below it.

### Monitor: reference torque

`ip_tqi_ref_mon` · `0x40539` · 6 × 8 · Nm · **read only** · risk high

Stock: 18 to 328

Inside the ROM test area of the monitor. Any change breaks the checksum test.

### ROM test switch

`val_mo3_swi_cal_cks` · `0x45788` · constant · no unit · **read only** · risk high

Stock: 0

Turns off the reaction to the checksum test. Do not change, it is a safety function.

### ROM test target sum (high)

`val_mo3_cal_cks_high` · `0x457AC` · constant · no unit · **read only** · risk high

Stock: 1.909e+07

Target value of the checksum over 0x40240-0x407C7. Recalculated, matches the file.

### ROM test target sum (low)

`val_mo3_cal_cks_low` · `0x457B0` · constant · no unit · **read only** · risk high

Stock: 4.247e+09

Target value of the checksum over 0x40240-0x407C7. Recalculated, matches the file.
