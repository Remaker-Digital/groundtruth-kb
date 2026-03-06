"""Generate S154 session handoff prompt."""
import sys
sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()

prompt = """Continue work on Agent Red Customer Experience commercial project.
Location: E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement
Key files: CLAUDE.md, memory/MEMORY.md
Session: S154

## S153 Summary
S153 was a massive spec verification session spanning 4+ context windows:
- **377 specs promoted** specified->implemented across 12 batches (501 test artifacts TEST-8177..TEST-8677)
- **14 cold grey palette specs retired** as OBSOLETE per owner directive (warm stone palette in agentRedTheme.ts)
- **241 specified specs remain** - all genuinely non-promotable (process directives, future features, contradicted by implementation, business decisions)
- 7 code defects fixed, 9 customer interface features, GOV-18 created
- Commit e1865c6c (product code changes)

## Current KB State
- 1,287 implemented, 314 verified, 241 specified, 25 retired, 1 approved
- 8,677 test artifacts, all quality gates GREEN

## Remaining 241 Specified Specs (Non-Promotable Categories)
- **Process/governance directives** (~80): How work should be done
- **Future features** (~60): CQ-* conversation quality, A/B testing, Pipeline Observatory, MCP, campaigns
- **Contradicted by implementation** (~30): Wizard 3 steps not 8, wrong logo variants, features marked for removal still present
- **Business/creative decisions** (~25): Pricing, competitive comparisons, category images
- **WI approvals** (~20): Approvals for work items, not code implementations
- **External documentation** (~15): agentredcx.com content, GitHub wiki formatting
- **Aspirational** (~10): 100% coverage, every element has tooltip, resizable width

## Next Steps
1. **Owner decision needed:** Should any of the 241 remaining specified specs be retired/reclassified?
2. **Commit S153 test files** (12 batch verification files + recording scripts)
3. **Continue with normal project work** - spec verification campaign is complete
4. **Re-run assertion check** to update quality dashboard with new spec statuses
"""

db.insert_session_prompt(
    session_id="S154",
    prompt_text=prompt,
)
print("Session prompt for S154 generated")
