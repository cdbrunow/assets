# System fan / power supply sound credits

## IBM PS1 2121

- **Files:** everything in `IBM PS1 2121/`
- **Source:** IBMulator, <https://github.com/barotto/IBMulator>,
  `share/ibmulator/sounds/system/`, as of upstream commit `ec51e54`
  (2026-02-04). These are the system unit's power supply fan sounds as
  IBMulator plays them for the IBM PS/1.
- **Author:** Marco Bortolin (IBMulator's sole listed author). The sound
  folder carries no separate credit, so these are attributed to the project.
- **License:** GNU GPL version 3 or later, the license of the IBMulator
  repository. The full text is in `IBM PS1 2121/COPYING.GPL-3.0`, copied
  from IBMulator's `COPYING`.

| File here | IBMulator original | Changes |
|---|---|---|
| `IBM_PS1_2121_POWER_UP.wav` | `power_up.wav` | renamed only (samples bit-identical) |
| `IBM_PS1_2121_POWER_ON.wav` | `power_on.wav` | 30 ms equal-power crossfade at the loop seam, so the file is 30 ms shorter |
| `IBM_PS1_2121_POWER_DOWN.wav` | `power_down.wav` | header rewritten; first 350 ms capped at -41.7 dBFS (4 dB above the running fan) to soften the switch click; the rest unchanged |

All three were written by `tools/ambient/prepare_samples.py`. The original
`power_down.wav` has an 18-byte `fmt ` chunk, which 86Box's WAV loader
rejects; the script writes the plain 44-byte header it expects.
