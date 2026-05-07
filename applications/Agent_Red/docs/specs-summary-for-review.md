# System Specification — Phase 1 Extraction Summary

**Total specs extracted from transcripts:** 871
**Source sessions:** 90
**Existing KB entries (work items):** 163

## Source Type Breakdown

| Source | Count |
|--------|-------|
| owner_directive | 758 |
| owner_approval | 113 |

## Specifications by Domain

### ADMIN_UI (263 specs)

- **SPEC-0001**: The sidebar nav label for the Configuration page MUST read 'Agent configuration'
- **SPEC-0002**: The sidebar nav label for the Widget page MUST read 'Widget configuration'
- **SPEC-0003**: The Team page table header column MUST read 'Team member' instead of 'Member'
- **SPEC-0004**: The role label for the 'agent' role MUST read 'Escalation agent' instead of 'Agent'
- **SPEC-0005**: The Escalation slider MUST display 'Conservative' left-justified and 'Aggressive' right-justified, neither extending bey...
- *...and 258 more*

### GENERAL (99 specs)

- **SPEC-0034**: Only fixes to open-source artifacts MUST flow back to the AGNTCY project, nothing else
- **SPEC-0047**: The term 'effort' MUST NOT be used in project discussions; use tokens consumed, elapsed time, or probability of regressi...
- **SPEC-0067**: A UI glossary MUST be maintained and Claude MUST encourage consistent use of glossary terms
- **SPEC-0068**: Glossary term: 'control' = element that triggers a change of system state (buttons, selectors, filters, checkboxes, radi...
- **SPEC-0069**: Glossary term: 'input' = element that elaborates the future desired state when the next control is triggered
- *...and 94 more*

### OPS (81 specs)

- **SPEC-0027**: The master test MUST include a tested plan to execute a non-disruptive upgrade of the production environment
- **SPEC-0028**: A parallel production-capable dev/test environment MUST be created for future releases
- **SPEC-0029**: Non-disruptive upgrade MUST be proven before getting Shopify app store approval
- **SPEC-0033**: A detailed step-by-step process for non-disruptive upgrade MUST include provisioning scripts and a regression test packa...
- **SPEC-0035**: A standard pre-flight checklist MUST be executed for any production deployment
- *...and 76 more*

### TESTING (80 specs)

- **SPEC-0026**: A master test plan MUST synthesize all requirements into a single test with 100% pass rate before submission
- **SPEC-0039**: End-to-end tests MUST be run on a freshly initialized environment, not one with stale data
- **SPEC-0040**: 100% UI test coverage means every possible input and value for every possible state has been checked
- **SPEC-0041**: 100% UI test coverage MUST include every button pushed, every selection selected, every state for a given set of inputs ...
- **SPEC-0042**: 100% UI test coverage MUST include Light/Dark mode verification for every test
- *...and 75 more*

### CONFIG (65 specs)

- **SPEC-0052**: Brand voice MUST be a mandatory configuration field
- **SPEC-0053**: Language support at launch MUST be English only, with Spanish and French planned next
- **SPEC-0054**: All configuration page changes are drafts until activated using the 'Activate' control
- **SPEC-0058**: All transient keys, values, URLs, and variables that change between builds or tenant environments MUST NOT be hardcoded;...
- **SPEC-0064**: When configuration becomes Active, the widget MUST immediately become available
- *...and 60 more*

### AUTH (48 specs)

- **SPEC-0009**: Newly added team members MUST receive a welcome email with a temporary strong password
- **SPEC-0010**: Temporary passwords for team members MUST expire periodically
- **SPEC-0011**: Users with expired passwords MUST be flagged as not-active so the merchant admin can take action
- **SPEC-0012**: Team members MUST be able to change their temporary password
- **SPEC-0077**: The standalone admin MUST be secured with a simple password to avoid casual trespassers
- *...and 43 more*

### CONVERSATIONS (45 specs)

- **SPEC-0096**: Escalation action MUST ask which team member or which escalation category to route to
- **SPEC-0097**: Escalated conversations MUST show up when using the escalation filter
- **SPEC-0180**: Implement CQ-1: conversation quality scoring infrastructure that evaluates every conversation on a 1-5 scale.
- **SPEC-0181**: Implement CQ-2: quality threshold alerting that notifies when conversation quality falls below a configurable threshold.
- **SPEC-0183**: Implement CQ-4: automated quality regression detection that identifies drops in conversation quality.
- *...and 40 more*

### WIDGET_UI (42 specs)

- **SPEC-0023**: The chat widget MUST support a Dark Mode option
- **SPEC-0024**: The Live Preview MUST support a Dark Mode option
- **SPEC-0030**: The standalone admin chat UI MUST use Agent Red colors, not default blue
- **SPEC-0032**: The default widget colors and styling MUST match Agent Red brand colors, customizable from there by the merchant
- **SPEC-0038**: The default chat widget colors MUST be Agent Red colors rather than blue
- *...and 37 more*

### BILLING (34 specs)

- **SPEC-0083**: Pricing and packaging decisions are orthogonal to release scope — base product plus optional features may be required fo...
- **SPEC-0171**: Add-on modules MUST each indicate which entitlements are required for activation (Starter, Pro, Pro+, Enterprise)
- **SPEC-0172**: Add-on modules not available for the current tier MUST NOT be subscribable; the Subscribe control MUST show the minimum ...
- **SPEC-0173**: The Upgrade path MUST display entitlement tiers in order (Starter -> Pro -> Pro+ -> Enterprise) with an option to Upgrad...
- **SPEC-0174**: Completing an Upgrade MUST change the available subscribable add-on modules to match the new entitlement level
- *...and 29 more*

### API (29 specs)

- **SPEC-0188**: Implement CQ-9: quality reporting API exposing quality metrics through a REST endpoint.
- **SPEC-0215**: Refactoring R2 (response model consolidation) shall be implemented at P1 priority.
- **SPEC-0216**: Refactoring R3 (middleware chain simplification) shall be deferred to post-launch.
- **SPEC-0218**: Refactoring R5 (Cosmos client singleton) shall be rejected — current pattern is acceptable.
- **SPEC-0219**: Refactoring R6 (error handler unification) shall be implemented at P2 priority.
- *...and 24 more*

### PROVISIONING (29 specs)

- **SPEC-0057**: A freshly initialized tenant MUST show zero conversations on the Dashboard (no synthetic historical data)
- **SPEC-0201**: The standalone admin console shall include a tenant provisioning form for creating new tenants via the SPA.
- **SPEC-0202**: A Shopify purchase event shall trigger automated tenant provisioning without manual intervention.
- **SPEC-0204**: Harrison Corp and Kidsely shall be provisioned as beta test tenants.
- **SPEC-0261**: Cosmos DB full initialization shall create all 10 containers with DiskANN vector index and correct partition keys, uniqu...
- *...and 24 more*

### KNOWLEDGE_BASE (21 specs)

- **SPEC-0164**: KB changes MUST participate in the Save-then-Activate flow: KB creates/edits/deletes mark config as Pending, activation ...
- **SPEC-0166**: There MUST be a way to restore (unarchive) an article that has been archived
- **SPEC-0575**: Knowledge Base MUST allow adding a test entry, and the entry MUST appear in the list and be editable and deletable
- **SPEC-0617**: Product documentation MUST be vectorized and added to RAG so admin users can ask questions about admin tools while viewi...
- **SPEC-0641**: The Knowledge Base MUST support adding a test article that appears in the list and can be edited and deleted.
- *...and 16 more*

### TEAM (16 specs)

- **SPEC-0136**: When 'Escalation agent' role is selected, the team member MUST also be assigned to one or more escalation categories (Sa...
- **SPEC-0137**: It MUST be possible to toggle each team member between enabled and disabled
- **SPEC-0311**: The Team Management API (WI-179) shall use a dedicated team_members Cosmos DB collection (not an embedded array in the t...
- **SPEC-0359**: Escalation agents MUST have read-only access to the Inbox page
- **SPEC-0365**: Team members MUST NOT be able to change their own email addresses — email is an admin-controlled identity field
- *...and 11 more*

### EMAIL (15 specs)

- **SPEC-0154**: Email sending MUST use Titan SMTP with credentials from env.local (TITAN_USER_ID, TITAN_PASSWORD) via smtp.titan.email:4...
- **SPEC-0237**: Escalation notifications shall be sent via email to team members (not as an in-app 'assign to agent' action).
- **SPEC-0409**: Azure Communication Services MUST be used as the email provider.
- **SPEC-0420**: Team member invitation emails MUST be sent when a team member is invited. The system MUST NOT rely on the admin manually...
- **SPEC-0491**: The merchant superadmin MUST receive notification emails for: initial Trial activation, entitlement changes, tenancy exp...
- *...and 10 more*

### SHOPIFY (3 specs)

- **SPEC-0350**: Shopify merchant category images MUST be included for marketing purposes
- **SPEC-0355**: The Shopify embedded admin MUST include a cross-navigation link to the standalone admin console
- **SPEC-0356**: Documentation links MUST be included in the Shopify app submission materials

### DOCS (1 specs)

- **SPEC-0336**: WI #77 (API documentation with OpenAPI/Swagger) approved for implementation

## KB Cross-Reference Results

| Metric | Count | % |
|--------|-------|---|
| Specs matching a KB entry | 499 | 57.3% |
| Specs with NO KB match (new) | 372 | 42.7% |
| KB entries with matching specs | 109/163 | 66.9% |
| KB entries with NO matching specs | 54/163 | 33.1% |

**Average decomposition:** 8.9 granular specs per KB work item (range: 1-176).

### What the uncovered 372 specs represent

These are granular specifications the owner expressed during sessions that were
**never captured as KB work items**. They include:
- Specific color values (e.g., "chat history background MUST be #19191A")
- Exact label text (e.g., "sidebar nav label MUST read 'Agent configuration'")
- Pixel dimensions (e.g., "integration logos MUST have a height of 150px")
- Dark mode palette rules (e.g., "Dark Mode MUST use greys, not blue/purple")
- UI behavior rules (e.g., "Deactivate action MUST show confirmation dialog")
- Process policies (e.g., "no effort estimates", "launch timing is owner's decision")

These are exactly the kind of granular specifications that were missing from the
project's governance — they were expressed, implemented, but never recorded as
testable specifications. This is why drift could not be detected.

### Uncovered specs by domain (top 5)

| Domain | New Specs | Example |
|--------|-----------|---------|
| ADMIN_UI | 80 | Logo placement, color values, dark mode palette |
| GENERAL | 70 | Process policies, terminology rules, glossary terms |
| OPS | 38 | Deployment procedures, upgrade requirements |
| TESTING | 33 | Test methodology, coverage definitions |
| CONFIG | 29 | Field defaults, activation rules, mandatory inputs |

### What the 54 orphan KB entries represent

KB entries with no matching extracted specs are likely:
1. Implementation-level features Claude proposed and built (Phase 2 will capture these)
2. Deferred/retired items with no active specification
3. Items where keyword matching missed the connection

## Completeness Note

This Phase 1 extraction captures specs from **owner messages only** (directives +
explicit approvals). It does NOT yet capture:
- Claude proposals accepted implicitly (no explicit "yes" from owner)
- Implementation details never discussed in transcripts
- Ad-hoc decisions made during coding (text, colors, defaults chosen by Claude)

**Phase 2** (implementation inspection) will fill these gaps by creating specs
for the current implementation state — every element in the codebase gets a spec,
regardless of whether it originated from an owner directive or a Claude decision.

## Next Steps

1. Owner reviews this extraction domain by domain
2. Phase 2: Implementation inspection creates specs for current code state
3. Merge Phase 1 (owner-sourced) + Phase 2 (implementation-sourced) into unified System Specification
4. Phase 3: Audit all 4,652 tests to link each test to a specification
