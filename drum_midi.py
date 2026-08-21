#!/usr/bin/env python3
"""
drums_to_midi.py

Pipeline:
  1. Take a LOCAL audio file you already have the rights to use
     (your own mix, a purchased/licensed track, a royalty-free sample, etc.)
  2. Separate it into stems with Demucs and keep only the drum stem
  3. Convert the isolated drum audio into a MIDI file with basic-pitch

Install deps first:
    pip install demucs basic-pitch --break-system-packages

Usage:
    python drums_to_midi.py /path/to/song.wav
    python drums_to_midi.py /path/to/song.mp3 --outdir ./drum_output

Notes:
  - Demucs works best on wav/mp3/flac.
  - Drum-specific audio-to-MIDI is inherently approximate — expect to need
    manual cleanup afterward in your DAW (velocities, ghost notes, hi-hat
    vs cymbal choices are the usual trouble spots).
  - This script only processes files already on your disk. It does not
    download anything from the internet.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def separate_drums(input_path: Path, outdir: Path) -> Path:
    """Run Demucs source separation and return the path to the drums stem."""
    print(f"[1/2] Separating stems with Demucs for: {input_path.name}")
    cmd = [
        sys.executable, "-m", "demucs",
        "--two-stems", "drums",   # isolates drums vs "everything else"
        "-o", str(outdir),
        str(input_path),
    ]
    subprocess.run(cmd, check=True)

    # Demucs writes to: <outdir>/<model_name>/<track_name>/drums.wav
    model_dirs = list(outdir.glob("*"))
    if not model_dirs:
        raise RuntimeError("Demucs did not produce output.")
    track_name = input_path.stem
    drums_path = model_dirs[0] / track_name / "drums.wav"
    if not drums_path.exists():
        raise FileNotFoundError(f"Expected drum stem not found at {drums_path}")
    print(f"    -> Drum stem saved to: {drums_path}")
    return drums_path


def drums_to_midi(drums_path: Path, outdir: Path) -> Path:
    """Convert the isolated drum audio into a MIDI file using basic-pitch."""
    print(f"[2/2] Converting drum audio to MIDI with basic-pitch")
    cmd = [
        sys.executable, "-m", "basic_pitch",
        str(outdir),
        str(drums_path),
    ]
    subprocess.run(cmd, check=True)

    midi_path = outdir / f"{drums_path.stem}_basic_pitch.mid"
    if midi_path.exists():
        print(f"    -> MIDI file saved to: {midi_path}")
    else:
        print("    -> Check the output directory; basic-pitch names files "
              "based on its own convention.")
    return midi_path


def main():
    parser = argparse.ArgumentParser(description="Isolate drums and convert to MIDI.")
    parser.add_argument("input_file", type=str, help="Path to a local audio file you have rights to use")
    parser.add_argument("--outdir", type=str, default="./drum_output", help="Output directory")
    args = parser.parse_args()

    input_path = Path(args.input_file).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"Error: file not found: {input_path}")
        sys.exit(1)

    drums_path = separate_drums(input_path, outdir)
    drums_to_midi(drums_path, outdir)

    print("\nDone. Recommended next step: open the MIDI file in your DAW "
          "(Ableton, Logic, FL Studio, Reaper, etc.) and clean up velocities "
          "and note placement by ear.")


if __name__ == "__main__":
    main()