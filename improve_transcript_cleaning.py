#!/usr/bin/env python3
"""
Improved Transcript Cleaning for YouTube Auto-Generated Subtitles

This script handles the repetitive nature of auto-generated subtitles
and creates a cleaner, more readable transcript for evaluation purposes.
"""

import json
import re
import os
from pathlib import Path
from collections import Counter
import difflib

def extract_segments_from_vtt(raw_text):
    """
    Extract individual subtitle segments with timestamps from VTT text.

    Args:
        raw_text: Raw VTT subtitle text

    Returns:
        List of (start_time, end_time, text) tuples
    """
    segments = []
    lines = raw_text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for timestamp lines
        timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})', line)
        if timestamp_match:
            start_time = timestamp_match.group(1)
            end_time = timestamp_match.group(2)

            # Get the text content (next non-empty line)
            i += 1
            text_parts = []
            while i < len(lines) and lines[i].strip():
                text_line = lines[i].strip()
                # Remove positioning/alignment info
                text_line = re.sub(r'align:\w+ position:\d+%', '', text_line)
                # Remove VTT tags
                text_line = re.sub(r'<[^>]+>', '', text_line)
                if text_line:
                    text_parts.append(text_line)
                i += 1

            if text_parts:
                segments.append((start_time, end_time, ' '.join(text_parts)))
        else:
            i += 1

    return segments

def deduplicate_segments(segments):
    """
    Remove duplicate and overlapping segments from subtitle data.

    Auto-generated subtitles often repeat the same text across multiple
    time segments as the speech recognition updates its predictions.
    """
    if not segments:
        return []

    # Group segments by similar text content
    text_groups = {}
    for start, end, text in segments:
        # Normalize text for comparison
        normalized = text.lower().strip()
        if normalized not in text_groups:
            text_groups[normalized] = []
        text_groups[normalized].append((start, end, text))

    # For each text group, keep only the longest/most complete version
    deduplicated = []

    for normalized_text, group in text_groups.items():
        if not normalized_text or normalized_text in ['[music]', '[applause]']:
            # Keep all music/sound effect markers
            deduplicated.extend(group)
        else:
            # For speech, find the most complete version
            # Sort by text length (longest first)
            group.sort(key=lambda x: len(x[2]), reverse=True)
            best_segment = group[0]
            deduplicated.append(best_segment)

    # Sort by start time
    deduplicated.sort(key=lambda x: x[0])

    return deduplicated

def merge_continuous_segments(segments):
    """
    Merge segments that represent continuous speech.

    Auto-generated subtitles often break sentences across multiple
    segments. This function tries to reconstruct complete sentences.
    """
    if not segments:
        return []

    merged = []
    current_start = None
    current_end = None
    current_text_parts = []

    for start, end, text in segments:
        text = text.strip()

        # Handle music/sound effects separately
        if text in ['[Music]', '[Applause]'] or re.match(r'^\[.*\]$', text):
            # Finish current segment if any
            if current_text_parts:
                merged_text = ' '.join(current_text_parts)
                merged.append((current_start, current_end, merged_text))
                current_start = None
                current_end = None
                current_text_parts = []

            # Add sound effect
            merged.append((start, end, text))
            continue

        # For speech segments
        if current_start is None:
            # Start new segment
            current_start = start
            current_end = end
            current_text_parts = [text]
        else:
            # Check if this continues the previous segment
            # Look for repeated text or continuation
            last_text = current_text_parts[-1] if current_text_parts else ""

            # If text is completely contained in previous text, skip it
            if text.lower() in last_text.lower():
                current_end = end  # Update end time
                continue

            # If previous text is contained in current text, replace it
            if last_text.lower() in text.lower():
                current_text_parts[-1] = text
                current_end = end
                continue

            # If texts are similar but not identical, choose the longer one
            similarity = difflib.SequenceMatcher(None, last_text.lower(), text.lower()).ratio()
            if similarity > 0.7:
                if len(text) > len(last_text):
                    current_text_parts[-1] = text
                current_end = end
                continue

            # Check if this is a natural continuation (doesn't repeat the start)
            words_last = last_text.split()
            words_current = text.split()

            # If current text starts with some words from the end of last text,
            # it's likely a continuation with overlap
            overlap_found = False
            for i in range(1, min(len(words_last), len(words_current)) + 1):
                if words_last[-i:] == words_current[:i]:
                    # Found overlap, merge without duplication
                    new_text = last_text + ' ' + ' '.join(words_current[i:])
                    current_text_parts[-1] = new_text
                    current_end = end
                    overlap_found = True
                    break

            if not overlap_found:
                # No overlap, add as new part
                current_text_parts.append(text)
                current_end = end

    # Add final segment
    if current_text_parts:
        merged_text = ' '.join(current_text_parts)
        merged.append((current_start, current_end, merged_text))

    return merged

def create_clean_transcript(segments):
    """
    Create a clean, readable transcript from processed segments.
    """
    if not segments:
        return ""

    # Extract just the text, maintaining order
    text_parts = []

    for start, end, text in segments:
        text = text.strip()

        # Handle sound effects
        if re.match(r'^\[.*\]$', text):
            text_parts.append(text)
        else:
            # Regular speech - clean up
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)

            # Capitalize first letter of sentences
            sentences = re.split(r'([.!?]+)', text)
            cleaned_sentences = []
            for i, sentence in enumerate(sentences):
                if i % 2 == 0 and sentence.strip():  # Actual sentence, not punctuation
                    sentence = sentence.strip()
                    if sentence:
                        sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                    cleaned_sentences.append(sentence)
                else:
                    cleaned_sentences.append(sentence)

            cleaned_text = ''.join(cleaned_sentences)
            if cleaned_text:
                text_parts.append(cleaned_text)

    # Join with appropriate spacing
    result = []
    for i, part in enumerate(text_parts):
        if part.startswith('[') and part.endswith(']'):
            # Sound effect
            result.append(part)
        else:
            # Regular text
            if i > 0 and not text_parts[i-1].startswith('['):
                # Previous was also text, add space if needed
                if result and not result[-1].endswith((' ', '.', '!', '?')):
                    result.append(' ')
            result.append(part)

    return ''.join(result)

def improve_transcript_cleaning(input_file, output_file=None):
    """
    Main function to improve transcript cleaning.
    """
    # Load the original transcript
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    raw_text = data['transcript']['text']

    print("🔧 Extracting segments from VTT data...")
    segments = extract_segments_from_vtt(raw_text)
    print(f"   Found {len(segments)} segments")

    print("🔧 Removing duplicates...")
    deduplicated = deduplicate_segments(segments)
    print(f"   Reduced to {len(deduplicated)} unique segments")

    print("🔧 Merging continuous segments...")
    merged = merge_continuous_segments(deduplicated)
    print(f"   Merged to {len(merged)} logical segments")

    print("🔧 Creating clean transcript...")
    clean_text = create_clean_transcript(merged)

    # Create improved dataset
    improved_data = data.copy()
    improved_data['transcript']['clean_text'] = clean_text
    improved_data['transcript']['processing_info'] = {
        'original_segments': len(segments),
        'deduplicated_segments': len(deduplicated),
        'final_segments': len(merged),
        'cleaning_method': 'improved_deduplication'
    }

    # Save if output file specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(improved_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Improved transcript saved: {output_file}")

    return clean_text, improved_data

def main():
    """Process the transcript with improved cleaning."""
    input_file = "./transcriptions/-EWMgB26bmU_Vaporeon_copypasta_animated.json"
    output_file = "./transcriptions/-EWMgB26bmU_Vaporeon_copypasta_animated_improved.json"
    clean_text_file = "./transcriptions/-EWMgB26bmU_Vaporeon_copypasta_animated_improved.txt"

    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return

    try:
        clean_text, improved_data = improve_transcript_cleaning(input_file, output_file)

        # Save clean text
        with open(clean_text_file, 'w', encoding='utf-8') as f:
            f.write(clean_text)

        print(f"\n🎉 Improved cleaning complete!")
        print(f"📋 Improved data: {output_file}")
        print(f"📝 Clean text: {clean_text_file}")

        # Show stats
        stats = improved_data['transcript']['processing_info']
        print(f"\n📊 Processing Stats:")
        print(f"   Original segments: {stats['original_segments']}")
        print(f"   After deduplication: {stats['deduplicated_segments']}")
        print(f"   Final segments: {stats['final_segments']}")

        # Show text stats
        word_count = len(clean_text.split())
        char_count = len(clean_text)
        print(f"\n📈 Text Stats:")
        print(f"   Words: {word_count:,}")
        print(f"   Characters: {char_count:,}")

        # Show preview
        preview = clean_text[:300] + "..." if len(clean_text) > 300 else clean_text
        print(f"\n📝 Clean Text Preview:")
        print(f"{preview}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
