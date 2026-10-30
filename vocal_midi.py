#!/usr/bin/env python3
"""Create a vocal-free backing track from a local song.

Install:
    python -m pip install demucs

Usage:
    python vocal_midi.py "song.mp3"
    python vocal_midi.py "song.wav" --outdir "./vocal_output"

Outputs: vocal_output/htdemucs/<song name>/no_vocals.wav and vocals.wav.
This creates audio, not MIDI. Demucs separates ALL vocals together; it cannot
remove only the lead singer while reliably preserving backing vocals.
Some vocals may remain and some instruments may be affected.
The first run downloads the model. MP3 input may require FFmpeg on your PATH.
"""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path


def remove_vocals(input_path: Path, outdir: Path) -> Path:
    """Separate vocals from accompaniment and return the backing track."""
    print(f"Removing vocals from: {input_path.name}", flush=True)
    print("Note: backing vocals may also be removed.", flush=True)
    cmd = [
        sys.executable, "-m", "demucs",
        "-n", "htdemucs",
        "--two-stems", "vocals",
        "-o", str(outdir),
        str(input_path),
    ]
    subprocess.run(cmd, check=True)

    track_dir = outdir / "htdemucs" / input_path.stem
    backing_track = track_dir / "no_vocals.wav"
    if not backing_track.is_file():
        raise FileNotFoundError(f"Expected backing track not found: {backing_track}")

    print(f"\nBacking track: {backing_track}")
    print(f"Isolated vocals reference: {track_dir / 'vocals.wav'}")
    return backing_track


def main():
    parser = argparse.ArgumentParser(
        description="Remove vocals for practice (includes backing vocals, not just lead)."
    )
    parser.add_argument("input_file", help="Path to your local audio file")
    parser.add_argument("--outdir", default="./vocal_output", help="Output directory")
    args = parser.parse_args()

    input_path = Path(args.input_file).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()
    if not input_path.is_file():
        parser.error(f"Audio file not found: {input_path}")
    if importlib.util.find_spec("demucs") is None:
        parser.exit(1, "Install Demucs first: python -m pip install demucs\n")

    try:
        outdir.mkdir(parents=True, exist_ok=True)
        remove_vocals(input_path, outdir)
    except subprocess.CalledProcessError as error:
        parser.exit(1, f"Demucs failed (exit code {error.returncode}). See its output above.\n")
    except OSError as error:
        parser.exit(1, f"Error: {error}\n")

    print("\nDone! Play no_vocals.wav to practice along with the music.")


if __name__ == "__main__":
    main()
