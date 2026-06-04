## Constraint

The dispatch envelope record schema (per `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001`) MUST satisfy the following machine-checkable assertions before a dispatch may fire.

## Machine-Checkable Assertions

1. **Target exclusivity:** Every envelope record has exactly one `target_harness_id` OR one `target_role`, never both. A `target_role` value MUST be `prime-builder` or `loyal-opposition` (closed set; `acting-prime-builder` SET-rejected per `GOV-ACTING-PRIME-BUILDER-001`).
2. **Activity gate mandatory:** Every envelope has a non-empty `activity_gate` — a deterministic read-only predicate run before spawning; a positive result is required to dispatch (S308 guard).
3. **Authorization reference mandatory:** Every envelope carries an `authorization` reference (PAUTH or owner-decision DELIB); dispatch is refused if absent or expired.
4. **Specialization is not an authority substitute:** `specialization_ref`, when present, names an existing skill / session-lane / subagent-type; it never substitutes for the authority role.
5. **Singleton dispatch:** Dispatch is singleton per `(envelope_id, fire_window)`; re-entrancy is blocked by the existing dispatch-state/lock path.

## Authority

- Derived from `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` (this DCL constrains the envelope schema specified by the ADR).
- `S308 lesson` (blind activity-independent automation is the defect; this DCL's activity-gate mandate preserves the lesson).
- `GOV-ACTING-PRIME-BUILDER-001` (authority role set is closed).
