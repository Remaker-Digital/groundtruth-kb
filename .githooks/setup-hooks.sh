#!/usr/bin/env bash
# Activates the .githooks/ directory as Git's local hook path.
# Run once per developer after cloning or when hooks are added.
#
# Usage:
#   bash .githooks/setup-hooks.sh
#
# What it does:
#   git config core.hooksPath .githooks
#
# This configures Git to look for hooks in .githooks/ instead of the default
# .git/hooks/. The setting is stored in .git/config (local, not committed),
# so every developer must run this once on their machine.
#
# Hooks activated:
#   pre-commit - redacted staged secret scan and PowerShell AST syntax check
#   pre-push - redacted secret range scan for refs about to be pushed
#
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

set -e

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "ERROR: Not inside a Git repository." >&2
    exit 1
}

cd "$REPO_ROOT"

git config core.hooksPath .githooks
chmod +x .githooks/pre-commit 2>/dev/null || true
chmod +x .githooks/pre-push 2>/dev/null || true

echo "Git hooks activated: core.hooksPath = .githooks"
echo "Active hooks:"
echo "  pre-commit - redacted staged secret scan and PowerShell syntax validation for staged .ps1 files"
echo "  pre-push - redacted secret range scan for refs about to be pushed"
