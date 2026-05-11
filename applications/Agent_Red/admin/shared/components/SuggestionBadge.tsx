// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * SuggestionBadge — inline badge for config field suggestions.
 *
 * KA-7: Knowledge Automation Admin UI.
 *
 * Renders a small "Suggested" badge next to empty config fields when
 * a suggestion is available from the KB analysis engine. Clicking the
 * badge applies the suggestion to the field.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import {
  Badge,
  Tooltip,
} from '@mantine/core';
import type { ConfigSuggestion } from '../hooks/useSuggestions';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface SuggestionBadgeProps {
  suggestion: ConfigSuggestion | undefined;
  currentValue: string | null | undefined;
  onApply: (value: unknown) => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function SuggestionBadge({
  suggestion,
  currentValue,
  onApply,
}: SuggestionBadgeProps) {
  // Only show when there's a suggestion and the field is empty
  if (!suggestion || (currentValue && currentValue.trim().length > 0)) {
    return null;
  }

  const confidenceLabel = suggestion.confidence >= 0.7
    ? 'High confidence'
    : suggestion.confidence >= 0.4
      ? 'Medium confidence'
      : 'Low confidence';

  const displayValue = typeof suggestion.value === 'string'
    ? suggestion.value
    : Array.isArray(suggestion.value)
      ? suggestion.value.join(', ')
      : JSON.stringify(suggestion.value);

  const truncatedValue = displayValue.length > 60
    ? displayValue.slice(0, 57) + '...'
    : displayValue;

  return (
    <Tooltip
      label={`${confidenceLabel}: "${truncatedValue}" (from ${suggestion.source}). Click to apply.`}
      multiline
      w={300}
      withArrow
    >
      <Badge
        size="xs"
        variant="light"
        color="violet"
        style={{ cursor: 'pointer' }}
        onClick={() => onApply(suggestion.value)}
      >
        Suggested
      </Badge>
    </Tooltip>
  );
}

/**
 * Wrapper that places a SuggestionBadge next to a label.
 */
export function LabelWithSuggestion({
  label,
  suggestion,
  currentValue,
  onApply,
}: {
  label: string;
  suggestion: ConfigSuggestion | undefined;
  currentValue: string | null | undefined;
  onApply: (value: unknown) => void;
}) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
      <span>{label}</span>
      <SuggestionBadge
        suggestion={suggestion}
        currentValue={currentValue}
        onApply={onApply}
      />
    </span>
  );
}
