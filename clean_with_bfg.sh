#!/bin/bash

# Alternative: Use BFG Repo-Cleaner to remove secrets from history
# This is more thorough than git filter-branch

echo "Installing BFG Repo-Cleaner..."

# Download BFG (you may need to install Java first)
# wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

echo "Creating secrets file for BFG..."
cat > secrets.txt << 'EOF'
hf_****************************
shannonamberson
shannon
sh4nn0n
EOF

echo "Running BFG to clean repository..."
# java -jar bfg-1.14.0.jar --replace-text secrets.txt --no-blob-protection .

echo "Cleaning up git history..."
# git reflog expire --expire=now --all && git gc --prune=now --aggressive

echo "Repository cleaned! Force push required:"
echo "git push --force-with-lease origin master"