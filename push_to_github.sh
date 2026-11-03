#!/usr/bin/env bash
# One-time push of this project to https://github.com/cybersmeashish/sovereign-AI
set -euo pipefail
cd "$(dirname "$0")"
REMOTE="https://github.com/cybersmeashish/sovereign-AI.git"

command -v git >/dev/null || { echo "git not found - run: xcode-select --install"; exit 1; }

if [ ! -d .git ]; then
  git init -b main
fi
git add -A
git -c user.name="${GIT_AUTHOR_NAME:-Ashish Srivastava}" \
    -c user.email="${GIT_AUTHOR_EMAIL:-$(git config user.email || echo cybersmeashish@users.noreply.github.com)}" \
    commit -m "Sovereign AI Stack: blueprint, reference control plane, policies, infra and CI" || echo "nothing new to commit"
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"

# If the remote already has commits (e.g. a README created on GitHub), integrate them first.
if git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
  git pull --rebase -X theirs origin main --allow-unrelated-histories || true
fi
git push -u origin main
echo "Pushed to $REMOTE"
