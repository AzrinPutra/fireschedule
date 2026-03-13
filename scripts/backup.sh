#!/bin/bash

# FireSchedule Git Backup Script
# This script guides you through backing up your FireSchedule data with git
# Designed for learning - explains each command as it runs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=============================================="
echo "  🔥 FireSchedule Git Backup Script"
echo "=============================================="
echo ""
echo "This script will guide you through backing up"
echo "your FireSchedule data using git."
echo ""

# Check if we're in a git repository
echo "STEP 1: Check git status"
echo "----------------------------"
echo "Command: git status"
echo ""
echo "Explanation: This shows which files have been modified"
echo "and whether this is a git repository."
echo ""

cd "$PROJECT_DIR"
git status

echo ""
echo "STEP 2: Check git log"
echo "----------------------------"
echo "Command: git log --oneline -5"
echo ""
echo "Explanation: Shows your recent commits to understand"
echo "the commit history."
echo ""

git log --oneline -5

echo ""
echo "STEP 3: Add files to staging"
echo "----------------------------"
echo "Command: git add ."
echo ""
echo "Explanation: This stages ALL changes for commit."
echo "The dot (.) means 'all files in current directory'."
echo "Alternatively, you can add specific files:"
echo "  git add src/          # Add only source files"
echo "  git add config.yaml   # Add only config"
echo ""

read -p "Press Enter to continue..."
git add .

echo ""
echo "Files staged:"
git diff --cached --name-only | head -20

echo ""
echo "STEP 4: Review changes"
echo "----------------------------"
echo "Command: git diff --cached"
echo ""
echo "Explanation: This shows exactly what will be committed."
echo "Review this to make sure you're not committing anything"
echo "sensitive (like passwords or API keys)."
echo ""

read -p "Press Enter to see the diff..."
git diff --cached

echo ""
echo "STEP 5: Commit changes"
echo "----------------------------"
echo "Command: git commit -m 'Your message here'"
echo ""
echo "Explanation: This saves your staged changes to the"
echo "local git history with a descriptive message."
echo ""

echo "Enter a commit message (or press Enter for default):"
read COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Update FireSchedule - $(date '+%Y-%m-%d %H:%M')"
fi

git commit -m "$COMMIT_MSG"

echo ""
echo "STEP 6: View commit"
echo "----------------------------"
echo "Command: git log --oneline -1"
echo ""
echo "Explanation: Verify your commit was created."
echo ""

git log --oneline -1

echo ""
echo "=============================================="
echo "  ✅ Local backup complete!"
echo "=============================================="
echo ""
echo "To push to GitHub, run:"
echo ""
echo "  git push origin main"
echo ""
echo "Or if you're on a different branch:"
echo "  git push origin <your-branch-name>"
echo ""
echo "To learn more about the commands used:"
echo "  git status --help"
echo "  git add --help"
echo "  git commit --help"
echo ""
