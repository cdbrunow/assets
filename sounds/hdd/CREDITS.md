# HDD sound credits

This file only covers profiles added by the ambient-sounds work. The
profiles that were already here came without attribution notes.

## 1990 IBM WDL-330P

- **Files:** everything in `1990 IBM WDL-330P/`
- **Source:** IBMulator, <https://github.com/barotto/IBMulator>,
  `share/ibmulator/sounds/hdd/`, as of upstream commit `ec51e54`
  (2026-02-04). The drive is the 30 MB IBM WDL-330P from the IBM PS/1
  model 2011.
- **Author:** Marco Bortolin (IBMulator's sole listed author). The sound
  folder carries no separate credit, so these are attributed to the project.
- **License:** GNU GPL version 3 or later, the license of the IBMulator
  repository. The full text is in `1990 IBM WDL-330P/COPYING.GPL-3.0`,
  copied from IBMulator's `COPYING`.

| File here | IBMulator original | Changes |
|---|---|---|
| `1990_IBM_WDL-330P_3600RPM_SPINUP.wav` | `drive_spin_up.wav` | renamed only (samples bit-identical) |
| `1990_IBM_WDL-330P_3600RPM_RUNNING.wav` | `drive_spin.wav` | 30 ms equal-power crossfade at the loop seam, so the file is 30 ms shorter |
| `1990_IBM_WDL-330P_3600RPM_SPINDOWN.wav` | `drive_spin_down.wav` | renamed only (samples bit-identical) |
| `1990_IBM_WDL-330P_3600RPM_SEEK_1TRACK.wav` | `drive_seek.wav` | renamed only (samples bit-identical) |

All four were written by `tools/ambient/prepare_samples.py`, which also
rewrites each file with the plain 44-byte WAV header 86Box's loader
requires. IBMulator's `drive_seek_long.wav` isn't used, because 86Box HDD
profiles have only one seek sound.
