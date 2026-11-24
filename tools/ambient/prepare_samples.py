#!/usr/bin/env python3
"""Prepare WAV samples for 86Box's drive/ambient sound engines.

86Box's loader (sound_load_wav() in src/sound/sound_util.c) only accepts
16-bit PCM, mono or stereo, with the plain 44-byte WAV header: a 16-byte
"fmt " chunk followed directly by "data". It does not resample, so every
file must already be 48 kHz.

For each input file this script:
  1. converts it to 16-bit PCM at 48 kHz with SoX, keeping the channel count
     (resampling uses SoX's very-high-quality "rate -v" only when needed);
  2. optionally trims leading/trailing silence and peak-normalizes
     (--trim-db, --normalize-db; both off by default);
  3. for --loop files, reports the loop seam and optionally crossfades it
     (--crossfade-ms);
  4. writes the result with Python's wave module, which always produces the
     plain 44-byte header, and checks that it did.

Needs: Python 3.8+, numpy, and the `sox` command-line tool.
Run it in isolated mode so it can't import code from the sample folders:

    python3 -I tools/ambient/prepare_samples.py -o OUTDIR in1.wav in2.wav
    python3 -I tools/ambient/prepare_samples.py --loop -o OUTDIR loop.wav
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np

RATE = 48000
SEAM_MS = 10.0


def sox_convert(src, dst):
    """Convert src to 16-bit signed PCM WAV at RATE Hz, same channels."""
    info = subprocess.run(["sox", "--i", "-r", src], check=True,
                          capture_output=True, text=True)
    src_rate = int(float(info.stdout.strip()))
    cmd = ["sox", src, "-t", "wav", "-e", "signed-integer", "-b", "16", dst]
    if src_rate != RATE:
        cmd += ["rate", "-v", str(RATE)]
    subprocess.run(cmd, check=True, capture_output=True)
    return src_rate


def read_wav(path):
    with wave.open(path, "rb") as w:
        if w.getsampwidth() != 2:
            raise ValueError(f"{path}: expected 16-bit after conversion")
        ch = w.getnchannels()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
    return data.reshape(-1, ch).astype(np.float64), ch


def write_wav(path, frames, ch):
    pcm = np.clip(np.round(frames), -32768, 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    with open(path, "rb") as f:
        hdr = f.read(44)
    # Same checks as sound_load_wav(): RIFF/WAVE, 16-byte fmt, then data.
    if (hdr[0:4] != b"RIFF" or hdr[8:12] != b"WAVE" or hdr[12:16] != b"fmt "
            or int.from_bytes(hdr[16:20], "little") != 16
            or hdr[36:40] != b"data"):
        raise RuntimeError(f"{path}: header is not the plain 44-byte form")


def dbfs(x):
    return 20 * np.log10(max(x, 1e-9) / 32768.0)


def trim_silence(frames, thresh_db):
    level = 32768.0 * 10 ** (thresh_db / 20)
    loud = np.nonzero(np.max(np.abs(frames), axis=1) > level)[0]
    if loud.size == 0:
        return frames
    return frames[loud[0]:loud[-1] + 1]


def normalize(frames, peak_db):
    peak = np.max(np.abs(frames))
    if peak == 0:
        return frames
    return frames * (32767.0 * 10 ** (peak_db / 20) / peak)


def seam_report(frames):
    """Describe how smoothly the end of a loop runs into its start.

    jump:  sample step from the last frame to the first, per channel (max).
    typ:   99th percentile of ordinary sample-to-sample steps in the file.
    ratio: jump / typ. Above ~1 the seam is a bigger step than the signal
           normally makes, which is what you hear as a click.
    rms_diff_db: loudness difference between the last and first 10 ms, a
           sign the loop will "pump" each lap even without a click.
    """
    n = int(RATE * SEAM_MS / 1000)
    jump = float(np.max(np.abs(frames[0] - frames[-1])))
    steps = np.abs(np.diff(frames, axis=0))
    typ = float(np.percentile(steps, 99)) or 1.0
    rms = lambda a: float(np.sqrt(np.mean(a ** 2)))
    return {
        "jump": jump,
        "typ": typ,
        "ratio": jump / typ,
        "rms_diff_db": dbfs(rms(frames[-n:])) - dbfs(rms(frames[:n])),
    }


def crossfade_loop(frames, ms):
    """Equal-power crossfade of the loop's tail into its head.

    The result is n frames shorter. Its first n frames blend the original
    tail (fading out) with the original head (fading in), so playback runs
    ...tail end -> blended start... with no jump at the wrap point.
    """
    n = int(RATE * ms / 1000)
    if n * 2 >= len(frames):
        raise ValueError("crossfade is longer than half the loop")
    t = (np.arange(n) / n)[:, None]
    fade_in, fade_out = np.sin(t * np.pi / 2), np.cos(t * np.pi / 2)
    out = frames[:-n].copy()
    out[:n] = frames[:n] * fade_in + frames[-n:] * fade_out
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("inputs", nargs="+", help="input WAV files")
    ap.add_argument("-o", "--outdir", required=True)
    ap.add_argument("--trim-db", type=float, metavar="DB",
                    help="trim leading/trailing audio below DB dBFS")
    ap.add_argument("--normalize-db", type=float, metavar="DB",
                    help="scale so the peak is DB dBFS (e.g. -1)")
    ap.add_argument("--loop", action="store_true",
                    help="inputs are loops: report the seam")
    ap.add_argument("--crossfade-ms", type=float, metavar="MS",
                    help="with --loop: crossfade the seam (20-50 ms)")
    args = ap.parse_args()

    if shutil.which("sox") is None:
        sys.exit("prepare_samples: the `sox` command is required")
    if args.crossfade_ms and not args.loop:
        sys.exit("prepare_samples: --crossfade-ms only makes sense with --loop")
    os.makedirs(args.outdir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        for src in args.inputs:
            name = os.path.basename(src)
            conv = os.path.join(tmp, name)
            src_rate = sox_convert(src, conv)
            frames, ch = read_wav(conv)
            notes = [f"{src_rate} Hz -> {RATE} Hz" if src_rate != RATE
                     else f"{RATE} Hz", "stereo" if ch == 2 else "mono"]

            if args.trim_db is not None:
                before = len(frames)
                frames = trim_silence(frames, args.trim_db)
                notes.append(f"trimmed {before - len(frames)} frames")
            if args.normalize_db is not None:
                frames = normalize(frames, args.normalize_db)
                notes.append(f"peak -> {args.normalize_db} dBFS")

            if args.loop:
                s = seam_report(frames)
                notes.append("seam jump {jump:.0f} (typ {typ:.0f}, ratio "
                             "{ratio:.2f}), end-vs-start RMS "
                             "{rms_diff_db:+.1f} dB".format(**s))
                if args.crossfade_ms:
                    frames = crossfade_loop(frames, args.crossfade_ms)
                    s = seam_report(frames)
                    notes.append(f"CROSSFADED {args.crossfade_ms:g} ms -> "
                                 "ratio {ratio:.2f}, RMS {rms_diff_db:+.1f} "
                                 "dB".format(**s))

            peak = float(np.max(np.abs(frames)))
            rms = float(np.sqrt(np.mean(frames ** 2)))
            notes.append(f"{len(frames) / RATE:.2f} s, peak {dbfs(peak):.1f} "
                         f"dBFS, RMS {dbfs(rms):.1f} dBFS")
            write_wav(os.path.join(args.outdir, name), frames, ch)
            print(f"{name}: " + "; ".join(notes))


if __name__ == "__main__":
    main()
