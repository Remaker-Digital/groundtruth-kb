# Session Handoff Prompt Template

Use this template when generating the Phase 5 handoff prompt.

```python
db.insert_session_prompt(
    session_id="$0",
    prompt_text="""Continue work on Agent Red Customer Experience commercial project.
Location: E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement
Key files: CLAUDE.md, memory/MEMORY.md

## Session {next_session_id} — Continuing from $0

### Previous Session Summary
{what_was_done}

### Current Status
- Production: {version} (deployed/not deployed)
- Staging: {version}
- Tests: {pass_count} passed, {fail_count} failed
- Open WIs: {open_wi_count}

### Suggested Next Tasks
1. {task_1}
2. {task_2}
3. {task_3}

### Blockers / Open Items
- {blocker_or_open_item}
""",
    changed_by="Claude",
    change_reason=f"$0: Session wrap-up handoff",
)
```
