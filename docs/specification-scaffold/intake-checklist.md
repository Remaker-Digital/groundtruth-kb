# Specification Intake Checklist

Use this checklist at the start of a new project to establish the specification foundation. Each step produces artifacts in the Knowledge Database.

## Pre-Intake

- [ ] Initialize groundtruth-kb instance (`gt project init`)
- [ ] Import boilerplate specifications from `initial-specifications.json`
- [ ] Verify KB is accessible via Python API and web UI
- [ ] Establish session ID convention (S1, S2, ...)
- [ ] Configure CLAUDE.md with project identity, copyright notice, and branching strategy

## Phase 1: Governance Foundation (Session 1)

- [ ] Review and adapt GOV-01 through GOV-08 for project context
- [ ] Adjust coverage thresholds and quality gate parameters
- [ ] Define spec-classifier hook triggers (GOV-09)
- [ ] Record any project-specific governance rules (GOV-09+)
- [ ] Verify assertion-check hook runs at session start

## Phase 2: Architecture Decisions (Sessions 1-3)

- [ ] Identify cross-cutting architectural concerns
- [ ] For each concern, create an ADR spec:
  - Context: what forces are at play
  - Decision: what was chosen and why
  - Consequences: trade-offs accepted
  - Failed approaches: what was considered and rejected
  - Rejected alternatives: other options with rationale
- [ ] Derive machine-checkable DCL constraints from each ADR
- [ ] Record assertions on DCL specs for automated verification

## Phase 3: Protected Behaviors (Sessions 2-4)

- [ ] Identify behaviors that must never regress (data integrity, security, isolation)
- [ ] Create PB-* specs with machine-verifiable assertions
- [ ] Ensure Phase 0 regression gate checks PB assertions before every build
- [ ] Document rollback procedures for PB violations

## Phase 4: Foundational Requirements (Sessions 3-8)

- [ ] Elicit functional requirements from owner/stakeholders
- [ ] For each requirement:
  - Record as SPEC-* with status `specified`
  - Assign priority (P0-P3) and scope
  - Create linked work items with origin `new`
  - Create linked tests (GOV-12: WI triggers tests)
  - Add to backlog snapshot
- [ ] Group requirements into implementation phases
- [ ] Record phase plan as test_plan with ordered phases

## Phase 5: Non-Functional Requirements (Sessions 4-10)

- [ ] Performance: latency targets, throughput, scalability
- [ ] Security: authentication, authorization, encryption, audit
- [ ] Reliability: availability targets, failure modes, recovery
- [ ] Observability: logging, metrics, alerting, dashboards
- [ ] Compliance: data residency, privacy, retention
- [ ] Create specs for each NFR with measurable acceptance criteria
- [ ] Create architecture decision records for infrastructure choices

## Phase 6: Test Plan Setup (Sessions 5-10)

- [ ] Create PLAN-001 test plan with initial phases
- [ ] Map tests to phases by execution order
- [ ] Define gate criteria for each phase
- [ ] Establish test type distribution targets:
  - Unit tests: ~70% (isolated function/method tests)
  - Integration tests: ~15% (service boundary tests)
  - E2E tests: ~10% (workflow tests)
  - Behavioral/other: ~5% (BDD, assertion, structural)
- [ ] Configure CI pipeline with test shards and coverage threshold

## Phase 7: Loyal Opposition Setup (Sessions 5-10)

- [ ] Deploy second agent (Loyal Opposition) with review mandate
- [ ] Configure bridge protocol for async message passing
- [ ] Establish review cadence:
  - Implementation proposal → LO review → GO/NO-GO
  - Post-implementation report → LO review → sign-off
- [ ] Define evidence standard (claim, evidence, severity, impact, action)
- [ ] Create initial LO report templates

## Post-Intake Verification

- [ ] All governance specs have assertions that pass
- [ ] Architecture decisions cover identified cross-cutting concerns
- [ ] Protected behaviors have regression assertions
- [ ] Foundational requirements are linked to tests and work items
- [ ] Test plan phases are ordered and have gate criteria
- [ ] Loyal Opposition is online and has completed at least one review cycle
- [ ] Backlog snapshot captures current state
- [ ] Session wrap-up procedure is documented

## Ongoing Cadence

After intake, the following rhythm maintains specification health:

| Cadence | Activity |
|---------|----------|
| Every session | Run assertion-check hook at start; update specs touched |
| Every 5th session | Audit session: spec coverage gaps, unmapped specs, stale WIs |
| Every deployment | Verify PB assertions; run Phase 0 regression gate |
| Monthly | Review and retire obsolete specs; quality score computation |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
