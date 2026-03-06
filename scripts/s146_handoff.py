"""S146 handoff prompt insertion."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))

import db as kdb

database = kdb.KnowledgeDB()

prompt = r"""Continue work on Agent Red Customer Experience commercial project.
Location: E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
Key files: CLAUDE.md, memory/MEMORY.md
Session: S147

## S146 Completed
Batch assertion generation achieved 60.5% coverage (1,129/1,867 specs), meeting the SPEC-1660 threshold. Three rounds of auto-generation: (1) Source-referenced specs with title pattern extraction, (2) Source file discovery for no-source specs, (3) Keyword-to-file mapping for remaining specs. 1,066 assertions pass (94.5% rate). 62 legacy non-machine assertions still fail. 51 specs remain without assertions.

## S147 Priorities (per S145 plan)
1. **Convert 62 legacy assertion failures** to machine-verifiable types (grep/glob/grep_absent). These are all early specs (SPEC-101..300 range) with types like "functional", "structural", "e2e", "requirement" that the assertion runner cannot execute.
2. **Push coverage toward 70%** -- 51 specs without assertions + converting legacy failures could reach ~65-70%.
3. **Test traceability improvement** -- currently 49.8% (target >80%). Run test_pipeline.py with --junitxml, then record_test_results.py to update KB test artifacts.
4. **GitHub Actions setup** -- owner deferred in S146 but this is the next infrastructure step after assertions are solid.

## Quality Dashboard State
- Assertion Coverage: 60.5% (target >= 60%) -- MET
- Test Traceability: 49.8% (target >80%) -- needs work
- Defect Velocity: +69 (91 resolved, 22 open) -- healthy
- Defect Escape Rate: 0 production incidents -- clean

## Batch Generation Scripts
- scripts/batch_assertions_round2.py -- source file discovery + glob fallback
- scripts/batch_assertions_round3.py -- keyword-to-file mapping table
These can be extended for future assertion generation rounds.
"""

result = database.insert_session_prompt(
    session_id="S147",
    prompt_text=prompt,
)
print(f"Handoff prompt inserted: {result.get('session_id', 'S147')}")
