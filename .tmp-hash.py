import hashlib
from pathlib import Path

f = Path(".claude/rules/canonical-terminology.md")
content = f.read_text(encoding="utf-8")

# Edit 1: Insert handoff prompt entry between harness identity and role assignment
old1 = "--harness-id <id> --owner-requested.\n\n### role assignment"
insert_block = """

### handoff prompt

**Definition:** The deterministic-service OUTPUT generated at session close
(canonical `::wrap`) by the handoff-prompt generator
(`SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`). A handoff prompt is the
structured content that carries forward session context, continuation scope,
and next-step direction to the next session. It is *generated content*,
distinct from its *persisted record*.

**Canonical alias:** none. Do NOT use "continuation prompt" — that label is
explicitly rejected (per `DELIB-20260883`) as a redundant third term for the
same concept.

**Not to be confused with:** `Session Prompt` — the PERSISTED RECORD of a
handoff prompt (the `session_prompts` MemBase row; see Supporting Records). A
handoff prompt is the generator output; a Session Prompt is that output stored
as a governed record. Two views of one thing: the handoff prompt is what
`::wrap` produces; the Session Prompt is what persists it for the next session
to consume.

**Source:** `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (the generator);
`DELIB-20260883` (owner terminology decision: generated-vs-stored model;
"continuation prompt" rejected); WI-4363 (`GTKB-SYSTEMS-TERMINOLOGY-MAP-001`).

**Implementation pointer:** `groundtruth_kb.session.wrap` / the handoff-prompt
deterministic service invoked at canonical `::wrap`; persisted as a
`session_prompts` row (the Session Prompt record).

"""
new1 = old1.replace("\n\n### role assignment", insert_block + "### role assignment")
content = content.replace(old1, new1, 1)

# Edit 2: Update Session Prompt row
old2 = "| Session Prompt | session_prompts | Structured handoff message for next session |"
new2 = '| Session Prompt | session_prompts | Structured handoff message for next session (the persisted record of a handoff prompt — see "handoff prompt") |'
content = content.replace(old2, new2, 1)

h = hashlib.sha256(content.encode("utf-8")).hexdigest()
print(f"sha256:{h}")
print(f"content_length: {len(content)}")
print(f"handoff_prompt_entry: {'### handoff prompt' in content}")
print(f"session_prompt_xref: {'see' in content and 'handoff prompt' in content}")
