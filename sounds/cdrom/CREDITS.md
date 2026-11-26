# CD-ROM drive sound credits

## Generic ATAPI (IBMulator)

- **Files:** everything in `Generic ATAPI (IBMulator)/`
- **Source:** IBMulator, <https://github.com/barotto/IBMulator>,
  `share/ibmulator/sounds/cdrom/`, as of upstream commit `ec51e54`
  (2026-02-04). IBMulator emulates a generic ATAPI CD-ROM drive; the
  recordings aren't tied to a named model.
- **Author:** Marco Bortolin (IBMulator's sole listed author). The sound
  folder carries no separate credit, so these are attributed to the project.
- **License:** GNU GPL version 3 or later, the license of the IBMulator
  repository. The full text is in `Generic ATAPI (IBMulator)/COPYING.GPL-3.0`,
  copied from IBMulator's `COPYING`.

| File here | IBMulator original | Changes |
|---|---|---|
| `GENERIC_ATAPI_SPIN_START.wav` | `spin_start.wav` | renamed only (samples bit-identical) |
| `GENERIC_ATAPI_SPIN.wav` | `spin.wav` | 20 ms equal-power crossfade at the loop seam (it clicked slightly), so the file is 20 ms shorter |
| `GENERIC_ATAPI_SPIN_STOP.wav` | `spin_stop.wav` | renamed only |
| `GENERIC_ATAPI_SEEK_STEP.wav` | `seek_step.wav` | renamed only |
| `GENERIC_ATAPI_SEEK_IN.wav` | `seek_in.wav` | renamed only |
| `GENERIC_ATAPI_SEEK_OUT.wav` | `seek_out.wav` | renamed only |
| `GENERIC_ATAPI_OPEN_TRAY.wav` | `open_tray.wav` | renamed only (mono, as the original) |
| `GENERIC_ATAPI_CLOSE_TRAY.wav` | `close_tray.wav` | renamed only (mono, as the original) |

All were written by `tools/ambient/prepare_samples.py`. Seek volumes are 0.8
in the profile, matching IBMulator's default balance of seek against spin
noise (80 vs 100).
