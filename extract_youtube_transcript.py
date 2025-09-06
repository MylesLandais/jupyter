#!/usr/bin/env python3
"""
YouTube Transcript Extractor using yt-dlp

This script extracts transcripts/subtitles from YouTube videos using yt-dlp's
built-in subtitle extraction capabilities. No additional transcription libraries needed.

Usage:
    python extract_youtube_transcript.py

This will extract transcript from: https://www.youtube.com/watch?v=-EWMgB26bmU
"""

import json
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import re

# The target video URL
VIDEO_URL = "https://www.youtube.com/watch?v=-EWMgB26bmU"

# Use persistent dataset directory (mounted from host ~/downloads/ytdlp)
# In dev container, this will be mounted to /home/jovyan/downloads/ytdlp
OUTPUT_DIR = "/home/jovyan/downloads/ytdlp"

# Ensure output directory exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def run_command(cmd, description="Running command"):
    """Run a shell command and return the result."""
    print(f"{description}: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Stderr: {e.stderr}")
        raise

def check_yt_dlp():
    """Check if yt-dlp is available."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        print("SUCCESS: yt-dlp is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: yt-dlp not found")
        print("Install with: sudo pacman -S yt-dlp  # or your package manager")
        return False

def get_video_info(url):
    """Get video metadata using yt-dlp."""
    cmd = ["yt-dlp", "--dump-json", "--no-download", url]
    result = run_command(cmd, "Getting video info")
    return json.loads(result.stdout)

def list_available_subtitles(url):
    """List available subtitles for the video."""
    cmd = ["yt-dlp", "--list-subs", url]
    result = run_command(cmd, "Listing available subtitles")
    return result.stdout

def download_subtitles(url, output_path):
    """Download subtitles from YouTube video."""

    # Try to get auto-generated subtitles first (more likely to be available)
    cmd = [
        "yt-dlp",
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs", "en,en-US,en-GB",
        "--sub-format", "vtt,srt,json3",
        "--skip-download",  # Only download subtitles
        "-o", output_path,
        url
    ]

    try:
        result = run_command(cmd, "Downloading subtitles")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to download subtitles: {e}")
        return False

def download_audio_and_transcript(url, output_path):
    """Download audio and attempt to extract transcript."""

    # Download audio for backup transcription if needed
    audio_cmd = [
        "yt-dlp",
        "-x",  # Extract audio only
        "--audio-format", "mp3",
        "--audio-quality", "0",  # Best quality
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs", "en,en-US,en-GB",
        "--sub-format", "vtt,srt,json3",
        "-o", output_path,
        url
    ]

    try:
        result = run_command(audio_cmd, "Downloading audio and subtitles")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to download: {e}")
        return False

def find_subtitle_files(base_path):
    """Find downloaded subtitle files."""
    base = Path(base_path)
    parent_dir = base.parent
    stem = base.stem

    # Look for subtitle files
    patterns = [
        f"{stem}.*.vtt",
        f"{stem}.*.srt",
        f"{stem}.*.json3",
        f"{stem}.en.vtt",
        f"{stem}.en.srt",
        f"{stem}.en.json3"
    ]

    subtitle_files = []
    for pattern in patterns:
        matches = list(parent_dir.glob(pattern))
        subtitle_files.extend(matches)

    return subtitle_files

def parse_vtt_content(vtt_path):
    """Parse VTT subtitle file and extract text."""
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove VTT header
    content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.MULTILINE | re.DOTALL)

    # Extract text lines (skip timestamp lines)
    lines = content.split('\n')
    text_lines = []

    for line in lines:
        line = line.strip()
        # Skip empty lines and timestamp lines
        if line and not re.match(r'^\d+:\d+:\d+\.\d+ --> \d+:\d+:\d+\.\d+$', line):
            # Remove VTT formatting tags
            clean_line = re.sub(r'<[^>]+>', '', line)
            if clean_line:
                text_lines.append(clean_line)

    return '\n'.join(text_lines)

def parse_srt_content(srt_path):
    """Parse SRT subtitle file and extract text."""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by subtitle blocks
    blocks = re.split(r'\n\s*\n', content.strip())
    text_lines = []

    for block in blocks:
        lines = block.split('\n')
        # Skip subtitle number and timestamp lines
        for line in lines[2:] if len(lines) > 2 else []:
            line = line.strip()
            if line:
                text_lines.append(line)

    return '\n'.join(text_lines)

def parse_json3_content(json_path):
    """Parse JSON3 subtitle file and extract text."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract events/cues
    events = data.get('events', [])
    text_parts = []

    for event in events:
        if 'segs' in event:
            for seg in event['segs']:
                if 'utf8' in seg:
                    text_parts.append(seg['utf8'])

    return ''.join(text_parts)

def extract_transcript_from_files(subtitle_files):
    """Extract transcript text from subtitle files."""
    transcript_text = ""

    # Prefer JSON3, then VTT, then SRT
    for ext in ['.json3', '.vtt', '.srt']:
        for file_path in subtitle_files:
            if str(file_path).endswith(ext):
                print(f"Processing subtitle file: {file_path}")

                try:
                    if ext == '.vtt':
                        transcript_text = parse_vtt_content(file_path)
                    elif ext == '.srt':
                        transcript_text = parse_srt_content(file_path)
                    elif ext == '.json3':
                        transcript_text = parse_json3_content(file_path)

                    if transcript_text.strip():
                        print(f"SUCCESS: Successfully extracted transcript from {file_path}")
                        return transcript_text, file_path
                except Exception as e:
                    print(f"ERROR: Failed to parse {file_path}: {e}")
                    continue

    return "", None

def save_transcript(transcript_text, video_info, output_prefix, source_file=None):
    """Save transcript in multiple formats."""

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_prefix), exist_ok=True)

    # Save full JSON
    full_data = {
        "video_info": {
            "id": video_info.get("id"),
            "title": video_info.get("title"),
            "description": video_info.get("description", "")[:500] + "..." if len(video_info.get("description", "")) > 500 else video_info.get("description", ""),
            "duration": video_info.get("duration"),
            "upload_date": video_info.get("upload_date"),
            "uploader": video_info.get("uploader"),
            "view_count": video_info.get("view_count"),
            "url": video_info.get("webpage_url"),
        },
        "transcript": {
            "text": transcript_text,
            "source_file": str(source_file) if source_file else None,
            "extraction_method": "yt-dlp_subtitles"
        }
    }

    json_path = f"{output_prefix}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2, ensure_ascii=False)
    print(f"SUCCESS: Full data saved: {json_path}")

    # Save plain text
    txt_path = f"{output_prefix}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Title: {video_info.get('title', 'N/A')}\n")
        f.write(f"URL: {video_info.get('webpage_url', 'N/A')}\n")
        f.write(f"Duration: {video_info.get('duration', 'N/A')} seconds\n")
        f.write(f"Uploader: {video_info.get('uploader', 'N/A')}\n")
        f.write(f"Upload Date: {video_info.get('upload_date', 'N/A')}\n")
        f.write(f"Views: {video_info.get('view_count', 'N/A'):,}" if video_info.get('view_count') else "Views: N/A")
        f.write("\n" + "-" * 50 + "\n\n")
        f.write(transcript_text)

    print(f"SUCCESS: Text transcript saved: {txt_path}")

    return json_path, txt_path

def main():
    """Main transcript extraction pipeline."""
    print("YouTube Transcript Extractor")
    print("=" * 50)
    print(f"Video URL: {VIDEO_URL}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print()

    # Check dependencies
    if not check_yt_dlp():
        print("\nERROR: yt-dlp not found. Please install it first.")
        sys.exit(1)

    try:
        # Get video info
        print("\nGetting video information...")
        video_info = get_video_info(VIDEO_URL)

        # Create safe filename
        video_id = video_info.get("id", "unknown")
        title = video_info.get("title", "unknown")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:50]  # Limit length

        filename = f"{video_id}_{safe_title}".replace(" ", "_")
        output_prefix = os.path.join(OUTPUT_DIR, filename)

        print(f"Title: {title}")
        print(f"Duration: {video_info.get('duration')} seconds")
        print(f"Uploader: {video_info.get('uploader')}")

        # List available subtitles
        print(f"\nChecking available subtitles...")
        subtitle_info = list_available_subtitles(VIDEO_URL)
        print(subtitle_info)

        # Download subtitles and audio
        print(f"\nDownloading subtitles and audio...")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, "video")

            success = download_audio_and_transcript(VIDEO_URL, temp_path)

            if not success:
                print("ERROR: Failed to download content")
                sys.exit(1)

            # Find subtitle files
            subtitle_files = find_subtitle_files(temp_path)
            print(f"Found subtitle files: {[str(f) for f in subtitle_files]}")

            if not subtitle_files:
                print("ERROR: No subtitle files found")
                sys.exit(1)

            # Extract transcript
            transcript_text, source_file = extract_transcript_from_files(subtitle_files)

            if not transcript_text.strip():
                print("ERROR: Failed to extract transcript text")
                sys.exit(1)

            # Save results
            print(f"\nSaving transcript...")
            json_path, txt_path = save_transcript(transcript_text, video_info, output_prefix, source_file)

            # Copy audio file if it exists
            audio_files = list(Path(temp_dir).glob("*.mp3"))
            if audio_files:
                audio_file = audio_files[0]
                final_audio_path = f"{output_prefix}.mp3"
                import shutil
                shutil.copy2(audio_file, final_audio_path)
                print(f"SUCCESS: Audio file saved: {final_audio_path}")

        print(f"\nSUCCESS: Transcript extraction completed!")
        print(f"Output files: {output_prefix}.*")

        # Show text preview
        preview = transcript_text[:300] + "..." if len(transcript_text) > 300 else transcript_text
        print(f"\nPreview:\n{preview}")
        print(f"\nStats:")
        print(f"   Characters: {len(transcript_text):,}")
        print(f"   Words: {len(transcript_text.split()):,}")
        print(f"   Lines: {len(transcript_text.splitlines()):,}")

    except KeyboardInterrupt:
        print("\nERROR: Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
