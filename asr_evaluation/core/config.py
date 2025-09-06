"""
Configuration management for ASR evaluation system.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import os
from pathlib import Path


@dataclass
class EvaluationConfig:
    """Configuration for evaluation runs."""
    
    # Model settings
    model_name: str = "faster-whisper"
    model_size: str = "base"
    
    # Evaluation settings
    batch_size: int = 1
    timeout_seconds: int = 300
    retry_attempts: int = 3
    
    # Output settings
    output_dir: str = "results"
    save_transcriptions: bool = True
    save_detailed_results: bool = True
    
    # Audio processing
    supported_formats: List[str] = field(default_factory=lambda: [".mp3", ".wav", ".m4a", ".webm"])
    max_audio_length: int = 3600  # seconds
    
    # Custom parameters
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatasetConfig:
    """Configuration for evaluation datasets."""
    
    name: str
    path: str
    reference_format: str = "json"  # "json", "txt", "csv"
    audio_dir: Optional[str] = None
    
    # Validation settings
    validate_audio: bool = True
    validate_references: bool = True


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "evaluation_config.json"
        self.evaluation_config = EvaluationConfig()
        self.datasets: Dict[str, DatasetConfig] = {}
    
    def load_config(self) -> EvaluationConfig:
        """Load configuration from file or return defaults."""
        if os.path.exists(self.config_path):
            # TODO: Implement JSON loading in future task
            pass
        return self.evaluation_config
    
    def add_dataset(self, name: str, path: str, **kwargs) -> None:
        """Add a dataset configuration."""
        self.datasets[name] = DatasetConfig(name=name, path=path, **kwargs)
    
    def get_dataset(self, name: str) -> Optional[DatasetConfig]:
        """Get dataset configuration by name."""
        return self.datasets.get(name)
    
    def list_datasets(self) -> List[str]:
        """List all configured dataset names."""
        return list(self.datasets.keys())