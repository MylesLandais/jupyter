#!/usr/bin/env python3
"""
Dataset Setup and HF Repository Initialization Script
This script helps format your dataset and initialize a Hugging Face repository for version tracking.
"""

import os
import json
from pathlib import Path
from datasets import Dataset, DatasetDict, load_dataset
from huggingface_hub import HfApi, create_repo, login
import pandas as pd

class DatasetManager:
    def __init__(self, dataset_name: str, hf_username: str):
        self.dataset_name = dataset_name
        self.hf_username = hf_username
        self.repo_id = f"{hf_username}/{dataset_name}"
        self.local_path = Path("./dataset")
        self.api = HfApi()
        
    def create_local_structure(self):
        """Create the recommended ImageFolder structure"""
        print("Creating local dataset structure...")
        
        # Create main directories
        dirs = [
            "dataset/train",
            "dataset/validation", 
            "dataset/test",
            "dataset/metadata"
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            
        print(f"✓ Created directory structure at {self.local_path}")
        
    def create_metadata_template(self):
        """Create metadata file templates for different CV tasks"""
        
        # Image classification metadata template
        classification_csv = """file_name,label,split
sample_001.jpg,cat,train
sample_002.jpg,dog,train
sample_003.jpg,cat,validation
"""
        
        # Image captioning metadata template  
        captioning_jsonl = """{"file_name": "sample_001.jpg", "text": "A cat sitting on a windowsill", "split": "train"}
{"file_name": "sample_002.jpg", "text": "A golden retriever playing in the park", "split": "train"}
{"file_name": "sample_003.jpg", "text": "A tabby cat sleeping on a couch", "split": "validation"}
"""
        
        # Object detection metadata template
        detection_jsonl = """{"file_name": "sample_001.jpg", "objects": {"bbox": [[100, 50, 200, 150]], "categories": [0]}, "split": "train"}
{"file_name": "sample_002.jpg", "objects": {"bbox": [[50, 30, 180, 120], [200, 100, 300, 200]], "categories": [1, 0]}, "split": "train"}
"""
        
        # Write templates
        with open("dataset/metadata/classification_template.csv", "w") as f:
            f.write(classification_csv)
            
        with open("dataset/metadata/captioning_template.jsonl", "w") as f:
            f.write(captioning_jsonl)
            
        with open("dataset/metadata/detection_template.jsonl", "w") as f:
            f.write(detection_jsonl)
            
        print("✓ Created metadata templates in dataset/metadata/")
        
    def create_dataset_card(self):
        """Create a comprehensive dataset card (README.md)"""
        
        card_content = f"""---
license: apache-2.0
task_categories:
- image-classification
- image-captioning
- object-detection
language:
- en
tags:
- computer-vision
- image-dataset
size_categories:
- 1K<n<10K
---

# {self.dataset_name}

## Dataset Description

This dataset contains images for computer vision tasks including classification, captioning, and object detection.

### Dataset Summary

- **Repository:** {self.repo_id}
- **Task:** Multiple CV tasks supported
- **Language:** English
- **License:** Apache 2.0

## Dataset Structure

### Data Instances

The dataset follows the ImageFolder structure with metadata files for different tasks:

```
dataset/
├── train/
│   ├── class1/
│   ├── class2/
│   └── metadata.csv
├── validation/
│   ├── class1/
│   ├── class2/
│   └── metadata.csv
└── test/
    ├── class1/
    ├── class2/
    └── metadata.csv
```

### Data Fields

#### Image Classification
- `image`: PIL Image
- `label`: Classification label
- `file_name`: Original filename

#### Image Captioning  
- `image`: PIL Image
- `text`: Caption text
- `file_name`: Original filename

#### Object Detection
- `image`: PIL Image
- `objects`: Dictionary with `bbox` and `categories`
- `file_name`: Original filename

## Dataset Creation

### Source Data

[Describe your data sources here]

### Data Collection and Processing

[Describe how the data was collected and processed]

## Considerations for Using the Data

### Social Impact of Dataset

[Discuss potential social impacts]

### Discussion of Biases

[Discuss potential biases in the dataset]

## Additional Information

### Dataset Curators

[Your name/organization]

### Licensing Information

Apache 2.0 License

### Citation Information

```
@dataset{{{self.dataset_name},
  title={{{self.dataset_name}}},
  author={{{self.hf_username}}},
  year={{2025}},
  url={{https://huggingface.co/datasets/{self.repo_id}}}
}}
```
"""
        
        with open("dataset/README.md", "w") as f:
            f.write(card_content)
            
        print("✓ Created dataset card (README.md)")
        
    def create_gitattributes(self):
        """Create .gitattributes for proper LFS handling"""
        
        gitattributes_content = """*.jpg filter=lfs diff=lfs merge=lfs -text
*.jpeg filter=lfs diff=lfs merge=lfs -text
*.png filter=lfs diff=lfs merge=lfs -text
*.gif filter=lfs diff=lfs merge=lfs -text
*.bmp filter=lfs diff=lfs merge=lfs -text
*.tiff filter=lfs diff=lfs merge=lfs -text
*.webp filter=lfs diff=lfs merge=lfs -text
*.zip filter=lfs diff=lfs merge=lfs -text
*.tar filter=lfs diff=lfs merge=lfs -text
*.tar.gz filter=lfs diff=lfs merge=lfs -text
"""
        
        with open("dataset/.gitattributes", "w") as f:
            f.write(gitattributes_content)
            
        print("✓ Created .gitattributes for LFS")
        
    def initialize_hf_repo(self, private: bool = False):
        """Initialize Hugging Face repository"""
        
        try:
            # Create repository
            create_repo(
                repo_id=self.repo_id,
                repo_type="dataset",
                private=private,
                exist_ok=True
            )
            print(f"✓ Created HF repository: {self.repo_id}")
            
        except Exception as e:
            print(f"Error creating repository: {e}")
            
    def setup_complete_dataset(self, private: bool = False):
        """Run complete dataset setup"""
        
        print(f"Setting up dataset: {self.dataset_name}")
        print(f"HF Repository: {self.repo_id}")
        print("-" * 50)
        
        # Create local structure
        self.create_local_structure()
        
        # Create metadata templates
        self.create_metadata_template()
        
        # Create dataset card
        self.create_dataset_card()
        
        # Create gitattributes
        self.create_gitattributes()
        
        # Initialize HF repo
        self.initialize_hf_repo(private=private)
        
        print("-" * 50)
        print("✓ Dataset setup complete!")
        print(f"\nNext steps:")
        print(f"1. Add your images to dataset/train/, dataset/validation/, dataset/test/")
        print(f"2. Update metadata files in dataset/metadata/ or create new ones in split folders")
        print(f"3. Update the README.md with your specific dataset information")
        print(f"4. Push to HF Hub using: dataset.push_to_hub('{self.repo_id}')")


if __name__ == "__main__":
    # Configuration - Update these values
    DATASET_NAME = "my-image-dataset"  # Change this to your dataset name
    HF_USERNAME = "your-username"      # Change this to your HF username
    PRIVATE_REPO = False               # Set to True for private repository
    
    # Initialize dataset manager
    manager = DatasetManager(DATASET_NAME, HF_USERNAME)
    
    # Run setup
    manager.setup_complete_dataset(private=PRIVATE_REPO)