import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Paper, Group, Stack, Text, Badge, Progress, Button, SimpleGrid, Alert, Loader, } from '@mantine/core';
import { tokens } from '../theme/styles';
const ACTION_BLUE = tokens.action;
// ---------------------------------------------------------------------------
// Status helpers
// ---------------------------------------------------------------------------
const statusColorMap = {
    pending: 'yellow',
    running: 'blue',
    completed: 'green',
    failed: 'red',
    cancelled: 'gray',
};
const statusLabelMap = {
    pending: 'Pending',
    running: 'In Progress',
    completed: 'Completed',
    failed: 'Failed',
    cancelled: 'Cancelled',
};
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export function IngestionPanel({ job, loading = false, onCancel, cancelLoading = false, onRefresh, }) {
    if (loading) {
        return (_jsx(Paper, { p: "md", radius: "md", withBorder: true, children: _jsxs(Group, { justify: "center", py: "md", children: [_jsx(Loader, { size: "sm" }), _jsx(Text, { size: "sm", c: "dimmed", children: "Loading ingestion status..." })] }) }));
    }
    if (!job) {
        return (_jsx(Paper, { p: "md", radius: "md", withBorder: true, children: _jsx(Stack, { gap: "sm", align: "center", py: "md", children: _jsx(Text, { size: "sm", c: "dimmed", children: "No ingestion job found. Start one by importing from your storefront or selecting a category template below." }) }) }));
    }
    const isActive = job.status === 'pending' || job.status === 'running';
    return (_jsx(Paper, { p: "md", radius: "md", withBorder: true, children: _jsxs(Stack, { gap: "md", children: [_jsxs(Group, { justify: "space-between", children: [_jsxs(Group, { gap: "sm", children: [_jsx(Text, { fw: 600, size: "sm", children: "Ingestion Job" }), _jsx(Badge, { size: "sm", color: statusColorMap[job.status] || 'gray', variant: "filled", children: statusLabelMap[job.status] || job.status }), _jsx(Badge, { size: "xs", variant: "light", color: "gray", children: job.jobType === 'category_template' ? 'Template' : job.jobType.toUpperCase() })] }), _jsxs(Group, { gap: "xs", children: [isActive && onCancel && (_jsx(Button, { size: "xs", variant: "default", color: "red", onClick: onCancel, loading: cancelLoading, children: "Cancel" })), onRefresh && (_jsx(Button, { size: "xs", variant: "default", onClick: onRefresh, children: "Refresh" }))] })] }), isActive && (_jsx(Progress, { value: job.progressPercent, size: "lg", radius: "md", color: ACTION_BLUE, animated: job.status === 'running' })), _jsxs(SimpleGrid, { cols: 4, spacing: "sm", children: [_jsxs(Paper, { p: "xs", radius: "sm", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", children: "Articles created" }), _jsx(Text, { fw: 700, size: "lg", children: job.articlesCreated })] }), _jsxs(Paper, { p: "xs", radius: "sm", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", children: "Articles failed" }), _jsx(Text, { fw: 700, size: "lg", c: job.articlesFailed > 0 ? 'red' : undefined, children: job.articlesFailed })] }), _jsxs(Paper, { p: "xs", radius: "sm", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", children: "Total characters" }), _jsx(Text, { fw: 700, size: "lg", children: job.totalChars > 1000 ? `${(job.totalChars / 1000).toFixed(1)}k` : job.totalChars })] }), _jsxs(Paper, { p: "xs", radius: "sm", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", children: "Pages crawled" }), _jsx(Text, { fw: 700, size: "lg", children: job.pagesCrawled })] })] }), job.errorMessage && (_jsx(Alert, { color: "red", variant: "light", title: "Error", children: job.errorMessage })), job.status === 'completed' && (_jsxs(Alert, { color: "green", variant: "light", title: "Import complete", children: ["Successfully imported ", job.articlesCreated, " articles into your knowledge base."] }))] }) }));
}
//# sourceMappingURL=IngestionPanel.js.map