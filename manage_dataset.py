#!/usr/bin/env python3
"""
Dataset Management CLI
Simple command-line interface for managing your image dataset
"""

import argparse
import os
from pathlib import Path
from dataset_config import DATASET_CONFIG
from setup_dataset import DatasetManager
from dataset_utils import (
    authenticate_hf, 
    validate_dataset_structure, 
    push_to_hub, 
    create_version_tag,
    update_dataset_card
)

def setup_command(args):
    """Setup new dataset structure and HF repository"""
    
    dataset_name = args.name or DATASET_CONFIG["name"]
    username = args.username or DATASET_CONFIG["hf_username"]
    
    if username == "your-username":
        print("Please update your HF username in dataset_config.py or use --username flag")
        return
    
    manager = DatasetManager(dataset_name, username)
    manager.setup_complete_dataset(private=args.private)

def validate_command(args):
    """Validate dataset structure"""
    
    dataset_path = args.path or "dataset"
    validation = validate_dataset_structure(dataset_path)
    
    print("Dataset Validation Results:")
    print("-" * 30)
    
    if validation["valid"]:
        print("✓ Dataset structure is valid")
        print(f"  Splits found: {validation['splits']}")
        print(f"  Total images: {validation['total_images']}")
        print(f"  Structure type: {validation['structure_type']}")
        print(f"  Metadata files: {len(validation['metadata_files'])}")
        
        if validation['metadata_files']:
            print("  Metadata files found:")
            for meta_file in validation['metadata_files']:
                print(f"    - {meta_file}")
    else:
        print(f"✗ Validation failed: {validation.get('error')}")

def push_command(args):
    """Push dataset to Hugging Face Hub"""
    
    dataset_path = args.path or "dataset"
    
    # Get repo_id
    if args.repo_id:
        repo_id = args.repo_id
    else:
        username = args.username or DATASET_CONFIG["hf_username"]
        dataset_name = args.name or DATASET_CONFIG["name"]
        
        if username == "your-username":
            print("Please specify --repo-id or update dataset_config.py")
            return
            
        repo_id = f"{username}/{dataset_name}"
    
    print(f"Pushing dataset to: {repo_id}")
    
    # Validate first
    validation = validate_dataset_structure(dataset_path)
    if not validation["valid"]:
        print(f"Dataset validation failed: {validation.get('error')}")
        return
    
    # Update dataset card with stats
    update_dataset_card(dataset_path, validation)
    
    # Push to hub
    success = push_to_hub(dataset_path, repo_id, private=args.private)
    
    if success and args.tag:
        create_version_tag(repo_id, args.tag, args.message or f"Version {args.tag}")

def status_command(args):
    """Show dataset status and statistics"""
    
    dataset_path = args.path or "dataset"
    
    print("Dataset Status")
    print("=" * 40)
    
    # Check if dataset exists
    if not Path(dataset_path).exists():
        print(f"Dataset directory '{dataset_path}' does not exist")
        print("Run 'python manage_dataset.py setup' to create it")
        return
    
    # Validate and show stats
    validation = validate_dataset_structure(dataset_path)
    
    print(f"Path: {Path(dataset_path).absolute()}")
    print(f"Valid: {'Yes' if validation['valid'] else 'No'}")
    
    if validation["valid"]:
        print(f"Splits: {', '.join(validation['splits']) if validation['splits'] else 'None'}")
        print(f"Total Images: {validation['total_images']}")
        print(f"Structure: {validation['structure_type']}")
        print(f"Metadata Files: {len(validation['metadata_files'])}")
        
        # Show split breakdown
        if validation['splits']:
            print("\nSplit Details:")
            for split in validation['splits']:
                split_path = Path(dataset_path) / split
                image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
                image_count = sum(1 for f in split_path.rglob("*") if f.suffix.lower() in image_extensions)
                print(f"  {split}: {image_count} images")
    else:
        print(f"Error: {validation.get('error')}")

def main():
    parser = argparse.ArgumentParser(description="Manage your image dataset")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup new dataset structure")
    setup_parser.add_argument("--name", help="Dataset name")
    setup_parser.add_argument("--username", help="HuggingFace username")
    setup_parser.add_argument("--private", action="store_true", help="Create private repository")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate dataset structure")
    validate_parser.add_argument("--path", default="dataset", help="Dataset path")
    
    # Push command
    push_parser = subparsers.add_parser("push", help="Push dataset to HuggingFace Hub")
    push_parser.add_argument("--path", default="dataset", help="Dataset path")
    push_parser.add_argument("--repo-id", help="Repository ID (username/dataset-name)")
    push_parser.add_argument("--username", help="HuggingFace username")
    push_parser.add_argument("--name", help="Dataset name")
    push_parser.add_argument("--private", action="store_true", help="Push to private repository")
    push_parser.add_argument("--tag", help="Create version tag")
    push_parser.add_argument("--message", help="Tag message")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show dataset status")
    status_parser.add_argument("--path", default="dataset", help="Dataset path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load environment variables
    if Path(".env").exists():
        from dotenv import load_dotenv
        load_dotenv()
    
    # Execute command
    if args.command == "setup":
        setup_command(args)
    elif args.command == "validate":
        validate_command(args)
    elif args.command == "push":
        push_command(args)
    elif args.command == "status":
        status_command(args)

if __name__ == "__main__":
    main()