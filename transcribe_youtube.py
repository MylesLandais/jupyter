#!/usr/bin/env python3
"""
YouTube Video Download and Transcription Script

This script downloads a YouTube video using yt-dlp and transcribes it using OpenAI's Whisper.
Designed for creating evaluation datasets from video content.

Usage:
    python transcribe_youtube.py <youtube_url> [--output-dir <dir>] [--model <whisper_model>]

Example:
    python transcribe_youtube.py "https://www.youtube.com/watch?v=-EWMgB26bmU"
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import tempfile
import shutil

try:
    import whisper
except ImportError:
    print("Whisper not installed. Install with: pip install openai-whisper")
    sys.exit(1)


class YouTubeTranscriber:
    """Handles YouTube video download and transcription."""

    def __init__(self, output_dir: str = "./transcriptions", whisper_model: str = "base"):
        """
        Initialize the transcriber.

        Args:
            output_dir: Directory to save outputs
            whisper_model: Whisper model size (tiny, base, small, medium, large)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.whisper_model = whisper_model
        self.model = None

    def load_whisper_model(self):
        """Load the Whisper model (lazy loading)."""
        if self.model is None:
            print(f"Loading Whisper model: {self.whisper_model}")
            self.model = whisper.load_model(self.whisper_model)
        return self.model

    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        if "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("/")[-1].split("?")[0]
        else:
            raise ValueError(f"Unable to extract video ID from URL: {url}")

    def get_video_info(self, url: str) -> Dict:
        """Get video metadata using yt-dlp."""
        try:
            cmd = [
                "yt-dlp",
                "--dump-json",
                "--no-download",
                url
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get video info: {e.stderr}")

    def download_audio(self, url: str, output_path: str) -> str:
        """
        Download audio from YouTube video.

        Args:
            url: YouTube URL
            output_path: Path to save the audio file

        Returns:
            Path to the downloaded audio file
        """
        try:
            cmd = [
                "yt-dlp",
                "-x",  # Extract audio only
                "--audio-format", "mp3",
                "--audio-quality", "0",  # Best quality
                "-o", output_path,
                url
            ]

            print(f"Downloading audio from: {url}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # yt-dlp adds the extension, so we need to find the actual file
            base_path = Path(output_path)
            audio_file = base_path.with_suffix(".mp3")

            if not audio_file.exists():
                # Try to find the downloaded file
                parent_dir = base_path.parent
                pattern = f"{base_path.stem}.*"
                candidates = list(parent_dir.glob(pattern))
                if candidates:
                    audio_file = candidates[0]
                else:
                    raise FileNotFoundError("Downloaded audio file not found")

            print(f"Audio downloaded: {audio_file}")
            return str(audio_file)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to download audio: {e.stderr}")

    def transcribe_audio(self, audio_path: str) -> Dict:
        """
        Transcribe audio file using Whisper.

        Args:
            audio_path: Path to the audio file

        Returns:
            Transcription result dictionary
        """
        model = self.load_whisper_model()

        print(f"Transcribing audio: {audio_path}")
        result = model.transcribe(
            audio_path,
            verbose=True,
            word_timestamps=True
        )

        return result

    def save_transcription(self, result: Dict, video_info: Dict, output_prefix: str):
        """
        Save transcription results in multiple formats.

        Args:
            result: Whisper transcription result
            video_info: Video metadata
            output_prefix: Prefix for output files
        """
        # Save full JSON with all data
        full_data = {
            "video_info": {
                "id": video_info.get("id"),
                "title": video_info.get("title"),
                "description": video_info.get("description"),
                "duration": video_info.get("duration"),
                "upload_date": video_info.get("upload_date"),
                "uploader": video_info.get("uploader"),
                "view_count": video_info.get("view_count"),
                "like_count": video_info.get("like_count"),
                "url": video_info.get("webpage_url"),
            },
            "transcription": result
        }

        json_path = f"{output_prefix}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, indent=2, ensure_ascii=False)
        print(f"Full data saved: {json_path}")

        # Save plain text transcript
        txt_path = f"{output_prefix}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {video_info.get('title', 'N/A')}\n")
            f.write(f"URL: {video_info.get('webpage_url', 'N/A')}\n")
            f.write(f"Duration: {video_info.get('duration', 'N/A')} seconds\n")
            f.write(f"Uploader: {video_info.get('uploader', 'N/A')}\n")
            f.write("-" * 50 + "\n\n")
            f.write(result["text"])
        print(f"Text transcript saved: {txt_path}")

        # Save SRT subtitle file
        srt_path = f"{output_prefix}.srt"
        self.save_srt(result["segments"], srt_path)
        print(f"SRT subtitles saved: {srt_path}")

        # Save VTT subtitle file
        vtt_path = f"{output_prefix}.vtt"
        self.save_vtt(result["segments"], vtt_path)
        print(f"VTT subtitles saved: {vtt_path}")

    def save_srt(self, segments: list, output_path: str):
        """Save segments as SRT subtitle file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start_time = self.format_timestamp(segment['start'])
                end_time = self.format_timestamp(segment['end'])
                text = segment['text'].strip()

                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

    def save_vtt(self, segments: list, output_path: str):
        """Save segments as VTT subtitle file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")

            for segment in segments:
                start_time = self.format_timestamp_vtt(segment['start'])
                end_time = self.format_timestamp_vtt(segment['end'])
                text = segment['text'].strip()

                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

    def format_timestamp(self, seconds: float) -> str:
        """Format seconds to SRT timestamp format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def format_timestamp_vtt(self, seconds: float) -> str:
        """Format seconds to VTT timestamp format (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def process_video(self, url: str, keep_audio: bool = False) -> Tuple[str, Dict]:
        """
        Complete pipeline: download and transcribe a YouTube video.

        Args:
            url: YouTube URL
            keep_audio: Whether to keep the downloaded audio file

        Returns:
            Tuple of (output_prefix, transcription_result)
        """
        # Get video info
        print("Getting video information...")
        video_info = self.get_video_info(url)

        # Create safe filename
        video_id = self.extract_video_id(url)
        safe_title = "".join(c for c in video_info.get('title', video_id)
                           if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title[:50]  # Limit length

        filename = f"{video_id}_{safe_title}".replace(" ", "_")
        output_prefix = self.output_dir / filename

        # Download audio
        audio_path = None
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_audio = os.path.join(temp_dir, "audio")
                audio_path = self.download_audio(url, temp_audio)

                # Transcribe
                result = self.transcribe_audio(audio_path)

                # Save results
                self.save_transcription(result, video_info, str(output_prefix))

                # Optionally keep audio file
                if keep_audio:
                    final_audio_path = f"{output_prefix}.mp3"
                    shutil.copy2(audio_path, final_audio_path)
                    print(f"Audio file saved: {final_audio_path}")

                return str(output_prefix), result

        except Exception as e:
            print(f"Error processing video: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description="Download and transcribe YouTube videos")
    parser.add_argument("url", help="YouTube URL to transcribe")
    parser.add_argument("--output-dir", "-o", default="./transcriptions",
                       help="Output directory (default: ./transcriptions)")
    parser.add_argument("--model", "-m", default="base",
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size (default: base)")
    parser.add_argument("--keep-audio", "-k", action="store_true",
                       help="Keep downloaded audio file")

    args = parser.parse_args()

    try:
        transcriber = YouTubeTranscriber(args.output_dir, args.model)
        output_prefix, result = transcriber.process_video(args.url, args.keep_audio)

        print(f"\n✅ Transcription completed!")
        print(f"📁 Output files: {output_prefix}.*")
        print(f"📝 Text length: {len(result['text'])} characters")
        print(f"⏱️  Duration: {result.get('duration', 'Unknown')} seconds")
        print(f"🎯 Segments: {len(result.get('segments', []))}")

    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
