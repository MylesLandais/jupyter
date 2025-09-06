# YouTube Video Transcription Evaluation Dataset

This directory contains a complete transcription evaluation dataset extracted from the YouTube video "Vaporeon copypasta (animated)" by Dangoheart Animation.

## 📁 Files Overview

### Raw Data
- `*_EWMgB26bmU_Vaporeon_copypasta_animated.json` - Complete extracted data with video metadata and raw VTT transcript
- `*_EWMgB26bmU_Vaporeon_copypasta_animated.txt` - Raw transcript with timestamps
- `*_EWMgB26bmU_Vaporeon_copypasta_animated.mp3` - Original audio file (164 seconds)

### Processed Data
- `vaporeon_transcript_clean.txt` - Clean, readable transcript without timestamps or duplications
- `vaporeon_evaluation_dataset.json` - Structured evaluation dataset with test cases and metadata

## 🎯 Dataset Purpose

This dataset is designed for evaluating speech-to-text transcription models, particularly for:
- Animated dialogue transcription
- Internet copypasta/meme content recognition  
- Mixed content with music and sound effects
- Clear speech with minimal background noise

## 📊 Dataset Statistics

- **Duration**: 164 seconds (2 minutes 44 seconds)
- **Word Count**: 270 words
- **Character Count**: 1,494 characters
- **Content Type**: Animated dialogue with copypasta
- **Audio Quality**: Good
- **Speech Clarity**: Clear
- **Language**: English (American accent)
- **Difficulty Level**: Medium

## 🧪 Test Cases

### 1. Full Transcription Test
- **Objective**: Complete accurate transcription of the entire video
- **Evaluation Method**: Word Error Rate (WER)
- **Target WER**: 0.0% (perfect reference)

### 2. Key Phrase Recognition
- **Objective**: Detection of important phrases from the copypasta content
- **Key Phrases Include**:
  - "hey guys did you know"
  - "in terms of male human and female Pokemon breeding"
  - "Vaporeon is the most compatible Pokemon"
  - "field egg group"
  - "three feet three inches tall"
  - "63.9 pounds"
  - "water-based biology"
  - "incredibly wet"
  - "water absorb and hydration"
  - "literally built for human"

### 3. Sound Effect Recognition
- **Objective**: Detection of non-speech audio elements
- **Sound Effects**: [Music], [Applause]

## 🛠 Extraction Process

1. **Download**: Used `yt-dlp` to extract audio and auto-generated subtitles
2. **Cleaning**: Removed timestamps, deduplicated repeated text from auto-generated captions
3. **Formatting**: Structured into evaluation-ready format with test cases
4. **Validation**: Manually reviewed for accuracy and completeness

## 📈 Usage Examples

### Loading the Dataset
```python
import json

# Load evaluation dataset
with open('vaporeon_evaluation_dataset.json', 'r') as f:
    dataset = json.load(f)

# Get reference transcript
reference_text = dataset['reference_transcript']['text']

# Get test cases
test_cases = dataset['test_cases']
```

### Evaluation Example
```python
def evaluate_transcription(predicted_text, reference_text):
    """
    Simple word error rate calculation
    """
    import difflib
    
    pred_words = predicted_text.lower().split()
    ref_words = reference_text.lower().split()
    
    # Calculate edit distance
    matcher = difflib.SequenceMatcher(None, ref_words, pred_words)
    errors = sum(1 for tag, _, _, _, _ in matcher.get_opcodes() 
                if tag != 'equal')
    
    wer = errors / len(ref_words) if ref_words else 0
    return wer

# Example usage
predicted = "your model's transcription here"
reference = dataset['reference_transcript']['text']
wer_score = evaluate_transcription(predicted, reference)
print(f"Word Error Rate: {wer_score:.2%}")
```

## ⚠ Content Warning

This dataset contains content from an internet copypasta with mature themes. It is included for technical evaluation purposes only.

## 🔧 Technical Details

### Extraction Command
```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 \
       --write-auto-subs --write-subs \
       --sub-langs en,en-US,en-GB \
       --sub-format vtt,srt,json3 \
       "https://www.youtube.com/watch?v=-EWMgB26bmU"
```

### Processing Steps
1. VTT subtitle parsing
2. Timestamp removal  
3. Duplicate text deduplication
4. Formatting cleanup
5. Sound effect annotation
6. Evaluation dataset structuring

## 📝 License and Attribution

- **Source Video**: "Vaporeon copypasta (animated)" by Dangoheart Animation
- **Original URL**: https://www.youtube.com/watch?v=-EWMgB26bmU
- **Extraction Date**: January 5, 2025
- **Usage**: Educational/Research purposes for transcription model evaluation

## 🚀 Getting Started

1. Use `vaporeon_transcript_clean.txt` as your reference transcript
2. Test your transcription model on the audio file `*.mp3`
3. Compare results using the evaluation framework in `vaporeon_evaluation_dataset.json`
4. Calculate Word Error Rate and phrase detection accuracy

## 📞 Support

This dataset was created as part of a transcription evaluation pipeline. For questions or improvements, refer to the extraction scripts in the parent directory.