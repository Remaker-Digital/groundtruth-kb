# Session Handoff Prompt Template

Use this template for Phase 5 of `kb-session-wrap`. The prompt must be complete enough for a fresh agent to continue without hidden chat memory.

Preferred first line:

```text
::init gtkb pb
```

Template body:

```text
::init gtkb pb

Continue GroundTruth-KB work in E:/GT-KB.

Session carried forward: <SESSION_ID>
Branch/HEAD: <branch> @ <sha>
Dirty state at wrap: <clean|summary of remaining uncommitted paths>

## Previous Session Summary
<1-4 concise paragraphs covering what changed and why. Include bridge IDs, work item IDs, spec IDs, and report paths when relevant.>

## Knowledge Collection
- MemBase: <work items/specs/projects/session_prompts updated, skipped, or blocked>
- Deliberation Archive: <captures/harvest counts or blocker>
- memory/MEMORY.md: <updated/no-op reason>
- Bridge state: <latest statuses from bridge/INDEX.md that matter next>
- Reports/procedures: <paths to implementation reports, reviews, or procedure updates>
- Ignored local evidence: <.groundtruth/.gtkb-state/report paths to inspect, or none>

## Verification
- Tests/assertions run: <commands and results>
- Wrap scanner outputs: <snapshot paths and severity summary>
- Known failures or skipped verification: <tracked reason or none>

## Blockers / Risks
- <owner/governance/tooling blocker, with exact next action>

## Suggested Next Actions
1. <next action>
2. <next action>
3. <next action>
```

Insertion example, when MemBase API support is available:

```python
from groundtruth_kb.db import KnowledgeDB

db = KnowledgeDB("groundtruth.db")
db.insert_session_prompt(
    session_id="<NEXT_SESSION_ID>",
    prompt_text=prompt_text,
    changed_by="codex",
    change_reason="<SESSION_ID>: session wrap handoff",
)
```

If `session_prompts` insertion is blocked, write the prompt text into the wrap summary/report and record the blocker explicitly.
