# How the limiter and the overrun fuel cut work

Background for [Sound and feel](sound.md). Addresses are 1 MB flash addresses or MPC code addresses.

## Rev limiter

The limiter code (MPC around `0x543E4`) works in three stages:

1. **Limit.** Up to 55 km/h and for 2 s after that, the limit comes from `id_n_max_h_mt`. Above that, it comes from `id_n_max_mt`. Both have one cell per detected gear.
2. **Soft control.** A P/I controller with prediction reduces torque as soon as the *predicted* rpm is above the limit (`id_fac_n_max_p_mt__gear`, `id_fac_n_max_i_mt__gear`, `id_t_n_max_pred_mt__gear`).
3. **Hard cut.** If the rpm is above **limit + `c_add_n_max_fcut`** (stock 6520 + 50), the controller sets its torque request to 0 until the rpm has fallen back to the limit. At 0 Nm the ECU cuts fuel on all six cylinders.

Stage 3 is the lever for the hard cut feel. The MS43 has the same trick with `c_n_max_hys`. In the emulator model the P/I gains and the prediction had almost no effect, the threshold had a strong one. The model uses the original controller code, but the engine is only a simple inertia model. It shows the direction, not the sound.

There are two kinds of hard cut:

- **Fuel cut** (this one): no unburnt fuel in the exhaust, a dry "d-d-d".
- **Ignition cut** (launch control, no-lift-shift): unburnt fuel ignites in the exhaust and bangs. This software has no parameter for it.

Risks: the ECU monitors rev limiting (`tqi_n_max_mon`). The stock limiter does not trigger it, but a public report from the MS45.1 mentions ECU restarts after a program patch that lowered the limit a lot. So go in small steps and read the fault memory after each one.

## Overrun fuel cut (burbles)

The overrun state machine (MPC `0x33D10`) runs every 10 ms:

1. Lifting off sets the overrun state. A counter starts at 0.
2. During overrun the ECU still injects. It only cuts fuel when **all** of these are true:
   - rpm above the cut-off threshold plus hysteresis (`ip_n_min_puc__tco__gr_mt`, with A/C `ip_n_accout_min_puc__tco__gr_mt`)
   - counter above the delay
   - in gear: torque has been reduced, **or** the counter has passed `c_t_max_pu` (1.20 s)
3. The delay depends on the situation:
   - below 6 km/h: `c_t_min_pu_vs`
   - clutch pressed: `c_t_min_pu` (sport mode: `c_t_min_pu_rng_l`)
   - otherwise the map `ip_t_min_pu__n__tco` (sport mode: `ip_t_min_pu_rng_l__n__tco`)
4. The A/C only changes the threshold. The time path is the same with A/C on and off.

The time unit is 0.01 s. Details that matter in practice:

- The in-gear map is read with the **current** rpm. As rpm falls, the time gets shorter. Example: 3600 rpm falling at 800 rpm/s gives 0.88 s instead of 1.10 s.
- If torque is reduced more slowly than assumed (0.4 s in the model), the floor of 1.21 s applies at all rpm. That is the most important thing to watch in a first test.
- The cut-off threshold is not fixed. Right after a cut-off it is 480 rpm higher for a while, then 96 rpm.
- When the overrun ends, the counter resets. No lasting effect was found.

**Two methods.** The time method (levels 1-2 in [Sound](sound.md)) delays the fuel cut by a set time, then the ECU cuts fuel normally. The threshold method ([level 3](sound.md#level-3-extreme-pops-bangs-and-flames)) raises the cut-off threshold, often to 255 raw (8160 rpm). Then the rpm is never above the threshold, and fuel is never cut: in the emulator more than 5 s of injection down to idle on one lift-off, instead of 1-2 s.

**Sound.** The time until fuel cut is proven, the sound is not. The overrun ignition limit `ip_iga_min_n_maf_pu` applies during the waiting time. At light load it is around -10° at 2300 rpm but +7° at 4800 and +12° at 5800. So at high rpm it injects longest but with the earliest ignition: longer, but probably quieter.

**Torque monitor.** After lifting off, the monitor allows the torque for 1.2 s (`c_t_tqi_mon` = 30 × 0.04 s), the same as `c_t_max_pu`. What happens if injection continues after that is not known. That is why step 1 of the burble recipe stays below 1.2 s.

**Catalyst.** More fuel with late ignition heats the exhaust and the catalyst. 1-2 s per lift-off in normal driving is very different from continuous injection. Repeated revving while standing and long downhill runs are not. No temperature limit could be proven.

## Pedal map and monitoring

The torque tables and the monitoring are read-only in the standard XDF. The pedal map `ip_fac_tq_req_driv` has a copy in the monitor (`ip_fac_tq_req_driv_mon`) inside the ROM test area. Changing one without the other triggers a monitoring fault. Catalyst, lambda and OBD diagnostics are not part of the parameter data.
