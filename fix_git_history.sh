#!/bin/bash

# Script to create a clean git history without secrets

echo "Creating clean git repository..."

# Create a backup of current state
cp -r .git .git.backup

# Remove git history completely
rm -rf .git

# Initialize fresh repository
git init

# Add all current clean files
git add .

# Create initial clean commit
git commit -m "Initial commit: ASR Model Evaluation System

- Complete ASR evaluation framework with OLMoASR and FasterWhisper adapters
- Leaderboard generation system with PostgreSQL integration
- Docker development environment with CUDA support
- Comprehensive test suite and documentation
- Secret scanning and cleanup tools"

# Add remote (you'll need to update this with your repo URL)
git remote add origin https://github.com/MylesLandais/jupyter.git

echo "Clean repository created!"
echo "Next steps:"
echo "1. Force push to overwrite remote history: git push -f origin master"
echo "2. Or create a new repository and push there"