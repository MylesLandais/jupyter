#!/usr/bin/env python3
"""
Simple YouTube Video Download and Transcription Script

This script downloads a YouTube video using yt-dlp and transcribes it.
Designed for creating evaluation datasets from video content.

Usage:
    python transcribe_video_simple.py

This will transcribe: https://www.youtube.com/watch?v=-EWMgB26bmU
"""

import json
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import shutil

# The target video URL
VIDEO_URL = "https://www.youtube.com/watch?v=-EWMgB26bmU"
OUTPUT_DIR = "./transcriptions"

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

def check_dependencies():
    """Check if required tools are available."""
    print("Checking dependencies...")

    # Check yt-dlp
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        print("✅ yt-dlp is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ yt-dlp not found")
        print("Install with: sudo pacman -S yt-dlp  # or your package manager")
        return False

    # Check if we can use whisper via whisper.cpp or other methods
    whisper_available = False

    # Try whisper.cpp
    try:
        subprocess.run(["whisper"], capture_output=True)
        whisper_available = True
        print("✅ whisper (whisper.cpp) is available")
    except FileNotFoundError:
        pass

    # Try faster-whisper
    try:
        import faster_whisper
        whisper_available = True
        print("✅ faster-whisper is available")
    except ImportError:
        pass

    # Try openai-whisper
    try:
        import whisper
        whisper_available = True
        print("✅ openai-whisper is available")
    except ImportError:
        pass

    if not whisper_available:
        print("❌ No whisper implementation found")
        print("Options:")
        print("1. Install whisper.cpp: https://github.com/ggerganov/whisper.cpp")
        print("2. Install faster-whisper: pip install --user faster-whisper")
        print("3. Install openai-whisper: pip install --user openai-whisper")
        return False

    return True

def get_video_info(url):
    """Get video metadata using yt-dlp."""
    cmd = ["yt-dlp", "--dump-json", "--no-download", url]
    result = run_command(cmd, "Getting video info")
    return json.loads(result.stdout)

def download_audio(url, output_path):
    """Download audio from YouTube video."""
    cmd = [
        "yt-dlp",
        "-x",  # Extract audio only
        "--audio-format", "mp3",
        "--audio-quality", "0",  # Best quality
        "-o", output_path,
        url
    ]

    run_command(cmd, "Downloading audio")

    # Find the actual downloaded file
    base_path = Path(output_path)
    audio_file = base_path.with_suffix(".mp3")

    if not audio_file.exists():
        # Try to find the downloaded file
        parent_dir = base_path.parent
        candidates = list(parent_dir.glob(f"{base_path.stem}.*"))
        if candidates:
            audio_file = candidates[0]
        else:
            raise FileNotFoundError("Downloaded audio file not found")

    return str(audio_file)

def transcribe_with_whisper_cpp(audio_path, output_path):
    """Transcribe using whisper.cpp."""
    cmd = [
        "whisper",
        "-f", audio_path,
        "-oj",  # Output JSON
        "-of", output_path.replace(".json", "")
    ]

    try:
        run_command(cmd, "Transcribing with whisper.cpp")
        return True
    except:
        return False

def transcribe_with_faster_whisper(audio_path):
    """Transcribe using faster-whisper."""
    try:
        from faster_whisper import WhisperModel

        print("Transcribing with faster-whisper...")
        model = WhisperModel("base", device="cpu", compute_type="int8")

        segments, info = model.transcribe(audio_path, beam_size=5)

        result = {
            "text": "",
            "segments": [],
            "language": info.language,
            "duration": info.duration
        }

        for segment in segments:
            segment_dict = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            }
            result["segments"].append(segment_dict)
            result["text"] += segment.text

        return result
    except ImportError:
        return None

def transcribe_with_openai_whisper(audio_path):
    """Transcribe using openai-whisper."""
    try:
        import whisper

        print("Transcribing with openai-whisper...")
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, verbose=True, word_timestamps=True)
        return result
    except ImportError:
        return None

def transcribe_audio(audio_path, output_path):
    """Transcribe audio using available whisper implementation."""

    # Try whisper.cpp first (fastest)
    if transcribe_with_whisper_cpp(audio_path, output_path):
        json_path = output_path.replace(".json", ".json")
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.load(f)

    # Try faster-whisper
    result = transcribe_with_faster_whisper(audio_path)
    if result:
        return result

    # Try openai-whisper
    result = transcribe_with_openai_whisper(audio_path)
    if result:
        return result

    raise RuntimeError("No working whisper implementation found")

def save_transcription(result, video_info, output_prefix):
    """Save transcription results in multiple formats."""

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_prefix), exist_ok=True)

    # Save full JSON
    full_data = {
        "video_info": {
            "id": video_info.get("id"),
            "title": video_info.get("title"),
            "description": video_info.get("description"),
            "duration": video_info.get("duration"),
            "upload_date": video_info.get("upload_date"),
            "uploader": video_info.get("uploader"),
            "view_count": video_info.get("view_count"),
            "url": video_info.get("webpage_url"),
        },
        "transcription": result
    }

    json_path = f"{output_prefix}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Full data saved: {json_path}")

    # Save plain text
    txt_path = f"{output_prefix}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Title: {video_info.get('title', 'N/A')}\n")
        f.write(f"URL: {video_info.get('webpage_url', 'N/A')}\n")
        f.write(f"Duration: {video_info.get('duration', 'N/A')} seconds\n")
        f.write(f"Uploader: {video_info.get('uploader', 'N/A')}\n")
        f.write("-" * 50 + "\n\n")

        # Handle different result formats
        if isinstance(result, dict) and "text" in result:
            f.write(result["text"])
        elif isinstance(result, str):
            f.write(result)
        else:
            f.write(str(result))

    print(f"✅ Text transcript saved: {txt_path}")

    # Save segments if available
    if isinstance(result, dict) and "segments" in result and result["segments"]:
        srt_path = f"{output_prefix}.srt"
        save_srt(result["segments"], srt_path)
        print(f"✅ SRT subtitles saved: {srt_path}")

def save_srt(segments, output_path):
    """Save segments as SRT subtitle file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            text = segment['text'].strip()

            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")

def format_timestamp(seconds):
    """Format seconds to SRT timestamp format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def main():
    """Main transcription pipeline."""
    print("🎥 YouTube Video Transcription")
    print("=" * 50)
    print(f"Video URL: {VIDEO_URL}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print()

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install them first.")
        sys.exit(1)

    try:
        # Get video info
        print("\n📋 Getting video information...")
        video_info = get_video_info(VIDEO_URL)

        # Create safe filename
        video_id = video_info.get("id", "unknown")
        title = video_info.get("title", "unknown")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:50]  # Limit length

        filename = f"{video_id}_{safe_title}".replace(" ", "_")
        output_prefix = os.path.join(OUTPUT_DIR, filename)

        print(f"📁 Title: {title}")
        print(f"⏱️  Duration: {video_info.get('duration')} seconds")
        print(f"👤 Uploader: {video_info.get('uploader')}")

        # Download audio
        print(f"\n🎵 Downloading audio...")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_audio_path = os.path.join(temp_dir, "audio")
            audio_path = download_audio(VIDEO_URL, temp_audio_path)
            print(f"✅ Audio downloaded: {audio_path}")

            # Transcribe
            print(f"\n🗣️  Transcribing audio...")
            result = transcribe_audio(audio_path, output_prefix + ".json")

            # Save results
            print(f"\n💾 Saving results...")
            save_transcription(result, video_info, output_prefix)

            # Optionally copy audio file
            final_audio_path = f"{output_prefix}.mp3"
            shutil.copy2(audio_path, final_audio_path)
            print(f"✅ Audio file saved: {final_audio_path}")

        print(f"\n🎉 Transcription completed!")
        print(f"📂 Output files: {output_prefix}.*")

        # Show text preview
        if isinstance(result, dict) and "text" in result:
            text = result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"]
            print(f"\n📝 Preview:\n{text}")

    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
