# Agent Control Baseline

Purpose: tracked, sanitized reference for local agent-control configuration used in this project.

## Why This Exists

The live `.claude/` directory is machine-local and git-ignored. This folder provides a portable baseline for:

- intended operating modes
- review-mode setup
- expected local control surfaces
- drift checks between tracked intent and local configuration

## Contents

- `REVIEW-MODE-SETUP.md` - how to run review sessions with non-mutating defaults
- `CONTROL-MAP.md` - tracked mapping of startup docs, rules, hooks, memory, and skills

## Boundary

- Do not put secrets in this folder.
- Do not treat these files as the live local configuration.
- Use them as the auditable source of intent for local setup.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
