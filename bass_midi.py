#!/usr/bin/env python3
"""Remove bass from a local song so you can practice playing along.

Install:
    python -m pip install demucs

Usage:
    python bass_midi.py "C:\\Music\\song.mp3"
    python bass_midi.py "song.wav" --outdir "./bass_output"

Outputs:
    bass_output/htdemucs/<song name>/no_bass.wav  (practice backing track)
    bass_output/htdemucs/<song name>/bass.wav     (isolated bass reference)

Despite the filename, this creates audio, not MIDI. No basic-pitch is needed.
Demucs downloads its model on first use. Separation can leave some artifacts
or residual bass. MP3 input may require FFmpeg installed and on your PATH.
"""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path


def remove_bass(input_path: Path, outdir: Path) -> Path:
    """Separate bass from everything else and return the practice track."""
    print(f"Removing bass from: {input_path.name}", flush=True)
    cmd = [
        sys.executable, "-m", "demucs",
        "-n", "htdemucs",
        "--two-stems", "bass",
        "-o", str(outdir),
        str(input_path),
    ]
    subprocess.run(cmd, check=True)

    # Use the explicit model name instead of guessing the output directory.
    track_dir = outdir / "htdemucs" / input_path.stem
    backing_track = track_dir / "no_bass.wav"
    if not backing_track.is_file():
        raise FileNotFoundError(f"Expected backing track not found: {backing_track}")

    print(f"\nPractice backing track: {backing_track}")
    print(f"Isolated bass reference: {track_dir / 'bass.wav'}")
    return backing_track


def main():
    parser = argparse.ArgumentParser(
        description="Remove bass from a song to create a bass practice backing track."
    )
    parser.add_argument("input_file", help="Path to your local audio file")
    parser.add_argument("--outdir", default="./bass_output", help="Output directory")
    args = parser.parse_args()

    input_path = Path(args.input_file).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()
    if not input_path.is_file():
        parser.error(f"Audio file not found: {input_path}")
    if importlib.util.find_spec("demucs") is None:
        parser.exit(1, "Install Demucs first: python -m pip install demucs\n")

    try:
        outdir.mkdir(parents=True, exist_ok=True)
        remove_bass(input_path, outdir)
    except subprocess.CalledProcessError as error:
        parser.exit(1, f"Demucs failed (exit code {error.returncode}). See its output above.\n")
    except OSError as error:
        parser.exit(1, f"Error: {error}\n")

    print("\nDone! Play no_bass.wav and practice your bass part along with it.")


if __name__ == "__main__":
    main()
