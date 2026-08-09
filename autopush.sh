#!/bin/bash
# Auto-commits and pushes dashboard changes.
# Triggered by launchd whenever data.json is modified.

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

REPO="$HOME/Desktop/MFL"
LOG="$REPO/autopush.log"

stamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

cd "$REPO" 2>/dev/null || {
  echo "$(stamp)  FAIL  cannot cd to $REPO" >> "$LOG"
  exit 1
}

# Confirm git is reachable (launchd has a minimal PATH)
if ! command -v git >/dev/null 2>&1; then
  echo "$(stamp)  FAIL  git not found on PATH" >> "$LOG"
  exit 1
fi

# Confirm we can actually read the repo (TCC on ~/Desktop can deny this)
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "$(stamp)  FAIL  not a git repo, or read denied by macOS privacy protection" >> "$LOG"
  exit 1
fi

# Nothing changed? Exit quietly.
if [ -z "$(git status --porcelain -- data.json index.html)" ]; then
  exit 0
fi

git add -- data.json index.html 2>>"$LOG"

if ! git commit -m "Auto-sync dashboard $(stamp)" >>"$LOG" 2>&1; then
  echo "$(stamp)  FAIL  commit failed" >> "$LOG"
  exit 1
fi

if git push >>"$LOG" 2>&1; then
  echo "$(stamp)  OK    pushed" >> "$LOG"
else
  echo "$(stamp)  FAIL  push rejected — check credentials with: gh auth status" >> "$LOG"
  exit 1
fi
