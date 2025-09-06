#!/usr/bin/env python3
"""
Process YouTube Transcript for Evaluation Dataset

This script cleans and processes the raw transcript data to create
a clean evaluation dataset suitable for testing transcription models.
"""

import json
import re
import os
from pathlib import Path

def clean_transcript_text(raw_text):
    """
    Clean the raw VTT transcript text to extract just the spoken content.

    Args:
        raw_text: Raw transcript text with timestamps and formatting

    Returns:
        Clean transcript text with just the spoken words
    """
    # Remove timestamp lines (format: HH:MM:SS.mmm --> HH:MM:SS.mmm)
    text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*?\n', '', raw_text)

    # Remove positioning/alignment tags
    text = re.sub(r'align:\w+ position:\d+%', '', text)

    # Remove VTT formatting tags
    text = re.sub(r'<[^>]+>', '', text)

    # Split into lines and clean each
    lines = text.split('\n')
    clean_lines = []

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip lines that are just timestamps or formatting
        if re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3}', line):
            continue

        # Handle music/sound effect markers
        if line == '[Music]' or line == '[Applause]':
            clean_lines.append(f"[{line[1:-1]}]")
            continue

        # Regular spoken text
        clean_lines.append(line)

    # Join lines with spaces, handling punctuation
    result = []
    for i, line in enumerate(clean_lines):
        if line.startswith('[') and line.endswith(']'):
            # Sound effects - add as separate items
            result.append(line)
        else:
            # Regular text
            if i > 0 and not clean_lines[i-1].startswith('['):
                # If previous line was also text, add space
                if result and not result[-1].endswith(('.', '!', '?')):
                    result.append(' ')
            result.append(line)

    # Join and clean up spacing
    final_text = ''.join(result)

    # Clean up multiple spaces
    final_text = re.sub(r'\s+', ' ', final_text)

    # Fix spacing around punctuation
    final_text = re.sub(r'\s+([,.!?])', r'\1', final_text)

    return final_text.strip()

def create_eval_dataset(transcript_file, output_file=None):
    """
    Create evaluation dataset from transcript file.

    Args:
        transcript_file: Path to the JSON transcript file
        output_file: Optional output file path

    Returns:
        Dictionary with evaluation data
    """
    # Load transcript data
    with open(transcript_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    video_info = data['video_info']
    transcript_data = data['transcript']

    # Clean the transcript text
    raw_text = transcript_data['text']
    clean_text = clean_transcript_text(raw_text)

    # Create evaluation dataset
    eval_data = {
        "dataset_info": {
            "created_from": "youtube_transcript",
            "source_url": video_info['url'],
            "video_id": video_info['id'],
            "title": video_info['title'],
            "duration_seconds": video_info['duration'],
            "uploader": video_info['uploader']
        },
        "reference_transcript": {
            "text": clean_text,
            "word_count": len(clean_text.split()),
            "character_count": len(clean_text),
            "contains_music": "[Music]" in clean_text,
            "contains_applause": "[Applause]" in clean_text
        },
        "evaluation_metrics": {
            "target_wer": 0.0,  # Word Error Rate (reference is 0)
            "target_cer": 0.0,  # Character Error Rate (reference is 0)
            "difficulty": "medium",  # Based on content type
            "content_type": "animated_dialogue",
            "audio_quality": "good"
        },
        "test_cases": [
            {
                "test_id": "full_transcript",
                "description": "Complete video transcription",
                "expected_output": clean_text,
                "evaluation_type": "full_match"
            },
            {
                "test_id": "key_phrases",
                "description": "Important phrases from the content",
                "expected_phrases": extract_key_phrases(clean_text),
                "evaluation_type": "phrase_match"
            }
        ]
    }

    # Save if output file specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(eval_data, f, indent=2, ensure_ascii=False)
        print(f"Evaluation dataset saved: {output_file}")

    return eval_data

def extract_key_phrases(text):
    """Extract key phrases for evaluation testing."""
    # This is specific to the Vaporeon copypasta content
    # In a real evaluation, you'd want more sophisticated phrase extraction

    key_phrases = [
        "hey guys did you know",
        "in terms of male human and female Pokemon breeding",
        "Vaporeon is the most compatible Pokemon for humans",
        "field egg group",
        "three feet three inches tall",
        "63.9 pounds",
        "impressive base stats",
        "water-based biology",
        "incredibly wet",
        "can also learn the moves",
        "attract baby doll eyes",
        "water absorb and hydration",
        "no other Pokemon comes close",
        "literally built for human",
        "ungodly defense stats"
    ]

    # Filter phrases that actually appear in the text (case insensitive)
    found_phrases = []
    text_lower = text.lower()

    for phrase in key_phrases:
        if phrase.lower() in text_lower:
            found_phrases.append(phrase)

    return found_phrases

def main():
    """Process the transcript for evaluation."""
    # Input and output files
    input_file = "./transcriptions/-EWMgB26bmU_Vaporeon_copypasta_animated.json"
    output_file = "./transcriptions/-EWMgB26bmU_Vaporeon_copypasta_animated_eval.json"
    clean_text_file = "./transcriptions/-EWMgB26bmU_Vaporeon_copypasta_animated_clean.txt"

    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        print("Run the transcript extraction script first.")
        return

    try:
        # Create evaluation dataset
        eval_data = create_eval_dataset(input_file, output_file)

        # Also save just the clean text
        clean_text = eval_data['reference_transcript']['text']
        with open(clean_text_file, 'w', encoding='utf-8') as f:
            f.write(clean_text)

        print("\n🎉 Evaluation dataset created!")
        print(f"📊 Clean transcript: {clean_text_file}")
        print(f"📋 Evaluation data: {output_file}")

        # Show stats
        stats = eval_data['reference_transcript']
        print(f"\n📈 Statistics:")
        print(f"   Words: {stats['word_count']:,}")
        print(f"   Characters: {stats['character_count']:,}")
        print(f"   Contains music: {stats['contains_music']}")
        print(f"   Contains applause: {stats['contains_applause']}")

        # Show clean text preview
        preview = clean_text[:200] + "..." if len(clean_text) > 200 else clean_text
        print(f"\n📝 Clean Text Preview:")
        print(f"{preview}")

        # Show key phrases
        key_phrases = eval_data['test_cases'][1]['expected_phrases']
        print(f"\n🔑 Key Phrases Found: {len(key_phrases)}")
        for phrase in key_phrases[:5]:  # Show first 5
            print(f"   • {phrase}")
        if len(key_phrases) > 5:
            print(f"   ... and {len(key_phrases) - 5} more")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
