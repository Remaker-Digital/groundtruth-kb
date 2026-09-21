# Specification lifecycle corrections

1. Read the current canonical specification, its version and authority state. Identify the owner's intended formal change and the affected current citations and work.
2. Keep formal authority distinct from implementation progress. Active means the requirement applies; superseded and retired records remain formal history. None of those states proves that implementation is complete or independently verified.
3. For a supersession or retirement, establish the actual replacement or reason the requirement no longer applies. A repeated assertion failure, an absent test, or a passing structural check is not that reason.
4. Apply the correction through the configured CLI's existing formal writer and read back the new current state. Preserve prior versions. If the writer reports changed input, re-read and reconcile the change instead of applying an obsolete postimage.
5. Reconcile current references and affected work scope. Existing verified bytes or prior proposal approval cannot be reused for a materially changed obligation without the required fresh review.

Structural checks can help locate a defect. File presence and matching text do not establish executable behavior. Run the actual specification-derived tests and preserve independent implementation review; do not infer completion from a stored historical result.
