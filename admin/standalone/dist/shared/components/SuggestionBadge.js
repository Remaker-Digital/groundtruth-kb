import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Badge, Tooltip, } from '@mantine/core';
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export function SuggestionBadge({ suggestion, currentValue, onApply, }) {
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
    return (_jsx(Tooltip, { label: `${confidenceLabel}: "${truncatedValue}" (from ${suggestion.source}). Click to apply.`, multiline: true, w: 300, withArrow: true, children: _jsx(Badge, { size: "xs", variant: "light", color: "violet", style: { cursor: 'pointer' }, onClick: () => onApply(suggestion.value), children: "Suggested" }) }));
}
/**
 * Wrapper that places a SuggestionBadge next to a label.
 */
export function LabelWithSuggestion({ label, suggestion, currentValue, onApply, }) {
    return (_jsxs("span", { style: { display: 'inline-flex', alignItems: 'center', gap: 6 }, children: [_jsx("span", { children: label }), _jsx(SuggestionBadge, { suggestion: suggestion, currentValue: currentValue, onApply: onApply })] }));
}
//# sourceMappingURL=SuggestionBadge.js.map