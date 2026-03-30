/**
 * Domain tag normalization for agent overlays and team members.
 *
 * Runtime enforcement (IntentRouter) uses exact set intersection,
 * so tags must be normalized identically on both the agent-side
 * (overlay staff_domain_tags) and caller-side (team member
 * staff_domain_tags) to avoid false denials.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

/**
 * Normalize domain tags: trim whitespace, lowercase, deduplicate, sort.
 *
 * Applied at every write point (agent overlay save, team member edit,
 * team member invite) so runtime intersection always matches.
 */
export function normalizeDomainTags(tags: string[]): string[] {
  const seen = new Set<string>();
  const result: string[] = [];
  for (const raw of tags) {
    const tag = raw.trim().toLowerCase();
    if (tag && !seen.has(tag)) {
      seen.add(tag);
      result.push(tag);
    }
  }
  return result.sort();
}
