# Pending Owner Decisions

This file is owned by .claude/hooks/owner-decision-tracker.py.

---

## Pending

(none)

## Resolved

- id: DECISION-0001
  asked_at: 2026-04-25T17:34:16.235676Z
  question: "ose anti-patterns (\"want me to X or Y?\") and logs them. **"
  detected_via: prose:offering_or_choice
  status: resolved
  question_hash: 816b3bc292f9eb72
  resolved_at: 2026-04-25T22:50:00Z
  resolved_in_session: S309
  answer: "doc-paragraph false positive; the assistant was DESCRIBING the prose-anti-pattern detector in a session-end report, not asking an owner decision. Captured into GTKB-STARTUP-ENHANCEMENTS Phase 7 (FP-guard tightening: quotation-aware + code-fence-aware) as live test evidence."
  notes: "Edited-by-prime-via-owner-direction 2026-04-25T22:50:00Z (owner asked to drive session to optimal conclusion)"
- id: DECISION-0002
  asked_at: 2026-04-25T18:05:52.219310Z
  question: "The detector saw `\"want me to X or Y?\"` as a literal stri"
  detected_via: prose:offering_or_choice
  status: resolved
  question_hash: 4d507bca99868817
  resolved_at: 2026-04-25T22:50:00Z
  resolved_in_session: S309
  answer: "doc-paragraph false positive; same class as DECISION-0001. The assistant was citing a backtick-quoted example of the regex pattern. Captured into GTKB-STARTUP-ENHANCEMENTS Phase 7 as live test evidence; quotation/code-fence-aware guard will suppress this case."
  notes: "Edited-by-prime-via-owner-direction 2026-04-25T22:50:00Z (owner asked to drive session to optimal conclusion)"
- id: DECISION-0005
  asked_at: 2026-04-25T18:22:47.070797Z
  question: "e | not yet filed — awaiting your direction |  ## Next move opt"
  detected_via: prose:awaiting_input
  status: resolved
  question_hash: 3dbf274b10e088de
  resolved_at: 2026-04-25T22:50:00Z
  resolved_in_session: S309
  answer: "doc-paragraph false positive; the assistant was rendering a markdown table cell describing the GTKB-STARTUP-ENHANCEMENTS row 9 status (\"awaiting your direction\"). Table-cell prose triggered the awaiting_input regex. Captured into GTKB-STARTUP-ENHANCEMENTS Phase 7 — table-cell context is another guard candidate alongside quotation/code-fence."
  notes: "Edited-by-prime-via-owner-direction 2026-04-25T22:50:00Z (owner asked to drive session to optimal conclusion)"
- id: DECISION-0003
  asked_at: 2026-04-25T18:22:47.070797Z
  question: "How aggressive should the rule-file consolidation be in Phase P4?"
  options:
    - "Full consolidation (Recommended)"
    - "Soft consolidation"
    - "Index-only"
  detected_via: ask_user_question
  status: resolved
  question_hash: 421a8dd70dc726b2
  resolved_at: 2026-04-25T18:22:47.070797Z
  answer: "User has answered your questions: \"How aggressive should the rule-file consolidation be in Phase P4?\"=\"Full consolidation (Recommended)\", \"Which phase should we start with, given the existing GTKB-STARTUP-ENHANCEMENTS slice plan?\"=\"P1 quick wins first (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""
- id: DECISION-0004
  asked_at: 2026-04-25T18:22:47.070797Z
  question: "Which phase should we start with, given the existing GTKB-STARTUP-ENHANCEMENTS slice plan?"
  options:
    - "P1 quick wins first (Recommended)"
    - "P3 six-primer registry first"
    - "P6 action tray first"
  detected_via: ask_user_question
  status: resolved
  question_hash: f7d7193d324160b8
  resolved_at: 2026-04-25T18:22:47.070797Z
  answer: "User has answered your questions: \"How aggressive should the rule-file consolidation be in Phase P4?\"=\"Full consolidation (Recommended)\", \"Which phase should we start with, given the existing GTKB-STARTUP-ENHANCEMENTS slice plan?\"=\"P1 quick wins first (Recommended)\". You can now continue with the user's answers in mind."
  notes: ""

## History

(none)
