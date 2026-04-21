# Session Wrap-Up — Repeatable Procedure

> **Type:** Operational Procedure
> **Trigger:** End of every working session (keyword: "wrap up", "done", "end session")
> **Executor:** Claude (automated via Session Scheduler)
> **Gate:** All steps must complete; failures are logged but do not block

---

## Variables

| Variable | Value |
|----------|-------|
| `SESSION_ID` | Current session identifier (e.g., S97) |
| `KNOWLEDGE_DB` | `groundtruth.db` |
| `MEMORY_FILE` | `memory/MEMORY.md` |
| `CLAUDE_MD` | `CLAUDE.md` |
| `SCHEDULE_FILE` | `.claude/SCHEDULE.md` |
| `DOCS_SITE` | `docs-site/` (agentredcx.com) |
| `GITHUB_REPO` | `https://github.com/Remaker-Digital/agent-red-customer-engagement` |
| `GITHUB_PROJECT` | `https://github.com/users/mike-remakerdigital/projects/1` |
| `GITHUB_WIKI` | `https://github.com/Remaker-Digital/agent-red-customer-engagement/wiki` |
| `STAGING_ENV` | `agent-red-staging` Container App |

---

## Phase 1 — Knowledge & Memory Updates

### Step 1.1: Update Knowledge Database

**If** any specifications were implemented, verified, or corrected during this session:

```python
import sys; sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB
db = KnowledgeDB()
db.update_spec("<id>", changed_by="claude", change_reason="<SESSION_ID>: <reason>", status="<new_status>")
db.close()
```

**Verification:** Run assertions and confirm no regressions:
```
python tools/knowledge-db/assertions.py
```

### Step 1.2: Update MEMORY.md

Update three sections of `memory/MEMORY.md`:

1. **Current Status** — Refresh production version, test counts, release plan step, and any changed status fields.
2. **Recent Sessions** — Add a one-line entry for this session: `- S<N>: <key outcomes>`.
3. **Quick Reference** — Update any changed values (version, API keys, image tags, test counts, etc.).

**Rule:** Keep MEMORY.md under 250 lines. If approaching the limit, archive the oldest "Recent Sessions" entries to `CLAUDE_ARCHIVE.md`.

### Step 1.3: Update CLAUDE.md (if needed)

**If** new architecture decisions, procedures, or patterns were established:
- Add to the appropriate section of `CLAUDE.md`
- Update the version number and date at the bottom

**Skip if:** Session was pure implementation with no new patterns or decisions.

---

## Phase 2 — Procedure Integrity

### Step 2.1: Verify Repeatable Procedures

**If** any Repeatable Procedures were executed or referenced during this session:
- Verify they are still accurate
- Fix any procedure defects discovered during execution
- Create new versions in the Knowledge DB via `db.insert_op_procedure()` or `db.insert_test_procedure()`

### Step 2.2: Confirm regression test coverage

**If** bugs were fixed during this session:
- Verify each fix has an associated automated regression test
- Per owner rule: "Manual test → automated test rule — bug fix MUST include regression test"

---

## Phase 3 — External Updates

### Step 3.1: Update agentredcx.com (if applicable)

**If** new customer-visible features or UI changes were deployed:
- Update relevant documentation pages in `docs-site/`
- Rebuild and deploy the docs site

**Skip if:** Session was backend-only or infrastructure work not visible to merchants.

### Step 3.2: Commit and push to GitHub

```bash
git add <relevant files>
git commit -m "<session summary>"
git push origin main
```

### Step 3.3: Update GitHub Project Board

```bash
# Close completed items
gh project item-edit --id <item-id> --field-id <status-field> --project-id <project-id> --value "Done"
# Add new items for deferred work
gh issue create --title "<title>" --body "<body>" --label "backlog"
```

**Skip if:** No project board items changed status.

### Step 3.4: Update GitHub Wiki

**If** new architecture decisions, API changes, or operational procedures were created:
- Update the relevant wiki page(s) via `gh` CLI or direct edit

**Skip if:** No wiki-worthy changes.

---

## Phase 4 — Staging Deployment

### Step 4.1: Assess staging deployment risk

**Decision criteria — deploy to staging IF:**
- ✅ All tests pass (0 failures)
- ✅ Changes are backward-compatible (no breaking API changes)
- ✅ No infrastructure changes that require manual configuration

**DO NOT deploy to staging IF:**
- ❌ Any test failures exist
- ❌ Changes require environment variable updates not yet applied
- ❌ Changes are experimental/incomplete

### Step 4.2: Deploy to staging (if approved)

```bash
az containerapp update --name agent-red-staging --resource-group Agent-Red \
  --image acragentredeastus.azurecr.io/api-gateway:v<VERSION>
```

**Verification:** Health check must return the new version.

---

## Phase 5 — Session Handoff

### Step 5.1: Generate next-session prompt

Build a structured handoff prompt containing:
1. **Session summary** — What was accomplished
2. **Current status** — Production version, test counts, release plan step
3. **Suggested next tasks** — Ordered by priority
4. **Blockers or decisions needed** — Anything requiring owner input
5. **Open items** — Work that was started but not completed

### Step 5.2: Check audit cadence and store handoff prompt

Before storing the handoff prompt, check whether the **next** session should be an audit session:

```python
import sys; sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB
db = KnowledgeDB()

# Determine next session ID
current_session = "S<N>"
next_session_num = db.parse_session_number(current_session) + 1
next_session_id = f"S{next_session_num}"

# Build prompt — prepend audit directive if next session is an audit interval
prompt_parts = []
if db.is_audit_session(next_session_id):
    prompt_parts.append(db.get_audit_directive())
    prompt_parts.append("")  # blank line separator

prompt_parts.append("<the regular handoff prompt text>")

db.insert_session_prompt(
    session_id=current_session,
    prompt_text="\n".join(prompt_parts),
    context={
        "production_version": "<version>",
        "test_count": <N>,
        "test_failures": <N>,
        "wis_implemented": ["<id>", ...],
        "wis_verified": ["<id>", ...],
        "next_tasks": ["<task>", ...],
        "blockers": ["<blocker>", ...],
        "is_audit_session": db.is_audit_session(next_session_id),
    },
)
db.close()
```

**Audit cadence:** Every 5th session (S100, S105, S110, ...) is an audit session. The audit directive instructs the next session to perform a fresh-context review of KB integrity, documentation accuracy, procedure validity, and design debt before starting new feature work. The interval is configurable via `KnowledgeDB.AUDIT_INTERVAL`.

**Verification:** The next session's SessionStart hook will automatically read and display this prompt, including the audit directive if applicable.

### Step 5.3: Clean up artifacts

Scan for and remove:
- Expired temp files in project directory
- Scratch files created during debugging
- Obsolete documents superseded by newer versions

**Rule:** Never delete files without listing them first. Protected files in MEMORY.md must not be touched.

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| Knowledge DB locked (WAL) | Environment transient | Retry after closing other DB connections |
| GitHub push rejected | Environment transient | Pull and rebase, then retry |
| Staging deploy fails (image not found) | Procedure defect | Verify ACR build completed; check image tag |
| Wiki edit conflicts | Environment transient | Pull latest wiki, resolve conflicts |
| Assertion count mismatch | Procedure defect | Investigate which spec changed; update assertion |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
