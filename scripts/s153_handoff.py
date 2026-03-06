"""S153 session handoff prompt."""
import sys
sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()

prompt = r"""Continue work on Agent Red Customer Experience commercial project.
Location: E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
Key files: CLAUDE.md, memory/MEMORY.md
Session: S154

Last session (S153) completed:
- Fixed 7 code defects (WI-1055..1061): connection pooling, TOCTOU lock, TRIAL tier, auth error, rate limit lock, timeout re-raise, UUID draft ID
- Fixed 2 operational procedures (WI-0842, WI-0843)
- Implemented customer interface features (WI-0868..0870, widget preview + header subtitle)
- Assessed provider admin features (18/20 resolved, 2 deferred: WI-0891 PipelineMetricsAggregator, WI-0883 human-readable IDs)
- Created SPEC-1662 (GOV-18: Assertion Quality Standard)
- Verified 42 specs across 3 batches with 118 real production-interface tests (TEST-8177..8294)
- Committed as e1865c6c. 5,442 tests passing, 0 fail.

Current state:
- 1,868 specs (952 implemented, 590 specified, 314 verified, 11 retired)
- 8,294 test artifacts, 1,862 assertions (100% pass rate)
- 16 open work items, 950 resolved
- All quality gates green

Remaining spec verification: 590 specified specs remain. Major clusters: Widget (56), Config (43), Tenant (32), Conversation (16), Shopify (15), Team (14). Specs intentionally NOT promoted: SPEC-1630/1632 (email styling), SPEC-1579..1587 (Pipeline Observatory scaffold), SPEC-1626 (distributed rate limiting) -- these need code changes.

Next: [describe task]."""

db.insert_session_prompt(
    session_id="S153",
    prompt_text=prompt,
    context={
        "commit": "e1865c6c",
        "tests_passed": 5442,
        "specs_promoted": 42,
        "test_artifacts_created": 118,
        "open_wis": 16,
    },
)
print("Handoff prompt generated for S153")
