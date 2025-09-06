#!/usr/bin/env python3
"""
Convert dataset to AI Toolkit format
Creates individual .txt files for each image as expected by AI Toolkit
"""

import json
from pathlib import Path

def main():
    dataset_dir = Path("dataset")
    train_dir = dataset_dir / "train"
    captions_file = dataset_dir / "captions.jsonl"
    
    if not captions_file.exists():
        print("Error: captions.jsonl not found")
        return
    
    print("Converting to AI Toolkit format (1:1 image to txt files)...")
    
    # Read captions
    captions = []
    with open(captions_file, 'r') as f:
        for line in f:
            captions.append(json.loads(line.strip()))
    
    print(f"Processing {len(captions)} caption entries...")
    
    # Create individual .txt files for each image
    created_count = 0
    for entry in captions:
        image_name = entry['file_name']
        caption_text = entry['text']
        
        # Get the base name without extension
        image_path = train_dir / image_name
        if not image_path.exists():
            print(f"Warning: Image not found: {image_name}")
            continue
            
        # Create corresponding .txt file
        txt_name = image_path.stem + '.txt'
        txt_path = train_dir / txt_name
        
        with open(txt_path, 'w') as f:
            f.write(caption_text)
        
        print(f"Created: {txt_name}")
        created_count += 1
    
    print(f"Created {created_count} caption files")
    print(f"Dataset ready for AI Toolkit at: {train_dir.absolute()}")
    print("You can now drag the train/ folder into AI Toolkit")

if __name__ == "__main__":
    main()