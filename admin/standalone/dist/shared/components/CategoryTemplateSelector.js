import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * CategoryTemplateSelector — picks and applies an industry template.
 *
 * KA-7: Knowledge Automation Admin UI.
 *
 * Displays available category templates as a grid of selectable cards.
 * On selection, shows preview details and "Apply to KB" button.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState } from 'react';
import { Paper, Group, Stack, Text, Badge, Button, SimpleGrid, Alert, Loader, Center, } from '@mantine/core';
import { tokens } from '../theme/styles';
const ACTION_BLUE = tokens.action;
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export function CategoryTemplateSelector({ templates, loading = false, error = null, onApply, applyLoading = false, applyError = null, }) {
    const [selected, setSelected] = useState(null);
    const [applyResult, setApplyResult] = useState(null);
    if (loading) {
        return (_jsxs(Center, { py: "lg", children: [_jsx(Loader, { size: "sm" }), _jsx(Text, { size: "sm", c: "dimmed", ml: "sm", children: "Loading templates..." })] }));
    }
    if (error) {
        return (_jsx(Alert, { color: "red", variant: "light", title: "Failed to load templates", children: error }));
    }
    if (!templates || templates.length === 0) {
        return (_jsx(Text, { size: "sm", c: "dimmed", ta: "center", py: "md", children: "No category templates available." }));
    }
    const selectedTemplate = templates.find((t) => t.id === selected);
    const handleApply = async () => {
        if (!selected)
            return;
        const result = await onApply(selected);
        if (result) {
            setApplyResult(result);
        }
    };
    return (_jsxs(Stack, { gap: "md", children: [_jsx(SimpleGrid, { cols: { base: 1, sm: 2, md: 3 }, spacing: "sm", children: templates.map((template) => (_jsx(Paper, { p: "sm", radius: "md", withBorder: true, style: {
                        cursor: 'pointer',
                        borderColor: selected === template.id ? ACTION_BLUE : undefined,
                        borderWidth: selected === template.id ? 2 : 1,
                    }, onClick: () => {
                        setSelected(selected === template.id ? null : template.id);
                        setApplyResult(null);
                    }, children: _jsxs(Stack, { gap: "xs", children: [_jsxs(Group, { justify: "space-between", wrap: "nowrap", children: [_jsx(Text, { fw: 600, size: "sm", truncate: "end", children: template.name }), _jsxs(Badge, { size: "xs", variant: "light", color: "gray", children: [template.articleCount, " articles"] })] }), _jsx(Text, { size: "xs", c: "dimmed", lineClamp: 2, children: template.description })] }) }, template.id))) }), selectedTemplate && (_jsx(Paper, { p: "md", radius: "md", withBorder: true, children: _jsxs(Stack, { gap: "sm", children: [_jsxs(Group, { justify: "space-between", children: [_jsxs("div", { children: [_jsx(Text, { fw: 600, children: selectedTemplate.name }), _jsx(Text, { size: "sm", c: "dimmed", children: selectedTemplate.description })] }), _jsx(Button, { color: ACTION_BLUE, onClick: handleApply, loading: applyLoading, children: "Apply to knowledge base" })] }), _jsxs(Group, { gap: "sm", children: [_jsxs(Badge, { variant: "light", children: [selectedTemplate.articleCount, " starter articles"] }), selectedTemplate.suggestedBrandVoice && (_jsxs(Badge, { variant: "light", color: "violet", children: ["Voice: ", selectedTemplate.suggestedBrandVoice] }))] }), applyError && (_jsx(Alert, { color: "red", variant: "light", title: "Apply failed", children: applyError })), applyResult && (_jsxs(Alert, { color: "green", variant: "light", title: "Template applied", children: ["Created ", applyResult.articlesCreated, " articles (", applyResult.totalChars > 1000
                                    ? `${(applyResult.totalChars / 1000).toFixed(1)}k`
                                    : applyResult.totalChars, " characters).", applyResult.configSuggestions && Object.keys(applyResult.configSuggestions).length > 0 && (_jsx(Text, { size: "xs", mt: "xs", c: "dimmed", children: "Configuration suggestions generated \u2014 check the Configuration page." }))] }))] }) }))] }));
}
//# sourceMappingURL=CategoryTemplateSelector.js.map