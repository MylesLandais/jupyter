#!/usr/bin/env python3
"""
Final YouTube Transcript Cleaner

This script creates a clean, readable transcript from the YouTube auto-generated
subtitles by removing timestamps, deduplicating repeated text, and formatting
properly for evaluation purposes.
"""

import json
import re
import os

def clean_vtt_transcript(raw_text):
    """
    Clean VTT transcript text by removing timestamps and deduplicating content.

    Args:
        raw_text: Raw VTT transcript with timestamps and repeated text

    Returns:
        Clean transcript text suitable for evaluation
    """

    # Split into lines for processing
    lines = raw_text.split('\n')

    # Extract text content while removing timestamps and duplicates
    text_segments = []
    seen_text = set()

    current_text = ""

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip timestamp lines
        if '-->' in line or re.match(r'^\d{2}:\d{2}:\d{2}', line):
            continue

        # Skip positioning/alignment info
        if 'align:' in line or 'position:' in line:
            continue

        # Handle music and sound effects
        if line == '[Music]' or line == '[Applause]':
            # Only add if we haven't seen consecutive music tags
            if not (text_segments and text_segments[-1] == f"[{line[1:-1]}]"):
                text_segments.append(f"[{line[1:-1]}]")
            continue

        # Regular text content
        if line:
            # Normalize for comparison (remove extra spaces, lowercase)
            normalized = ' '.join(line.split()).lower()

            # Skip if we've seen this exact text recently
            if normalized not in seen_text:
                text_segments.append(line)
                seen_text.add(normalized)

                # Keep seen_text set manageable (rolling window)
                if len(seen_text) > 50:
                    seen_text.clear()

    # Now clean up the segments by removing partial duplicates
    cleaned_segments = []

    for i, segment in enumerate(text_segments):
        # Skip sound effects for now, we'll handle them separately
        if segment.startswith('[') and segment.endswith(']'):
            cleaned_segments.append(segment)
            continue

        # For text segments, check for partial overlaps with previous segments
        should_add = True
        segment_words = segment.lower().split()

        # Check against recent segments for overlaps
        for j in range(max(0, len(cleaned_segments) - 5), len(cleaned_segments)):
            if cleaned_segments[j].startswith('['):
                continue

            prev_words = cleaned_segments[j].lower().split()

            # If current segment is completely contained in a previous one, skip
            if all(word in ' '.join(prev_words) for word in segment_words):
                should_add = False
                break

            # If previous segment is contained in current one, replace it
            if all(word in ' '.join(segment_words) for word in prev_words):
                cleaned_segments[j] = segment
                should_add = False
                break

            # Check for significant overlap (> 70% words in common)
            common_words = set(segment_words) & set(prev_words)
            if len(common_words) / max(len(segment_words), len(prev_words)) > 0.7:
                # Keep the longer version
                if len(segment) > len(cleaned_segments[j]):
                    cleaned_segments[j] = segment
                should_add = False
                break

        if should_add:
            cleaned_segments.append(segment)

    # Final cleanup and formatting
    final_text = []

    for segment in cleaned_segments:
        if segment.startswith('[') and segment.endswith(']'):
            # Sound effects
            final_text.append(segment)
        else:
            # Regular text - clean up
            segment = re.sub(r'\s+', ' ', segment.strip())
            if segment:
                # Capitalize first letter
                segment = segment[0].upper() + segment[1:] if len(segment) > 1 else segment.upper()
                final_text.append(segment)

    # Join segments with appropriate spacing
    result_parts = []

    for i, part in enumerate(final_text):
        if part.startswith('[') and part.endswith(']'):
            # Sound effect - add with space separation
            if result_parts:
                result_parts.append(' ')
            result_parts.append(part)
        else:
            # Text - add with space if needed
            if result_parts and not result_parts[-1].endswith(' '):
                # Check if we need space
                prev_part = result_parts[-1]
                if not prev_part.endswith(('.', '!', '?', ']')):
                    result_parts.append(' ')
            result_parts.append(part)

    final_result = ''.join(result_parts)

    # Clean up multiple spaces and punctuation
    final_result = re.sub(r'\s+', ' ', final_result)
    final_result = re.sub(r'\s+([,.!?])', r'\1', final_result)

    return final_result.strip()

def create_evaluation_dataset(input_file):
    """
    Create a clean evaluation dataset from the transcript file.
    """
    # Load original data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Clean the transcript
    raw_text = data['transcript']['text']
    clean_text = clean_vtt_transcript(raw_text)

    # Create evaluation dataset
    video_info = data['video_info']

    eval_dataset = {
        "metadata": {
            "dataset_name": "YouTube Vaporeon Copypasta Transcript",
            "video_id": video_info['id'],
            "video_title": video_info['title'],
            "video_url": video_info['url'],
            "duration_seconds": video_info['duration'],
            "uploader": video_info['uploader'],
            "creation_date": "2025-01-05",
            "extraction_method": "yt-dlp auto-generated subtitles"
        },
        "reference_transcript": {
            "text": clean_text,
            "word_count": len(clean_text.split()),
            "character_count": len(clean_text),
            "sentence_count": len([s for s in re.split(r'[.!?]+', clean_text) if s.strip()]),
            "contains_music": "[Music]" in clean_text,
            "contains_sound_effects": any(marker in clean_text for marker in ["[Music]", "[Applause]"])
        },
        "evaluation_criteria": {
            "content_type": "animated_dialogue_with_copypasta",
            "audio_quality": "good",
            "speech_clarity": "clear",
            "background_noise": "minimal_music",
            "difficulty_level": "medium",
            "language": "english",
            "accent": "american"
        },
        "test_cases": [
            {
                "test_id": "full_transcription",
                "description": "Complete accurate transcription of the entire video",
                "reference_text": clean_text,
                "evaluation_method": "word_error_rate",
                "target_wer": 0.0
            },
            {
                "test_id": "key_phrases",
                "description": "Recognition of key phrases from the copypasta",
                "key_phrases": [
                    "hey guys did you know",
                    "in terms of male human and female Pokemon breeding",
                    "Vaporeon is the most compatible Pokemon",
                    "field egg group",
                    "three feet three inches tall",
                    "63.9 pounds",
                    "water-based biology",
                    "incredibly wet",
                    "water absorb and hydration",
                    "literally built for human"
                ],
                "evaluation_method": "phrase_detection"
            },
            {
                "test_id": "sound_effect_recognition",
                "description": "Detection of non-speech audio elements",
                "sound_effects": ["[Music]", "[Applause]"],
                "evaluation_method": "sound_classification"
            }
        ]
    }

    return eval_dataset, clean_text

def main():
    """Main execution function."""
    print("🎬 Final YouTube Transcript Cleaner")
    print("=" * 50)

    # File paths
    input_file = "./transcriptions/-EWMgB26bmU_Vaporeon_copypasta_animated.json"
    output_clean_file = "./transcriptions/vaporeon_transcript_clean.txt"
    output_eval_file = "./transcriptions/vaporeon_evaluation_dataset.json"

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        print("Please run the transcript extraction script first.")
        return

    try:
        print(f"📖 Loading transcript from: {input_file}")

        # Create clean dataset
        eval_dataset, clean_text = create_evaluation_dataset(input_file)

        # Save clean text
        with open(output_clean_file, 'w', encoding='utf-8') as f:
            f.write(clean_text)

        # Save evaluation dataset
        with open(output_eval_file, 'w', encoding='utf-8') as f:
            json.dump(eval_dataset, f, indent=2, ensure_ascii=False)

        print(f"✅ Clean transcript saved: {output_clean_file}")
        print(f"✅ Evaluation dataset saved: {output_eval_file}")

        # Show statistics
        stats = eval_dataset['reference_transcript']
        print(f"\n📊 Transcript Statistics:")
        print(f"   📝 Words: {stats['word_count']:,}")
        print(f"   🔤 Characters: {stats['character_count']:,}")
        print(f"   📄 Sentences: {stats['sentence_count']}")
        print(f"   🎵 Contains music: {stats['contains_music']}")
        print(f"   🔊 Contains sound effects: {stats['contains_sound_effects']}")

        # Show preview
        print(f"\n📋 Clean Transcript Preview:")
        preview_length = 300
        preview = clean_text[:preview_length]
        if len(clean_text) > preview_length:
            preview += "..."
        print(f"{preview}")

        # Show key phrases found
        key_phrases = eval_dataset['test_cases'][1]['key_phrases']
        found_phrases = [phrase for phrase in key_phrases if phrase.lower() in clean_text.lower()]

        print(f"\n🔑 Key Phrases Analysis:")
        print(f"   Total key phrases: {len(key_phrases)}")
        print(f"   Found in transcript: {len(found_phrases)}")
        print(f"   Coverage: {len(found_phrases)/len(key_phrases)*100:.1f}%")

        if found_phrases:
            print(f"   ✅ Found phrases:")
            for phrase in found_phrases[:5]:  # Show first 5
                print(f"      • {phrase}")
            if len(found_phrases) > 5:
                print(f"      • ... and {len(found_phrases)-5} more")

        print(f"\n🎉 Final transcript cleaning completed!")
        print(f"📁 Files ready for evaluation testing")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
