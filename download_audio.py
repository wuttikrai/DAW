"""Download YouTube audio from CMD using yt-dlp and FFmpeg."""

import argparse
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.parse import urlsplit


def youtube_url(value):
    value = value.strip().strip('"').strip("'")
    try:
        parsed = urlsplit(value)
        host = (parsed.hostname or "").lower()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Invalid URL.") from exc
    if parsed.scheme not in ("https", "http") or not (
        host in ("youtu.be", "youtube.com") or host.endswith(".youtube.com")
    ):
        raise argparse.ArgumentTypeError("Enter a full YouTube URL starting with https://.")
    return value


def main():
    parser = argparse.ArgumentParser(
        description="Download the best available YouTube audio. Omit URL to paste it at a prompt."
    )
    parser.add_argument("url", nargs="?", type=youtube_url)
    parser.add_argument("-o", "--output", type=Path, default=Path("downloads"),
                        help="Destination folder (default: downloads in the current folder)")
    parser.add_argument("--mp3", action="store_true", help="Convert to MP3 at 320 kbps")
    args = parser.parse_args()

    if args.url is None:
        try:
            args.url = youtube_url(input("Paste YouTube URL: "))
        except argparse.ArgumentTypeError as exc:
            parser.error(str(exc))
        except EOFError:
            parser.error("No URL entered. Pass a URL as an argument or run interactively.")

    if importlib.util.find_spec("yt_dlp") is None:
        print('Install the dependency: python -m pip install -U "yt-dlp[default]"', file=sys.stderr)
        return 1
    missing = [name for name in ("ffmpeg", "ffprobe") if not shutil.which(name)]
    if missing:
        print("Missing " + ", ".join(missing) + ". Install FFmpeg and add its bin folder to PATH.", file=sys.stderr)
        return 1
    runtime = next((name for name in ("deno", "node") if shutil.which(name)), None)
    if runtime is None:
        print("Install Deno (recommended) or Node.js and add it to PATH for YouTube support.", file=sys.stderr)
        return 1

    output = args.output.expanduser().resolve()
    try:
        output.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"Cannot create output folder: {exc}", file=sys.stderr)
        return 1

    command = [
        sys.executable, "-m", "yt_dlp",
        "--ignore-config", "--no-playlist", "--no-overwrites",
        "--windows-filenames", "--trim-filenames", "180",
        "--js-runtimes", runtime,
        "--format", "bestaudio/best", "--extract-audio",
        "--audio-format", "mp3" if args.mp3 else "best",
        "--paths", str(output),
        "--output", "%(title)s [%(id)s].%(ext)s",
        "--print", "after_move:filepath", "--no-simulate", "--progress",
    ]
    if args.mp3:
        command.extend(["--audio-quality", "320K"])
    command.extend(["--", args.url])
    print(f"Saving audio in: {output}", flush=True)
    # Pass arguments directly; URL text is never executed by CMD.
    result = subprocess.run(command, check=False)
    if result.returncode:
        print('Download failed. Try updating: python -m pip install -U "yt-dlp[default]"', file=sys.stderr)
        return result.returncode
    print(f"Finished. Check: {output}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        sys.exit(130)
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
