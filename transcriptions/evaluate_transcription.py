#!/usr/bin/env python3
"""
Transcription Evaluation Script

This script demonstrates how to evaluate speech-to-text transcription results
using the YouTube Vaporeon copypasta evaluation dataset.

Usage:
    python evaluate_transcription.py [--predicted-file <file>] [--predicted-text "<text>"]

Example:
    python evaluate_transcription.py --predicted-text "Hey guys did you know that Vaporeon is great"
"""

import argparse
import json
import re
from pathlib import Path
import difflib
from typing import List, Tuple, Dict

class TranscriptionEvaluator:
    """Evaluates transcription accuracy using various metrics."""

    def __init__(self, dataset_file: str = "vaporeon_evaluation_dataset.json"):
        """
        Initialize evaluator with reference dataset.

        Args:
            dataset_file: Path to the evaluation dataset JSON file
        """
        with open(dataset_file, 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)

        self.reference_text = self.dataset['reference_transcript']['text']
        self.test_cases = self.dataset['test_cases']

    def normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison by:
        - Converting to lowercase
        - Removing extra whitespace
        - Removing punctuation
        - Handling sound effects consistently
        """
        # Convert to lowercase
        text = text.lower()

        # Normalize sound effects
        text = re.sub(r'\[music\]', '[music]', text, flags=re.IGNORECASE)
        text = re.sub(r'\[applause\]', '[applause]', text, flags=re.IGNORECASE)

        # Remove punctuation except sound effect markers
        text = re.sub(r'[^\w\s\[\]]', ' ', text)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def calculate_wer(self, predicted: str, reference: str) -> Tuple[float, Dict]:
        """
        Calculate Word Error Rate (WER).

        Args:
            predicted: Predicted transcription
            reference: Reference transcription

        Returns:
            Tuple of (WER score, detailed results dict)
        """
        pred_words = self.normalize_text(predicted).split()
        ref_words = self.normalize_text(reference).split()

        # Use difflib to find operations needed to transform predicted to reference
        matcher = difflib.SequenceMatcher(None, pred_words, ref_words)

        substitutions = 0
        deletions = 0
        insertions = 0
        correct = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                correct += (i2 - i1)
            elif tag == 'replace':
                substitutions += max(i2 - i1, j2 - j1)
            elif tag == 'delete':
                deletions += (i2 - i1)
            elif tag == 'insert':
                insertions += (j2 - j1)

        total_ref_words = len(ref_words)
        total_errors = substitutions + deletions + insertions

        wer = total_errors / total_ref_words if total_ref_words > 0 else 0

        results = {
            'wer': wer,
            'total_words': total_ref_words,
            'correct_words': correct,
            'substitutions': substitutions,
            'deletions': deletions,
            'insertions': insertions,
            'total_errors': total_errors
        }

        return wer, results

    def calculate_cer(self, predicted: str, reference: str) -> float:
        """
        Calculate Character Error Rate (CER).

        Args:
            predicted: Predicted transcription
            reference: Reference transcription

        Returns:
            CER score (0.0 = perfect, 1.0 = completely wrong)
        """
        pred_chars = list(self.normalize_text(predicted))
        ref_chars = list(self.normalize_text(reference))

        matcher = difflib.SequenceMatcher(None, pred_chars, ref_chars)

        errors = sum(1 for tag, _, _, _, _ in matcher.get_opcodes()
                    if tag != 'equal')

        total_chars = len(ref_chars)
        cer = errors / total_chars if total_chars > 0 else 0

        return cer

    def evaluate_key_phrases(self, predicted: str) -> Dict:
        """
        Evaluate key phrase detection accuracy.

        Args:
            predicted: Predicted transcription

        Returns:
            Dictionary with phrase detection results
        """
        key_phrases_test = None
        for test_case in self.test_cases:
            if test_case['test_id'] == 'key_phrases':
                key_phrases_test = test_case
                break

        if not key_phrases_test:
            return {'error': 'Key phrases test case not found'}

        key_phrases = key_phrases_test['key_phrases']
        predicted_lower = predicted.lower()

        detected_phrases = []
        missed_phrases = []

        for phrase in key_phrases:
            if phrase.lower() in predicted_lower:
                detected_phrases.append(phrase)
            else:
                missed_phrases.append(phrase)

        accuracy = len(detected_phrases) / len(key_phrases) if key_phrases else 0

        return {
            'total_phrases': len(key_phrases),
            'detected_phrases': detected_phrases,
            'missed_phrases': missed_phrases,
            'detection_accuracy': accuracy
        }

    def evaluate_sound_effects(self, predicted: str) -> Dict:
        """
        Evaluate sound effect detection accuracy.

        Args:
            predicted: Predicted transcription

        Returns:
            Dictionary with sound effect detection results
        """
        sound_effects_test = None
        for test_case in self.test_cases:
            if test_case['test_id'] == 'sound_effect_recognition':
                sound_effects_test = test_case
                break

        if not sound_effects_test:
            return {'error': 'Sound effects test case not found'}

        expected_effects = sound_effects_test['sound_effects']
        predicted_lower = predicted.lower()

        detected_effects = []
        missed_effects = []

        for effect in expected_effects:
            effect_patterns = [
                effect.lower(),
                effect.lower().replace('[', '').replace(']', ''),
                f"({effect.lower().replace('[', '').replace(']', '')})"
            ]

            found = any(pattern in predicted_lower for pattern in effect_patterns)

            if found:
                detected_effects.append(effect)
            else:
                missed_effects.append(effect)

        accuracy = len(detected_effects) / len(expected_effects) if expected_effects else 0

        return {
            'expected_effects': expected_effects,
            'detected_effects': detected_effects,
            'missed_effects': missed_effects,
            'detection_accuracy': accuracy
        }

    def comprehensive_evaluation(self, predicted: str) -> Dict:
        """
        Perform comprehensive evaluation of transcription.

        Args:
            predicted: Predicted transcription text

        Returns:
            Dictionary with all evaluation results
        """
        # Basic metrics
        wer, wer_details = self.calculate_wer(predicted, self.reference_text)
        cer = self.calculate_cer(predicted, self.reference_text)

        # Advanced metrics
        phrase_results = self.evaluate_key_phrases(predicted)
        sound_results = self.evaluate_sound_effects(predicted)

        # Overall assessment
        if wer <= 0.05:
            quality = "Excellent"
        elif wer <= 0.15:
            quality = "Good"
        elif wer <= 0.30:
            quality = "Fair"
        elif wer <= 0.50:
            quality = "Poor"
        else:
            quality = "Very Poor"

        return {
            'overall_quality': quality,
            'word_error_rate': wer,
            'character_error_rate': cer,
            'wer_details': wer_details,
            'key_phrase_detection': phrase_results,
            'sound_effect_detection': sound_results,
            'reference_stats': self.dataset['reference_transcript']
        }

def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate transcription accuracy")
    parser.add_argument('--predicted-file', help="File containing predicted transcription")
    parser.add_argument('--predicted-text', help="Predicted transcription text")
    parser.add_argument('--dataset', default="vaporeon_evaluation_dataset.json",
                       help="Evaluation dataset file")

    args = parser.parse_args()

    # Get predicted text
    if args.predicted_file:
        with open(args.predicted_file, 'r', encoding='utf-8') as f:
            predicted_text = f.read().strip()
    elif args.predicted_text:
        predicted_text = args.predicted_text
    else:
        # Interactive input
        print("Enter your transcription (press Ctrl+D or Ctrl+Z when done):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            predicted_text = '\n'.join(lines)

    if not predicted_text.strip():
        print("Error: No predicted text provided")
        return

    try:
        # Initialize evaluator
        evaluator = TranscriptionEvaluator(args.dataset)

        # Run evaluation
        print("🔍 Evaluating Transcription...")
        print("=" * 50)

        results = evaluator.comprehensive_evaluation(predicted_text)

        # Display results
        print(f"📊 Overall Quality: {results['overall_quality']}")
        print(f"📈 Word Error Rate (WER): {results['word_error_rate']:.2%}")
        print(f"📈 Character Error Rate (CER): {results['character_error_rate']:.2%}")

        # Detailed WER breakdown
        wer_details = results['wer_details']
        print(f"\n📋 Detailed WER Analysis:")
        print(f"   Total words: {wer_details['total_words']}")
        print(f"   Correct: {wer_details['correct_words']}")
        print(f"   Substitutions: {wer_details['substitutions']}")
        print(f"   Deletions: {wer_details['deletions']}")
        print(f"   Insertions: {wer_details['insertions']}")
        print(f"   Total errors: {wer_details['total_errors']}")

        # Key phrase detection
        phrase_results = results['key_phrase_detection']
        if 'error' not in phrase_results:
            print(f"\n🔑 Key Phrase Detection:")
            print(f"   Accuracy: {phrase_results['detection_accuracy']:.1%}")
            print(f"   Detected: {len(phrase_results['detected_phrases'])}/{phrase_results['total_phrases']}")

            if phrase_results['detected_phrases']:
                print(f"   ✅ Found phrases:")
                for phrase in phrase_results['detected_phrases'][:3]:
                    print(f"      • {phrase}")
                if len(phrase_results['detected_phrases']) > 3:
                    print(f"      • ... and {len(phrase_results['detected_phrases'])-3} more")

            if phrase_results['missed_phrases']:
                print(f"   ❌ Missed phrases:")
                for phrase in phrase_results['missed_phrases'][:3]:
                    print(f"      • {phrase}")
                if len(phrase_results['missed_phrases']) > 3:
                    print(f"      • ... and {len(phrase_results['missed_phrases'])-3} more")

        # Sound effect detection
        sound_results = results['sound_effect_detection']
        if 'error' not in sound_results:
            print(f"\n🔊 Sound Effect Detection:")
            print(f"   Accuracy: {sound_results['detection_accuracy']:.1%}")
            print(f"   Detected: {len(sound_results['detected_effects'])}/{len(sound_results['expected_effects'])}")

            if sound_results['detected_effects']:
                print(f"   ✅ Detected: {', '.join(sound_results['detected_effects'])}")

            if sound_results['missed_effects']:
                print(f"   ❌ Missed: {', '.join(sound_results['missed_effects'])}")

        # Reference comparison
        print(f"\n📖 Reference Transcript Info:")
        ref_stats = results['reference_stats']
        print(f"   Words: {ref_stats['word_count']}")
        print(f"   Characters: {ref_stats['character_count']}")
        print(f"   Contains music: {ref_stats['contains_music']}")

        # Show preview of differences if WER > 0
        if results['word_error_rate'] > 0:
            print(f"\n🔍 Text Comparison Preview:")
            ref_preview = evaluator.reference_text[:200] + "..." if len(evaluator.reference_text) > 200 else evaluator.reference_text
            pred_preview = predicted_text[:200] + "..." if len(predicted_text) > 200 else predicted_text
            print(f"   Reference: {ref_preview}")
            print(f"   Predicted: {pred_preview}")

        print(f"\n✅ Evaluation completed!")

    except FileNotFoundError as e:
        print(f"Error: Dataset file not found: {e}")
        print("Make sure you have 'vaporeon_evaluation_dataset.json' in the current directory")
    except Exception as e:
        print(f"Error during evaluation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
