#!/usr/bin/env python3
"""
ASR Model Leaderboard Generator for Vaporeon Dataset
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from asr_evaluation.adapters.faster_whisper_adapter import FasterWhisperAdapter
from asr_evaluation.adapters.olmoasr_adapter import OLMoASRAdapter
from asr_evaluation.storage.postgres_storage import PostgreSQLStorage


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Calculate Word Error Rate (WER)."""
    ref_words = reference.lower().split()
    hyp_words = hypothesis.lower().split()
    
    if len(ref_words) == 0:
        return 1.0 if len(hyp_words) > 0 else 0.0
    
    # Simple Levenshtein distance for words
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    
    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j
    
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = min(d[i-1][j], d[i][j-1], d[i-1][j-1]) + 1
    
    return d[len(ref_words)][len(hyp_words)] / len(ref_words)


def calculate_cer(reference: str, hypothesis: str) -> float:
    """Calculate Character Error Rate (CER)."""
    ref_chars = list(reference.lower())
    hyp_chars = list(hypothesis.lower())
    
    if len(ref_chars) == 0:
        return 1.0 if len(hyp_chars) > 0 else 0.0
    
    # Simple Levenshtein distance for characters
    d = [[0] * (len(hyp_chars) + 1) for _ in range(len(ref_chars) + 1)]
    
    for i in range(len(ref_chars) + 1):
        d[i][0] = i
    for j in range(len(hyp_chars) + 1):
        d[0][j] = j
    
    for i in range(1, len(ref_chars) + 1):
        for j in range(1, len(hyp_chars) + 1):
            if ref_chars[i-1] == hyp_chars[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = min(d[i-1][j], d[i][j-1], d[i-1][j-1]) + 1
    
    return d[len(ref_chars)][len(hyp_chars)] / len(ref_chars)


def load_reference_text() -> str:
    """Load the reference transcription."""
    ref_file = Path("transcriptions/vaporeon_transcript_clean.txt")
    
    if ref_file.exists():
        with open(ref_file, 'r') as f:
            return f.read().strip()
    else:
        print(f"ERROR: Reference file not found: {ref_file}")
        return ""


def test_model(adapter, model_name: str, audio_file: str, reference: str, 
               storage: Optional[PostgreSQLStorage], experiment_id: str) -> Dict[str, Any]:
    """Test a single model and return results."""
    print(f"\nTesting {model_name}...")
    
    try:
        # Check availability
        if not adapter.is_available():
            return {
                "model_name": model_name,
                "status": "UNAVAILABLE",
                "error": "Model not available"
            }
        
        # Transcribe
        start_time = time.time()
        result = adapter.transcribe(audio_file)
        total_time = time.time() - start_time
        
        # Calculate metrics
        wer = calculate_wer(reference, result.text)
        cer = calculate_cer(reference, result.text)
        
        # Calculate processing speed (seconds per minute of audio)
        audio_duration = result.metadata.get("audio_duration", 164)  # Vaporeon is ~164s
        speed_ratio = result.processing_time / (audio_duration / 60)
        
        # Get model info
        model_info = adapter.get_model_info()
        
        # Save to database if available
        if storage:
            try:
                response_id = storage.save_response(
                    experiment_id=experiment_id,
                    model_name=model_info.name,
                    model_version=model_info.version,
                    model_type=model_info.model_type,
                    predicted_text=result.text,
                    wer=wer,
                    cer=cer,
                    processing_time=result.processing_time,
                    audio_duration=audio_duration,
                    audio_file=audio_file,
                    device=result.metadata.get("device", "unknown"),
                    confidence_scores=result.confidence_scores,
                    model_parameters=result.metadata,
                    metadata={
                        "speed_ratio": speed_ratio,
                        "word_count": len(result.text.split()),
                        "char_count": len(result.text),
                        "total_time": total_time
                    }
                )
                print(f"  Saved to database with ID: {response_id[:8]}...")
            except Exception as e:
                print(f"  WARNING: Failed to save to database: {e}")
        else:
            print("  Database not available - results saved to files only")
        
        return {
            "model_name": model_name,
            "status": "SUCCESS",
            "transcription": result.text,
            "wer": wer,
            "cer": cer,
            "processing_time": result.processing_time,
            "total_time": total_time,
            "speed_ratio": speed_ratio,
            "word_count": len(result.text.split()),
            "char_count": len(result.text),
            "confidence_available": result.confidence_scores is not None,
            "metadata": result.metadata
        }
        
    except Exception as e:
        return {
            "model_name": model_name,
            "status": "ERROR",
            "error": str(e)
        }


def print_database_leaderboard(results: List[Dict[str, Any]]):
    """Print leaderboard from database results."""
    print("\n" + "="*100)
    print("ASR MODEL LEADERBOARD - ALL TIME (FROM DATABASE)")
    print("="*100)
    
    if not results:
        print("No results found in database!")
        return
    
    # Print header
    print(f"{'Rank':<4} {'Model':<25} {'Version':<15} {'Avg WER':<8} {'Best WER':<8} {'Evals':<6} {'Last Run'}")
    print("-" * 100)
    
    # Print results
    for i, result in enumerate(results, 1):
        model_name = result["model_name"][:24]
        version = result["model_version"][:14] if result["model_version"] else "N/A"
        avg_wer = f"{result['avg_wer']:.2%}"
        best_wer = f"{result['best_wer']:.2%}"
        eval_count = str(result["evaluation_count"])
        last_run = result["last_evaluation"].strftime("%m/%d %H:%M") if result["last_evaluation"] else "N/A"
        
        print(f"{i:<4} {model_name:<25} {version:<15} {avg_wer:<8} {best_wer:<8} {eval_count:<6} {last_run}")


def print_leaderboard(results: List[Dict[str, Any]]):
    """Print a formatted leaderboard table."""
    print("\n" + "="*100)
    print("ASR MODEL LEADERBOARD - CURRENT RUN")
    print("="*100)
    
    # Filter successful results
    successful_results = [r for r in results if r["status"] == "SUCCESS"]
    
    if not successful_results:
        print("No successful transcriptions to rank!")
        return
    
    # Sort by WER (lower is better)
    successful_results.sort(key=lambda x: x["wer"])
    
    # Print header
    print(f"{'Rank':<4} {'Model':<25} {'WER':<8} {'CER':<8} {'Speed':<10} {'Words':<7} {'Time':<8} {'Status'}")
    print("-" * 100)
    
    # Print results
    for i, result in enumerate(successful_results, 1):
        model_name = result["model_name"][:24]  # Truncate long names
        wer = f"{result['wer']:.2%}"
        cer = f"{result['cer']:.2%}"
        speed = f"{result['speed_ratio']:.2f}x"
        words = str(result["word_count"])
        proc_time = f"{result['processing_time']:.1f}s"
        
        print(f"{i:<4} {model_name:<25} {wer:<8} {cer:<8} {speed:<10} {words:<7} {proc_time:<8} SUCCESS")
    
    # Print failed results
    failed_results = [r for r in results if r["status"] != "SUCCESS"]
    if failed_results:
        print("\nFAILED MODELS:")
        print("-" * 60)
        for result in failed_results:
            model_name = result["model_name"][:24]
            status = result["status"]
            error = result.get("error", "Unknown error")[:30]
            print(f"{model_name:<25} {status:<12} {error}")
    
    # Print summary statistics
    if successful_results:
        print(f"\nSUMMARY:")
        print(f"- Best WER: {successful_results[0]['wer']:.2%} ({successful_results[0]['model_name']})")
        print(f"- Fastest: {min(successful_results, key=lambda x: x['speed_ratio'])['model_name']}")
        print(f"- Most words: {max(successful_results, key=lambda x: x['word_count'])['model_name']}")
        print(f"- Average WER: {sum(r['wer'] for r in successful_results) / len(successful_results):.2%}")


def save_results(results: List[Dict[str, Any]], output_file: str = "leaderboard_results.json"):
    """Save detailed results to JSON file and individual transcription files."""
    # Save JSON results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nDetailed results saved to: {output_file}")
    
    # Create transcriptions directory
    transcriptions_dir = Path("results/transcriptions")
    transcriptions_dir.mkdir(parents=True, exist_ok=True)
    
    # Save individual transcription files
    successful_results = [r for r in results if r["status"] == "SUCCESS"]
    
    for result in successful_results:
        model_name = result["model_name"].replace("/", "_").replace("-", "_")
        transcript_file = transcriptions_dir / f"{model_name}_vaporeon.txt"
        
        with open(transcript_file, 'w') as f:
            f.write(f"Model: {result['model_name']}\n")
            f.write(f"WER: {result['wer']:.2%}\n")
            f.write(f"CER: {result['cer']:.2%}\n")
            f.write(f"Processing Time: {result['processing_time']:.2f}s\n")
            f.write(f"Word Count: {result['word_count']}\n")
            f.write(f"Character Count: {result['char_count']}\n")
            f.write("-" * 50 + "\n")
            f.write("TRANSCRIPTION:\n")
            f.write(result['transcription'])
    
    if successful_results:
        print(f"Individual transcriptions saved to: {transcriptions_dir}/")
        print(f"Files created:")
        for result in successful_results:
            model_name = result["model_name"].replace("/", "_").replace("-", "_")
            print(f"  - {model_name}_vaporeon.txt")
    
    # Also save a comparison file
    comparison_file = transcriptions_dir / "comparison_all_models.txt"
    with open(comparison_file, 'w') as f:
        f.write("ASR MODEL COMPARISON - VAPOREON DATASET\n")
        f.write("=" * 60 + "\n\n")
        
        # Load reference
        ref_file = Path("transcriptions/vaporeon_transcript_clean.txt")
        if ref_file.exists():
            with open(ref_file, 'r') as ref:
                reference_text = ref.read().strip()
            f.write("REFERENCE TRANSCRIPTION:\n")
            f.write(reference_text)
            f.write("\n\n" + "=" * 60 + "\n\n")
        
        # Write each model's result
        for i, result in enumerate(sorted(successful_results, key=lambda x: x["wer"]), 1):
            f.write(f"RANK #{i}: {result['model_name']}\n")
            f.write(f"WER: {result['wer']:.2%} | CER: {result['cer']:.2%} | Time: {result['processing_time']:.2f}s\n")
            f.write("-" * 40 + "\n")
            f.write(result['transcription'])
            f.write("\n\n")
    
    print(f"Comparison file saved to: {comparison_file}")


def main():
    """Main leaderboard generation function."""
    print("ASR Model Leaderboard Generator")
    print("Testing models on Vaporeon copypasta dataset...")
    
    # Initialize PostgreSQL storage (detect Docker environment)
    try:
        import os
        
        # Use Docker service name if in container, localhost otherwise
        db_host = os.getenv("DB_HOST", "pgvector" if os.path.exists("/.dockerenv") else "localhost")
        
        storage = PostgreSQLStorage(
            host=db_host,
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "jupyter-dev"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password")
        )
        print(f"Connected to PostgreSQL database at {db_host}")
    except Exception as e:
        print(f"WARNING: Failed to connect to database: {e}")
        print("Continuing without database storage...")
        storage = None
    
    # Create results directory
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    print(f"Results will be saved to: {results_dir.absolute()}/")
    
    # Find audio file
    audio_file = Path("transcriptions/-EWMgB26bmU_Vaporeon_copypasta_animated.mp3")
    if not audio_file.exists():
        print(f"ERROR: Audio file not found: {audio_file}")
        return
    
    # Load reference text
    reference = load_reference_text()
    if not reference:
        return
    
    print(f"Reference text: {len(reference.split())} words, {len(reference)} characters")
    
    # Create experiment record if database available
    if storage:
        experiment_id = storage.create_experiment(
            name=f"Vaporeon ASR Evaluation - {time.strftime('%Y-%m-%d %H:%M:%S')}",
            description="Evaluation of multiple ASR models on Vaporeon copypasta dataset",
            dataset_name="vaporeon_copypasta",
            audio_file=str(audio_file),
            reference_text=reference,
            metadata={
                "audio_duration": 164,
                "reference_word_count": len(reference.split()),
                "reference_char_count": len(reference)
            }
        )
        print(f"Created experiment: {experiment_id}")
    else:
        # Generate a simple experiment ID for file naming
        experiment_id = f"exp_{int(time.time())}"
        print(f"Using local experiment ID: {experiment_id}")
    
    # Define models to test
    models_to_test = [
        # Faster-Whisper models
        ("faster-whisper-tiny", lambda: FasterWhisperAdapter(model_size="tiny")),
        ("faster-whisper-base", lambda: FasterWhisperAdapter(model_size="base")),
        ("faster-whisper-small", lambda: FasterWhisperAdapter(model_size="small")),
        
        # HuggingFace Whisper models via OLMoASR adapter
        ("hf-whisper-tiny", lambda: OLMoASRAdapter(model_name="openai/whisper-tiny")),
        ("hf-whisper-base", lambda: OLMoASRAdapter(model_name="openai/whisper-base")),
        ("hf-whisper-small", lambda: OLMoASRAdapter(model_name="openai/whisper-small")),
    ]
    
    results = []
    
    # Test each model
    for model_name, adapter_factory in models_to_test:
        try:
            adapter = adapter_factory()
            result = test_model(adapter, model_name, str(audio_file), reference, storage, experiment_id)
            results.append(result)
            
            # Print quick status
            if result["status"] == "SUCCESS":
                print(f"  WER: {result['wer']:.2%}, Time: {result['processing_time']:.1f}s")
            else:
                print(f"  FAILED: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            results.append({
                "model_name": model_name,
                "status": "ERROR",
                "error": f"Failed to create adapter: {e}"
            })
            print(f"  ERROR: {e}")
    
    # Generate leaderboard from database if available
    if storage:
        print("\nGenerating leaderboard from database...")
        db_leaderboard = storage.get_leaderboard(dataset_name="vaporeon_copypasta")
        
        if db_leaderboard:
            print_database_leaderboard(db_leaderboard)
        else:
            print("No historical data found in database")
    else:
        print("\nDatabase not available - showing current run results only")
    
    # Also print current run results
    print("\nCurrent Run Results:")
    print_leaderboard(results)
    
    # Save detailed results
    save_results(results)
    
    # Print database stats if available
    if storage:
        stats = storage.get_dataset_stats("vaporeon_copypasta")
        if stats:
            print(f"\nDataset Statistics:")
            print(f"- Total evaluations: {stats.get('total_evaluations', 0)}")
            print(f"- Unique models: {stats.get('unique_models', 0)}")
            print(f"- Average WER: {stats.get('avg_wer', 0):.2%}")
            print(f"- Best WER: {stats.get('best_wer', 0):.2%}")
        
        storage.close()
    print(f"\nLeaderboard generation completed!")


if __name__ == "__main__":
    main()