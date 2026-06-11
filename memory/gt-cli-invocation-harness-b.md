# gt CLI Invocation — Harness B (Claude Code, Windows)

author_identity: prime-builder
author_harness_id: B
author_session_context_id: B-2026-06-10T16-32-39Z
author_model: claude-fable-5
author_model_version: 5
author_model_configuration: interactive default

Operational pattern captured at S428 wrap (2026-06-10). Saves re-deriving interpreter resolution each session.

- `gt.exe` is NOT in `E:\GT-KB\.venv\Scripts`, and that venv lacks `click`/`groundtruth_kb`. Do not use `E:\GT-KB\.venv\Scripts\python.exe` for gt work.
- The plain PATH `python` carries the editable install (`E:\GT-KB\groundtruth-kb\src\groundtruth_kb`).
- **Invoke gt:** `python -c "import sys; sys.argv[0]='gt'; from groundtruth_kb.cli import main; main()" <subcommand> <args>`
- **Canonical `::wrap` service:** `... session wrap --harness-name claude --harness-id B` — harness flags are required (defaults to `codex`). Output: envelope archived at `harness-state/claude/session-envelope-archive/<ts>-session-envelope.json` with 5 `wrap_step_results` (finalize, DA harvest, git-status attestation, topic auto-close, archive). The git attestation is a useful end-of-session dirty-state snapshot.
- **Backlog capture:** `... backlog add --title ... --origin {new|hygiene|improvement|defect|regression} --component ... --change-reason ...` (+ optional `--priority`, `--description`, `--related-bridge-threads`). Governed candidate capture; attribution auto-resolved fail-closed (no `--changed-by` exists).
- Note: harness auto-memory writes to `C:\Users\micha\.claude\projects\E--GT-KB\memory\` are hook-blocked (root boundary). Durable operational notes belong here in `E:\GT-KB\memory\`.
