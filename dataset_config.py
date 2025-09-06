"""
Dataset Configuration
Update these settings for your specific dataset
"""

# Dataset Configuration
DATASET_CONFIG = {
    "name": "my-image-dataset",
    "hf_username": "your-username",  # Replace with your HF username
    "description": "A computer vision dataset for multiple tasks",
    "task_type": "multi-task",  # Options: "classification", "captioning", "detection", "multi-task"
    "private": False,  # Set to True for private repository
    "license": "apache-2.0",
    "language": "en"
}

# Supported task configurations
TASK_CONFIGS = {
    "classification": {
        "metadata_format": "csv",
        "required_columns": ["file_name", "label"],
        "folder_structure": "class_folders"  # Images organized in class subfolders
    },
    "captioning": {
        "metadata_format": "jsonl", 
        "required_columns": ["file_name", "text"],
        "folder_structure": "flat"  # All images in same folder with metadata
    },
    "detection": {
        "metadata_format": "jsonl",
        "required_columns": ["file_name", "objects"],
        "folder_structure": "flat"
    },
    "multi-task": {
        "metadata_format": "jsonl",
        "required_columns": ["file_name"],  # Additional columns as needed
        "folder_structure": "flexible"
    }
}

# Directory structure
DATASET_STRUCTURE = {
    "base_dir": "dataset",
    "splits": ["train", "validation", "test"],
    "metadata_dir": "metadata",
    "docs_dir": "docs"
}