"""
Dataset Utilities for Loading and Pushing to Hugging Face Hub
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datasets import Dataset, DatasetDict, load_dataset, Image
from huggingface_hub import login
import pandas as pd

def authenticate_hf():
    """Authenticate with Hugging Face using token from environment"""
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("Please set HF_TOKEN in your .env file")
        return False
    
    try:
        login(token=hf_token)
        print("✓ Successfully authenticated with Hugging Face")
        return True
    except Exception as e:
        print(f"Authentication failed: {e}")
        return False

def load_local_dataset(data_dir: str = "dataset", task_type: str = "imagefolder") -> DatasetDict:
    """Load dataset from local directory structure"""
    
    try:
        if task_type == "imagefolder":
            # Load using ImageFolder format
            dataset = load_dataset("imagefolder", data_dir=data_dir)
        elif task_type == "webdataset":
            # Load using WebDataset format  
            dataset = load_dataset("webdataset", data_dir=data_dir)
        else:
            raise ValueError(f"Unsupported task_type: {task_type}")
            
        print(f"✓ Loaded dataset from {data_dir}")
        print(f"Dataset info: {dataset}")
        return dataset
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

def validate_dataset_structure(dataset_path: str) -> Dict[str, Any]:
    """Validate dataset structure and return summary"""
    
    path = Path(dataset_path)
    if not path.exists():
        return {"valid": False, "error": "Dataset path does not exist"}
    
    summary = {
        "valid": True,
        "splits": [],
        "total_images": 0,
        "metadata_files": [],
        "structure_type": None
    }
    
    # Check for split directories
    for split in ["train", "validation", "test"]:
        split_path = path / split
        if split_path.exists():
            summary["splits"].append(split)
            
            # Count images in split
            image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
            image_count = sum(1 for f in split_path.rglob("*") if f.suffix.lower() in image_extensions)
            summary["total_images"] += image_count
            
            # Check for metadata files
            for meta_file in ["metadata.csv", "metadata.jsonl", "metadata.parquet"]:
                meta_path = split_path / meta_file
                if meta_path.exists():
                    summary["metadata_files"].append(str(meta_path))
    
    # Determine structure type
    if any((path / split).exists() for split in ["train", "validation", "test"]):
        summary["structure_type"] = "split_folders"
    else:
        summary["structure_type"] = "single_folder"
    
    return summary

def push_to_hub(dataset_path: str, repo_id: str, private: bool = False) -> bool:
    """Push dataset to Hugging Face Hub with proper versioning"""
    
    if not authenticate_hf():
        return False
    
    try:
        # Validate dataset structure
        validation = validate_dataset_structure(dataset_path)
        if not validation["valid"]:
            print(f"Dataset validation failed: {validation.get('error')}")
            return False
        
        print(f"Dataset validation passed:")
        print(f"  - Splits: {validation['splits']}")
        print(f"  - Total images: {validation['total_images']}")
        print(f"  - Structure: {validation['structure_type']}")
        
        # Load dataset
        dataset = load_local_dataset(dataset_path)
        if dataset is None:
            return False
        
        # Push to hub
        print(f"Pushing dataset to {repo_id}...")
        dataset.push_to_hub(repo_id, private=private)
        
        print(f"✓ Successfully pushed dataset to https://huggingface.co/datasets/{repo_id}")
        return True
        
    except Exception as e:
        print(f"Error pushing to hub: {e}")
        return False

def create_version_tag(repo_id: str, version: str, message: str = ""):
    """Create a version tag for dataset tracking"""
    from huggingface_hub import HfApi
    
    api = HfApi()
    try:
        # Create a tag for versioning
        api.create_tag(
            repo_id=repo_id,
            repo_type="dataset", 
            tag=version,
            tag_message=message or f"Dataset version {version}"
        )
        print(f"✓ Created version tag: {version}")
        return True
    except Exception as e:
        print(f"Error creating version tag: {e}")
        return False

def update_dataset_card(dataset_path: str, stats: Dict[str, Any]):
    """Update dataset card with current statistics"""
    
    readme_path = Path(dataset_path) / "README.md"
    if not readme_path.exists():
        print("README.md not found, skipping update")
        return
    
    # Read current content
    with open(readme_path, "r") as f:
        content = f.read()
    
    # Update statistics section
    stats_section = f"""
## Dataset Statistics

- **Total Images:** {stats.get('total_images', 0)}
- **Splits:** {', '.join(stats.get('splits', []))}
- **Structure Type:** {stats.get('structure_type', 'unknown')}
- **Last Updated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # Insert or replace statistics section
    if "## Dataset Statistics" in content:
        # Replace existing section
        lines = content.split('\n')
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if line.strip() == "## Dataset Statistics":
                start_idx = i
            elif start_idx is not None and line.startswith("## ") and i > start_idx:
                end_idx = i
                break
        
        if start_idx is not None:
            if end_idx is None:
                end_idx = len(lines)
            lines[start_idx:end_idx] = stats_section.strip().split('\n')
            content = '\n'.join(lines)
    else:
        # Add new section before "Additional Information"
        if "## Additional Information" in content:
            content = content.replace("## Additional Information", stats_section + "\n## Additional Information")
        else:
            content += stats_section
    
    # Write updated content
    with open(readme_path, "w") as f:
        f.write(content)
    
    print("✓ Updated dataset card with current statistics")

if __name__ == "__main__":
    # Example usage
    dataset_path = "dataset"
    repo_id = f"{os.getenv('HF_USERNAME', 'your-username')}/{os.getenv('DATASET_NAME', 'my-dataset')}"
    
    print("Dataset Utilities")
    print("-" * 30)
    
    # Validate dataset
    validation = validate_dataset_structure(dataset_path)
    print("Validation results:", validation)
    
    # Update dataset card
    if validation["valid"]:
        update_dataset_card(dataset_path, validation)