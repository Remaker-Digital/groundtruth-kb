---
name: No Hardcoded Paths In GT-KB
description: GT-KB code must not embed machine-local absolute paths in active operational code, scripts, hooks, skills, MCP config, or portable docs. Use relative/discovered/configured paths; env vars only for genuinely external dependencies.
type: feedback
originSessionId: 2c8e1d6f-cf03-4ec2-a4a8-6d3ff5a453da
---
There should be no hardcoded paths in GT-KB. Use relative paths; when an absolute path is genuinely required, retrieve it from local environment variables or configuration.

**Why:** Owner directive S307 (2026-04-24), reinforced by Codex hardcoded-path directive (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-24-20-35-HARDCODED-PATH-DIRECTIVE.md`). GT-KB ships as an adopter-installable platform; literal paths like `E:\Claude-Playground\...` or even `E:\GT-KB\...` make GT-KB fragile or non-functional on another workstation or after pip install. Codex applies this as a hard review gate going forward.

**How to apply:**

5-category classification for every path literal encountered:

1. **Active operational path dependency** — release-quality blocker. Refactor with `Path(__file__).resolve()`, `subprocess.run(["git","rev-parse","--show-toplevel"], ...)`, `(Resolve-Path (Join-Path $PSScriptRoot "..\.."))` (PowerShell), `path.resolve(__dirname, ...)` (JS), or env var. **Do not substitute one literal for another.**
2. **Local-only configuration** — `.local.*` files; either untrack-and-gitignore or accept tracked-but-machine-coupled (owner choice per file).
3. **External dependency path** — supply via env var with discovered default. Example: `GROUNDTRUTH_KB_PATH` for sibling-repo references.
4. **Historical evidence / log / archive** — leave untouched; exclude from migration verifier.
5. **Documentation example** — placeholder like `<project-root>` is preferred for portable docs/wikis; labeled-current-example acceptable for session-dated artifacts.

**Migration tool note:** `scripts/migrate_root_to_gtkb.py` (literal find/replace) is appropriate ONLY for Cat 4 and Cat 5 surfaces. For Cat 1 active operational files, never run `--execute`; do per-file refactors.

**Migration script self-protection:** the script must exclude itself from its own walk (its `REPLACEMENTS` table contains target literals as data). The matcher rewrite at `-003`/`-005` is what makes self-exclusion plus `**` recursion work; do not regress.

**Anti-patterns to reject:**
- "Run `--execute` to fix the migration." → No, only fixes Cat 4/5; Cat 1 needs refactor.
- "Replace `E:\Claude-Playground` with `E:\GT-KB`." → No, that preserves the workstation-coupling defect.
- "Use a config file with a hardcoded `project_root` value." → No, that re-introduces the literal in a different file. Use discovery (`git rev-parse`, `Path(__file__)`).
