#!/usr/bin/env python3
"""Remove piano from a song to make a piano practice backing track.

Install:
    python -m pip install demucs

Usage:
    python piano_midi.py "song.mp3"
    python piano_midi.py "song.wav" --outdir "./piano_output"

Outputs under piano_output/htdemucs_6s/<song name>/:
    no_piano.wav - backing track for practicing piano
    piano.wav    - isolated piano reference

This creates audio, not MIDI. The first run downloads the separation model.
Piano separation is experimental: some piano may remain, and other instruments
may be affected. MP3 input may require FFmpeg installed and on your PATH.
"""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path


def remove_piano(input_path: Path, outdir: Path) -> Path:
    """Separate piano from everything else and return the backing track."""
    print(f"Removing piano from: {input_path.name}", flush=True)
    cmd = [
        sys.executable, "-m", "demucs",
        "-n", "htdemucs_6s",  # Six-source model includes piano.
        "--two-stems", "piano",
        "-o", str(outdir),
        str(input_path),
    ]
    subprocess.run(cmd, check=True)

    track_dir = outdir / "htdemucs_6s" / input_path.stem
    backing_track = track_dir / "no_piano.wav"
    if not backing_track.is_file():
        raise FileNotFoundError(f"Expected backing track not found: {backing_track}")

    print(f"\nPractice backing track: {backing_track}")
    print(f"Isolated piano reference: {track_dir / 'piano.wav'}")
    return backing_track


def main():
    parser = argparse.ArgumentParser(
        description="Remove piano from a song to create a piano practice backing track."
    )
    parser.add_argument("input_file", help="Path to your local audio file")
    parser.add_argument("--outdir", default="./piano_output", help="Output directory")
    args = parser.parse_args()

    input_path = Path(args.input_file).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()
    if not input_path.is_file():
        parser.error(f"Audio file not found: {input_path}")
    if importlib.util.find_spec("demucs") is None:
        parser.exit(1, "Install Demucs first: python -m pip install demucs\n")

    try:
        outdir.mkdir(parents=True, exist_ok=True)
        remove_piano(input_path, outdir)
    except subprocess.CalledProcessError as error:
        parser.exit(1, f"Demucs failed (exit code {error.returncode}). See its output above.\n")
    except OSError as error:
        parser.exit(1, f"Error: {error}\n")

    print("\nDone! Play no_piano.wav and practice your piano part along with it.")


if __name__ == "__main__":
    main()
