#!/bin/bash

# YouTube Video Transcription Script
# Usage: ./transcribe_video.sh [URL] [MODEL]

set -e  # Exit on error

# Default values
URL="${1:-https://www.youtube.com/watch?v=-EWMgB26bmU}"
MODEL="${2:-base}"
OUTPUT_DIR="./transcriptions"

echo "🎥 YouTube Video Transcription"
echo "================================"
echo "URL: $URL"
echo "Whisper Model: $MODEL"
echo "Output Directory: $OUTPUT_DIR"
echo ""

# Check if virtual environment exists and activate it
if [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if required tools are installed
echo "🔍 Checking dependencies..."

if ! command -v yt-dlp &> /dev/null; then
    echo "❌ yt-dlp not found. Installing..."
    pip install yt-dlp
fi

if ! python -c "import whisper" &> /dev/null; then
    echo "❌ whisper not found. Installing..."
    pip install openai-whisper
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Run the transcription
echo ""
echo "🚀 Starting transcription..."
python transcribe_youtube.py "$URL" --output-dir "$OUTPUT_DIR" --model "$MODEL" --keep-audio

echo ""
echo "✅ Transcription complete!"
echo "📂 Check the '$OUTPUT_DIR' directory for output files"
