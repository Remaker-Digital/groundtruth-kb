import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
import React, { useState, useMemo, useCallback, useRef } from 'react';
import { Paper, Table, TextInput, Select, Modal, Textarea, Button, Badge, Group, Stack, Title, Text, ActionIcon, SimpleGrid, Loader, Center, Tabs, Progress, Alert, Accordion, Tooltip, NumberInput, Switch, } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useKnowledgeBase, useSaveKBArticle, useUploadFile, useImportUrl, useExportCSV, useStalenessSummary, useVerifyEntry, useConfig, useUpdateConfig, useAutoSaveDraft } from '../../shared/hooks/index';
import { AutoSaveIndicator } from '../../shared/components/AutoSaveIndicator';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { useIngestionStatus, useTemplates, useStartIngestion, useCancelIngestion, useApplyTemplate } from '../../shared/hooks/useIngestion';
import { IngestionPanel } from '../../shared/components/IngestionPanel';
import { CategoryTemplateSelector } from '../../shared/components/CategoryTemplateSelector';
import { LoadingState } from '../../shared/LoadingState';
import { tokens } from '../../shared/theme/styles';
const BRAND_RED = tokens.brand; // accent only — drag borders, loaders, progress bars
const ACTION_BLUE = tokens.action;
const CATEGORIES = ['All', 'Policies', 'Shipping', 'Products', 'Sales', 'Services', 'FAQ', 'Custom'];
const STATUSES = ['All', 'Published', 'Draft', 'Archived'];
const ACCEPTED_FILE_TYPES = '.pdf,.docx,.csv,.txt';
const statusColorMap = {
    published: 'green',
    draft: 'yellow',
    archived: 'gray',
};
const categoryColorMap = {
    Policies: 'blue',
    Shipping: 'violet',
    Products: 'teal',
    Sales: 'orange',
    Services: 'pink',
    FAQ: 'cyan',
    Custom: 'gray',
};
/** Derive a display-friendly category from entryType when category is null. */
const entryTypeToCategory = {
    faq: 'FAQ',
    product: 'Products',
    policy: 'Policies',
    custom: 'Custom',
};
/** Normalize legacy singular category names to canonical plural forms. */
const normalizeCategory = {
    Product: 'Products',
    Policy: 'Policies',
};
const stalenessColorMap = {
    fresh: 'green',
    aging: 'yellow',
    stale: 'red',
    very_stale: 'red',
};
const stalenessLabelMap = {
    fresh: 'Fresh',
    aging: 'Aging',
    stale: 'Stale',
    very_stale: 'Very stale',
};
// ---------------------------------------------------------------------------
// Icons as inline SVGs
// ---------------------------------------------------------------------------
const EditIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("path", { d: "M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" }), _jsx("path", { d: "M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" })] }));
const ArchiveIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("polyline", { points: "21 8 21 21 3 21 3 8" }), _jsx("rect", { x: "1", y: "3", width: "22", height: "5" }), _jsx("line", { x1: "10", y1: "12", x2: "14", y2: "12" })] }));
const RestoreIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("polyline", { points: "1 4 1 10 7 10" }), _jsx("path", { d: "M3.51 15a9 9 0 1 0 2.13-9.36L1 10" })] }));
const PlusIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("line", { x1: "12", y1: "5", x2: "12", y2: "19" }), _jsx("line", { x1: "5", y1: "12", x2: "19", y2: "12" })] }));
const SearchIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("circle", { cx: "11", cy: "11", r: "8" }), _jsx("line", { x1: "21", y1: "21", x2: "16.65", y2: "16.65" })] }));
const UploadIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("path", { d: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" }), _jsx("polyline", { points: "17 8 12 3 7 8" }), _jsx("line", { x1: "12", y1: "3", x2: "12", y2: "15" })] }));
const DownloadIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("path", { d: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" }), _jsx("polyline", { points: "7 10 12 15 17 10" }), _jsx("line", { x1: "12", y1: "15", x2: "12", y2: "3" })] }));
const CheckIcon = () => (_jsx("svg", { width: "14", height: "14", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: _jsx("polyline", { points: "20 6 9 17 4 12" }) }));
const ScanIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("path", { d: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" }), _jsx("line", { x1: "12", y1: "8", x2: "12", y2: "12" }), _jsx("line", { x1: "12", y1: "16", x2: "12.01", y2: "16" })] }));
const AlertTriangleIcon = () => (_jsxs("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round", children: [_jsx("path", { d: "M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" }), _jsx("line", { x1: "12", y1: "9", x2: "12", y2: "13" }), _jsx("line", { x1: "12", y1: "17", x2: "12.01", y2: "17" })] }));
const severityColorMap = {
    high: 'red',
    medium: 'orange',
    low: 'yellow',
};
const conflictTypeLabel = {
    near_duplicate: 'Near duplicate',
    conflicting: 'Conflicting information',
    topical_overlap: 'Topical overlap',
    similar_titles: 'Similar titles',
};
const emptyForm = {
    title: '',
    category: 'Policies',
    content: '',
    status: 'draft',
};
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatDate(iso) {
    if (!iso)
        return '--';
    try {
        return new Date(iso).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    }
    catch {
        return iso;
    }
}
// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------
export const KnowledgeBasePage = () => {
    const { apiFetch, onNotify, refreshActivationStatus } = useAppContext();
    // Policy overrides — config fields that live on this page
    const configResult = useConfig(apiFetch);
    const { updateConfig: saveConfigFields, loading: savingPolicy } = useUpdateConfig(apiFetch);
    const [returnWindow, setReturnWindow] = useState(30);
    const [refundPolicy, setRefundPolicy] = useState('');
    const [shippingPolicy, setShippingPolicy] = useState('');
    const policyInitRef = useRef(false);
    // Sync policy fields from server config on load
    React.useEffect(() => {
        if (configResult.data && !policyInitRef.current) {
            const cfg = configResult.data.config ?? configResult.data;
            setReturnWindow(cfg.return_window ?? cfg.returnWindow ?? 30);
            setRefundPolicy(cfg.return_policy ?? cfg.refundPolicy ?? '');
            setShippingPolicy(cfg.shipping_info ?? cfg.shippingPolicy ?? '');
            policyInitRef.current = true;
        }
    }, [configResult.data]);
    // Config-vs-KB conflict warnings (SPEC-1715)
    const [configConflicts, setConfigConflicts] = useState([]);
    /** Fire-and-forget config-vs-KB conflict check (SPEC-1715). */
    const checkConfigConflicts = useCallback(() => {
        const policyFields = {
            returnPolicy: refundPolicy,
            shippingInfo: shippingPolicy,
        };
        if (!Object.values(policyFields).some((v) => v))
            return;
        apiFetch('/api/admin/knowledge/scan/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(policyFields),
        })
            .then((r) => r.ok ? r.json() : null)
            .then((data) => {
            if (data?.conflicts?.length) {
                setConfigConflicts(data.conflicts.map((c) => ({
                    configField: c.configField,
                    configValue: c.configValue,
                    articleTitle: c.articleTitle,
                    conflictingFacts: c.conflictingFacts || [],
                })));
            }
            else {
                setConfigConflicts([]);
            }
        })
            .catch(() => { });
    }, [apiFetch, refundPolicy, shippingPolicy]);
    const savePolicyOverrides = useCallback(async () => {
        const changes = {
            return_window: returnWindow,
            return_policy: refundPolicy,
            shipping_info: shippingPolicy,
        };
        const result = await saveConfigFields(changes);
        if (result?.success) {
            refreshActivationStatus?.();
            checkConfigConflicts(); // SPEC-1715: fire-and-forget
            return true;
        }
        return false;
    }, [returnWindow, refundPolicy, shippingPolicy, saveConfigFields, refreshActivationStatus, checkConfigConflicts]);
    const { onBlur: policyOnBlur, saveCount: policySaveCount } = useAutoSaveDraft({
        save: savePolicyOverrides,
    });
    // API hooks
    const kbResult = useKnowledgeBase(apiFetch);
    const articles = kbResult.data?.articles ?? [];
    const { save, loading: saving, error: saveError } = useSaveKBArticle(apiFetch);
    const { upload: uploadFile, loading: uploading, error: uploadError, progress: uploadProgress, reset: resetUpload } = useUploadFile(apiFetch);
    const { importUrl, loading: importing, error: importError } = useImportUrl(apiFetch);
    const { exportCSV, loading: exporting } = useExportCSV(apiFetch);
    // Staleness hooks
    const { data: stalenessData, refetch: refetchStaleness } = useStalenessSummary(apiFetch);
    const { verify, loading: verifying } = useVerifyEntry(apiFetch);
    // Ingestion & template hooks (KA-7)
    const ingestionStatus = useIngestionStatus(apiFetch);
    const templatesResult = useTemplates(apiFetch);
    const { start: startIngestion, loading: startingIngestion } = useStartIngestion(apiFetch);
    const { cancel: cancelIngestion, loading: cancellingIngestion } = useCancelIngestion(apiFetch);
    const { apply: applyTemplate, loading: applyingTemplate, error: applyTemplateError } = useApplyTemplate(apiFetch);
    const [showAutomation, setShowAutomation] = useState(false);
    // Local UI state
    const [search, setSearch] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('All');
    const [statusFilter, setStatusFilter] = useState('All');
    const [hideArchived, setHideArchived] = useState(true);
    const [sortColumn, setSortColumn] = useState('updatedAt');
    const [sortDirection, setSortDirection] = useState('desc');
    const [modalOpened, { open: openModal, close: closeModal }] = useDisclosure(false);
    const [importModalOpened, { open: openImportModal, close: closeImportModal }] = useDisclosure(false);
    const [editingArticle, setEditingArticle] = useState(null);
    const [form, setForm] = useState(emptyForm);
    const [importUrl2, setImportUrl2] = useState('');
    const [uploadResult, setUploadResult] = useState(null);
    const [dragOver, setDragOver] = useState(false);
    const fileInputRef = useRef(null);
    // Conflict scan state
    const [scanModalOpened, { open: openScanModal, close: closeScanModal }] = useDisclosure(false);
    const [scanning, setScanning] = useState(false);
    const [scanResult, setScanResult] = useState(null);
    const [scanError, setScanError] = useState(null);
    // Filter articles
    /** Resolve display category: explicit category (normalized) → entryType fallback → null. */
    const resolveCategory = useCallback((a) => {
        const raw = a.category || entryTypeToCategory[a.entryType ?? ''] || null;
        return raw ? (normalizeCategory[raw] || raw) : null;
    }, []);
    /** Resolve display status: explicit status → isActive fallback. */
    const resolveStatus = useCallback((a) => a.status || (a.is_active === false ? 'archived' : 'draft'), []);
    const handleSortToggle = useCallback((column) => {
        setSortColumn((prev) => {
            if (prev === column) {
                setSortDirection((d) => (d === 'asc' ? 'desc' : 'asc'));
                return prev;
            }
            setSortDirection(column === 'updatedAt' ? 'desc' : 'asc');
            return column;
        });
    }, []);
    const filteredArticles = useMemo(() => {
        const filtered = articles.filter((article) => {
            const matchesSearch = search === '' ||
                (article.title ?? '').toLowerCase().includes(search.toLowerCase()) ||
                (article.content ?? '').toLowerCase().includes(search.toLowerCase());
            const cat = resolveCategory(article);
            const matchesCategory = !categoryFilter || categoryFilter === 'All' || cat === categoryFilter;
            const st = resolveStatus(article);
            const matchesStatus = !statusFilter ||
                statusFilter === 'All' ||
                st === statusFilter.toLowerCase();
            const matchesArchived = !hideArchived || st !== 'archived';
            return matchesSearch && matchesCategory && matchesStatus && matchesArchived;
        });
        // Sort
        const dir = sortDirection === 'asc' ? 1 : -1;
        filtered.sort((a, b) => {
            let aVal;
            let bVal;
            switch (sortColumn) {
                case 'title':
                    aVal = (a.title ?? '').toLowerCase();
                    bVal = (b.title ?? '').toLowerCase();
                    break;
                case 'category':
                    aVal = (resolveCategory(a) ?? '').toLowerCase();
                    bVal = (resolveCategory(b) ?? '').toLowerCase();
                    break;
                case 'status':
                    aVal = resolveStatus(a).toLowerCase();
                    bVal = resolveStatus(b).toLowerCase();
                    break;
                case 'freshness':
                    aVal = (a.stalenessCategory ?? '').toLowerCase();
                    bVal = (b.stalenessCategory ?? '').toLowerCase();
                    break;
                case 'updatedAt': {
                    const aTime = a.updatedAt ? new Date(a.updatedAt).getTime() : 0;
                    const bTime = b.updatedAt ? new Date(b.updatedAt).getTime() : 0;
                    return (aTime - bTime) * dir;
                }
                default:
                    return 0;
            }
            return aVal < bVal ? -dir : aVal > bVal ? dir : 0;
        });
        return filtered;
    }, [articles, search, categoryFilter, statusFilter, hideArchived, sortColumn, sortDirection, resolveCategory, resolveStatus]);
    // Summary stats
    const stats = useMemo(() => {
        const published = articles.filter((a) => resolveStatus(a) === 'published').length;
        const draft = articles.filter((a) => resolveStatus(a) === 'draft').length;
        const archived = articles.filter((a) => resolveStatus(a) === 'archived').length;
        return { total: articles.length, published, draft, archived };
    }, [articles, resolveStatus]);
    // Handlers
    const handleAddArticle = () => {
        setEditingArticle(null);
        setForm(emptyForm);
        openModal();
    };
    const handleEditArticle = (article) => {
        setEditingArticle(article);
        setForm({
            title: article.title ?? '',
            category: article.category ?? 'Policies',
            content: article.content ?? '',
            status: article.status ?? 'draft',
        });
        openModal();
    };
    const handleArchiveArticle = async (article) => {
        const result = await save({ ...article, status: 'archived' });
        if (result) {
            onNotify(`"${article.title}" archived`, 'success');
            kbResult.refetch();
        }
        else {
            onNotify(saveError || 'Failed to archive article', 'error');
        }
    };
    const handleRestoreArticle = async (article) => {
        const result = await save({ ...article, status: 'draft' });
        if (result) {
            onNotify(`"${article.title}" restored as Draft`, 'success');
            kbResult.refetch();
        }
        else {
            onNotify(saveError || 'Failed to restore article', 'error');
        }
    };
    const handleSave = async () => {
        const articleData = {
            title: form.title,
            category: form.category,
            content: form.content,
            status: form.status,
            entryType: 'article',
        };
        if (editingArticle)
            articleData.id = editingArticle.id;
        const result = await save(articleData);
        if (result) {
            onNotify(editingArticle ? 'Article updated successfully' : 'Article created successfully', 'success');
            kbResult.refetch();
            checkConfigConflicts(); // SPEC-1715: re-check after article change
            closeModal();
        }
        else {
            onNotify(saveError || 'Failed to save article', 'error');
        }
    };
    const handleVerify = useCallback(async (entryId) => {
        const result = await verify(entryId);
        if (result) {
            onNotify('Article verified as current', 'success');
            kbResult.refetch();
            refetchStaleness();
        }
        else {
            onNotify('Failed to verify article', 'error');
        }
    }, [verify, onNotify, kbResult, refetchStaleness]);
    const handleOpenImport = useCallback(() => {
        setUploadResult(null);
        resetUpload();
        setImportUrl2('');
        openImportModal();
    }, [resetUpload, openImportModal]);
    const handleFileUpload = useCallback(async (file) => {
        const result = await uploadFile(file);
        if (result) {
            setUploadResult(result);
            onNotify(`Imported ${result.entries_created} entries from ${file.name}`, 'success');
        }
        else {
            onNotify('File upload failed', 'error');
        }
    }, [uploadFile, onNotify]);
    const handleFileDrop = useCallback((e) => {
        e.preventDefault();
        setDragOver(false);
        if (uploading)
            return;
        const file = e.dataTransfer.files?.[0];
        if (file)
            handleFileUpload(file);
    }, [handleFileUpload, uploading]);
    const handleFileInputChange = useCallback((e) => {
        const file = e.target.files?.[0];
        if (file)
            handleFileUpload(file);
        if (fileInputRef.current)
            fileInputRef.current.value = '';
    }, [handleFileUpload]);
    const handleUrlImport = useCallback(async () => {
        const trimmed = importUrl2.trim();
        if (!trimmed)
            return;
        const result = await importUrl(trimmed);
        if (result) {
            setUploadResult(result);
            onNotify(`Imported ${result.entries_created} entries from URL`, 'success');
        }
        else {
            onNotify('URL import failed', 'error');
        }
    }, [importUrl2, importUrl, onNotify]);
    const handleImportDone = useCallback(() => {
        setUploadResult(null);
        closeImportModal();
        kbResult.refetch();
    }, [closeImportModal, kbResult]);
    const handleExport = useCallback(async () => {
        const ok = await exportCSV();
        if (ok) {
            onNotify('Knowledge base exported as CSV', 'success');
        }
        else {
            onNotify('Export failed', 'error');
        }
    }, [exportCSV, onNotify]);
    const handleScan = useCallback(async (force = false) => {
        setScanning(true);
        setScanError(null);
        try {
            const qs = force ? '?force=true' : '';
            const resp = await apiFetch(`/api/admin/knowledge/scan${qs}`, { method: 'POST' });
            if (resp.ok) {
                const data = await resp.json();
                setScanResult(data);
                openScanModal();
                const total = data.highCount + data.mediumCount + data.lowCount;
                if (total > 0) {
                    onNotify(`Scan found ${total} issue${total === 1 ? '' : 's'} (${data.highCount} high, ${data.mediumCount} medium, ${data.lowCount} low)`, 'warning');
                }
                else {
                    onNotify('No conflicts or duplicates found', 'success');
                }
            }
            else if (resp.status === 503) {
                setScanError('Conflict scanner is not available. This feature requires embedding support.');
                onNotify('Conflict scanner not available', 'error');
            }
            else {
                const text = await resp.text().catch(() => 'Unknown error');
                setScanError(text);
                onNotify('Scan failed', 'error');
            }
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Network error';
            setScanError(msg);
            onNotify('Scan failed: ' + msg, 'error');
        }
        finally {
            setScanning(false);
        }
    }, [apiFetch, onNotify, openScanModal]);
    // Loading state
    if (kbResult.loading && articles.length === 0) {
        return _jsx(LoadingState, { text: "Loading knowledge base" });
    }
    // Error state
    if (kbResult.error && articles.length === 0) {
        return (_jsxs(Stack, { gap: "lg", children: [_jsxs("div", { children: [_jsx(Title, { order: 2, children: "Knowledge base" }), _jsx(Text, { c: "dimmed", size: "sm", children: "Manage articles your AI uses to answer customers" })] }), _jsxs(Paper, { p: "xl", radius: "md", withBorder: true, children: [_jsxs(Text, { c: "red", ta: "center", children: ["Failed to load knowledge base: ", kbResult.error] }), _jsx(Center, { mt: "md", children: _jsx(Button, { variant: "default", onClick: kbResult.refetch, children: "Retry" }) })] })] }));
    }
    return (_jsxs(Stack, { gap: "lg", children: [_jsxs("div", { children: [_jsx(Title, { order: 2, children: "Knowledge base" }), _jsx(Text, { c: "dimmed", size: "sm", children: "Manage articles your AI uses to answer customers" })] }), configConflicts.length > 0 && (_jsxs(Alert, { color: "yellow", variant: "light", title: "Policy conflicts with knowledge base articles", withCloseButton: true, onClose: () => setConfigConflicts([]), children: [_jsx(Text, { size: "sm", mb: "xs", children: "Policy override values conflict with knowledge base articles below. Policies take priority, but consider updating the conflicting articles." }), configConflicts.map((c, i) => (_jsxs(Text, { size: "sm", c: "dimmed", mb: 2, children: [_jsx(Text, { span: true, fw: 600, c: "dark", children: c.configField }), " conflicts with article \"", c.articleTitle, "\"", c.conflictingFacts.length > 0 && ` — ${c.conflictingFacts[0]}`] }, i)))] })), _jsxs(Paper, { p: "lg", radius: "md", withBorder: true, onBlur: policyOnBlur, children: [_jsxs(Group, { justify: "space-between", mb: "md", children: [_jsxs(Text, { fw: 600, children: ["Policy overrides ", _jsx(HelpTooltip, { text: "These policy values take priority over knowledge base articles when the AI responds to customers.", docLink: "/docs/business-policies" })] }), _jsx(AutoSaveIndicator, { saveCount: policySaveCount })] }), _jsxs(Stack, { gap: "md", children: [_jsx(NumberInput, { label: "Return window", suffix: " days", value: returnWindow, onChange: (val) => setReturnWindow(Number(val) || 30), min: 0, max: 365 }), _jsx(Textarea, { label: "Refund policy", placeholder: "Describe your refund policy...", value: refundPolicy, onChange: (e) => setRefundPolicy(e.currentTarget.value), minRows: 3, autosize: true }), _jsx(Textarea, { label: "Shipping policy", placeholder: "Describe your shipping policy...", value: shippingPolicy, onChange: (e) => setShippingPolicy(e.currentTarget.value), minRows: 3, autosize: true })] }), _jsx(Text, { size: "xs", c: "dimmed", mt: "sm", children: "These values take priority over knowledge base articles. Changes save automatically." })] }), _jsx(Paper, { p: "md", radius: "md", withBorder: true, children: _jsxs(Stack, { gap: "sm", children: [_jsx(TextInput, { placeholder: "Search articles...", leftSection: _jsx(SearchIcon, {}), value: search, onChange: (e) => setSearch(e.currentTarget.value), style: { maxWidth: 360 } }), _jsxs(Group, { justify: "space-between", wrap: "wrap", gap: "sm", align: "flex-end", children: [_jsxs(Group, { gap: "sm", wrap: "wrap", align: "flex-end", children: [_jsx(Select, { placeholder: "Category", data: CATEGORIES, value: categoryFilter, onChange: setCategoryFilter, clearable: false, w: 160 }), _jsx(Select, { placeholder: "Status", data: STATUSES, value: statusFilter, onChange: setStatusFilter, clearable: false, w: 140 }), _jsx(Switch, { label: "Hide archived", checked: hideArchived, onChange: (e) => setHideArchived(e.currentTarget.checked), size: "sm", styles: { label: { paddingLeft: 8 } } })] }), _jsxs(Group, { gap: "sm", children: [_jsx(Tooltip, { label: "Detect duplicate, overlapping, or contradictory entries that may cause inconsistent AI responses", multiline: true, w: 260, withArrow: true, children: _jsx(Button, { leftSection: _jsx(ScanIcon, {}), variant: "default", onClick: () => handleScan(false), loading: scanning, disabled: articles.length === 0, children: "Scan for conflicts" }) }), _jsx(Tooltip, { label: "Download all knowledge base entries as a CSV file for backup or editing", multiline: true, w: 220, withArrow: true, children: _jsx(Button, { leftSection: _jsx(DownloadIcon, {}), variant: "default", onClick: handleExport, loading: exporting, disabled: articles.length === 0, children: "Export CSV" }) }), _jsx(Tooltip, { label: "Upload PDF, DOCX, CSV, or TXT files, or import from a URL to bulk-create entries", multiline: true, w: 240, withArrow: true, children: _jsx(Button, { leftSection: _jsx(UploadIcon, {}), variant: "default", onClick: handleOpenImport, children: "Import" }) }), _jsx(Tooltip, { label: "Create a new knowledge base article. Articles give your AI specific information to reference when answering customer questions.", multiline: true, w: 260, withArrow: true, children: _jsx(Button, { leftSection: _jsx(PlusIcon, {}), color: ACTION_BLUE, onClick: handleAddArticle, children: "Add article" }) })] })] })] }) }), _jsxs(SimpleGrid, { cols: { base: 2, xs: 5 }, spacing: "md", children: [_jsxs(Paper, { p: "md", radius: "md", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, mb: 4, children: "Total articles" }), _jsx(Text, { size: "xl", fw: 700, lh: 1, children: stats.total })] }), _jsxs(Paper, { p: "md", radius: "md", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, mb: 4, children: "Published" }), _jsx(Text, { size: "xl", fw: 700, lh: 1, c: "green", children: stats.published })] }), _jsxs(Paper, { p: "md", radius: "md", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, mb: 4, children: "Draft" }), _jsx(Text, { size: "xl", fw: 700, lh: 1, c: "yellow.7", children: stats.draft })] }), _jsxs(Paper, { p: "md", radius: "md", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, mb: 4, children: "Archived" }), _jsx(Text, { size: "xl", fw: 700, lh: 1, c: "dimmed", children: stats.archived })] }), _jsx(Tooltip, { label: "Articles marked stale or very stale that should be reviewed for accuracy", multiline: true, w: 240, withArrow: true, children: _jsxs(Paper, { p: "md", radius: "md", withBorder: true, style: { cursor: 'help' }, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, mb: 4, children: "Needs attention" }), _jsx(Text, { size: "xl", fw: 700, lh: 1, c: "red", children: (stalenessData?.staleCount ?? 0) + (stalenessData?.veryStaleCount ?? 0) })] }) })] }), _jsxs(Paper, { p: "md", radius: "md", withBorder: true, children: [_jsxs(Group, { justify: "space-between", mb: showAutomation ? 'md' : 0, children: [_jsxs(Group, { gap: "xs", children: [_jsx(Text, { fw: 600, children: "Knowledge automation" }), _jsx(Badge, { size: "xs", variant: "light", color: "violet", children: "Beta" })] }), _jsx(Button, { variant: "subtle", size: "xs", onClick: () => setShowAutomation((prev) => !prev), children: showAutomation ? 'Hide' : 'Show' })] }), !showAutomation && (_jsx(Text, { size: "xs", c: "dimmed", mt: "xs", children: "Import content from your storefront or apply industry templates to quickly build your knowledge base." })), showAutomation && (_jsxs(Stack, { gap: "lg", children: [_jsxs("div", { children: [_jsxs(Group, { gap: "xs", mb: "sm", children: [_jsx(Text, { fw: 500, size: "sm", children: "Storefront import" }), _jsx(Tooltip, { label: "Scan your storefront to import product descriptions, policies, and FAQ content as knowledge base articles.", multiline: true, w: 280, withArrow: true, children: _jsx(Badge, { size: "xs", variant: "light", color: "gray", style: { cursor: 'help' }, children: "?" }) })] }), _jsxs(Group, { gap: "sm", mb: "sm", children: [_jsx(Button, { size: "xs", color: ACTION_BLUE, onClick: () => startIngestion('shopify'), loading: startingIngestion, disabled: ingestionStatus.data?.status === 'running' || ingestionStatus.data?.status === 'pending', children: "Scan storefront" }), _jsx(Button, { size: "xs", variant: "default", onClick: () => ingestionStatus.refetch(), children: "Refresh status" })] }), _jsx(IngestionPanel, { job: ingestionStatus.data ?? null, loading: ingestionStatus.loading, onCancel: cancelIngestion, cancelLoading: cancellingIngestion, onRefresh: ingestionStatus.refetch })] }), _jsxs("div", { children: [_jsxs(Group, { gap: "xs", mb: "sm", children: [_jsx(Text, { fw: 500, size: "sm", children: "Industry templates" }), _jsx(Tooltip, { label: "Pre-built article sets for common Shopify merchant categories. Provides starter FAQ articles, policy templates, and glossary terms.", multiline: true, w: 280, withArrow: true, children: _jsx(Badge, { size: "xs", variant: "light", color: "gray", style: { cursor: 'help' }, children: "?" }) })] }), _jsx(CategoryTemplateSelector, { templates: templatesResult.data ?? null, loading: templatesResult.loading, error: templatesResult.error, onApply: async (categoryId) => {
                                            const result = await applyTemplate(categoryId);
                                            if (result) {
                                                kbResult.refetch();
                                                refetchStaleness();
                                                onNotify(`Template applied — ${result.articlesCreated} articles created.`, 'success');
                                            }
                                            return result;
                                        }, applyLoading: applyingTemplate, applyError: applyTemplateError })] })] }))] }), _jsx(Paper, { p: "md", radius: "md", withBorder: true, children: _jsxs(Table, { striped: true, highlightOnHover: true, children: [_jsx(Table.Thead, { children: _jsxs(Table.Tr, { children: [[
                                        ['title', 'Title'],
                                        ['category', 'Category'],
                                        ['status', 'Status'],
                                        ['freshness', 'Freshness'],
                                        ['updatedAt', 'Last updated'],
                                    ].map(([col, label]) => (_jsxs(Table.Th, { onClick: () => handleSortToggle(col), style: { cursor: 'pointer', userSelect: 'none', whiteSpace: 'nowrap' }, children: [label, ' ', sortColumn === col
                                                ? sortDirection === 'asc'
                                                    ? '\u25B2'
                                                    : '\u25BC'
                                                : '\u25B2\u25BC'] }, col))), _jsx(Table.Th, { style: { textAlign: 'right' }, children: "Actions" })] }) }), _jsxs(Table.Tbody, { children: [filteredArticles.map((article) => (_jsxs(Table.Tr, { style: resolveStatus(article) === 'archived' ? { opacity: 0.5 } : undefined, children: [_jsx(Table.Td, { children: _jsx(Text, { size: "sm", fw: 500, td: resolveStatus(article) === 'archived' ? 'line-through' : undefined, children: article.title }) }), _jsx(Table.Td, { children: (() => {
                                                const cat = resolveCategory(article);
                                                return cat ? (_jsx(Badge, { size: "sm", variant: "light", color: categoryColorMap[cat] || 'gray', children: cat })) : (_jsx(Text, { size: "xs", c: "dimmed", children: "--" }));
                                            })() }), _jsx(Table.Td, { children: (() => {
                                                const st = article.status || (article.is_active === false ? 'archived' : 'draft');
                                                return (_jsx(Badge, { size: "sm", variant: "light", color: statusColorMap[st] || 'gray', children: st }));
                                            })() }), _jsx(Table.Td, { children: _jsx(Badge, { size: "sm", variant: "light", color: stalenessColorMap[article.stalenessCategory ?? ''] || 'gray', children: stalenessLabelMap[article.stalenessCategory ?? ''] || '--' }) }), _jsx(Table.Td, { children: _jsx(Text, { size: "sm", c: "dimmed", children: formatDate(article.updatedAt) }) }), _jsx(Table.Td, { children: _jsxs(Group, { gap: 4, justify: "flex-end", wrap: "nowrap", children: [(article.stalenessCategory === 'stale' || article.stalenessCategory === 'aging' || article.stalenessCategory === 'very_stale') && (_jsx(Tooltip, { label: "Mark as verified", withArrow: true, children: _jsx(ActionIcon, { variant: "subtle", color: "green", size: "sm", onClick: () => handleVerify(article.id), loading: verifying, children: _jsx(CheckIcon, {}) }) })), _jsx(Tooltip, { label: "Edit article", withArrow: true, children: _jsx(ActionIcon, { variant: "subtle", color: "gray", size: "sm", onClick: () => handleEditArticle(article), children: _jsx(EditIcon, {}) }) }), resolveStatus(article) === 'archived' ? (_jsx(Tooltip, { label: "Restore article", withArrow: true, children: _jsx(ActionIcon, { variant: "subtle", color: "blue", size: "sm", onClick: () => handleRestoreArticle(article), loading: saving, children: _jsx(RestoreIcon, {}) }) })) : (_jsx(Tooltip, { label: "Archive article", withArrow: true, children: _jsx(ActionIcon, { variant: "subtle", color: "gray", size: "sm", onClick: () => handleArchiveArticle(article), loading: saving, children: _jsx(ArchiveIcon, {}) }) }))] }) })] }, article.id))), filteredArticles.length === 0 && (_jsx(Table.Tr, { children: _jsx(Table.Td, { colSpan: 6, children: _jsx(Text, { ta: "center", c: "dimmed", py: "xl", children: "No articles match your filters." }) }) }))] })] }) }), _jsx(Modal, { opened: modalOpened, onClose: closeModal, title: _jsx(Text, { fw: 600, size: "lg", children: editingArticle ? 'Edit article' : 'Add article' }), size: "lg", radius: "md", children: _jsxs(Stack, { gap: "md", children: [_jsx(TextInput, { label: "Title", placeholder: "Article title", value: form.title, onChange: (e) => setForm((f) => ({ ...f, title: e.currentTarget.value })), required: true }), _jsx(Select, { label: "Category", data: CATEGORIES.filter((c) => c !== 'All'), value: form.category, onChange: (val) => setForm((f) => ({ ...f, category: val || 'Policies' })), required: true }), _jsx(Textarea, { label: "Content", placeholder: "Write the article content here...", value: form.content, onChange: (e) => setForm((f) => ({ ...f, content: e.currentTarget.value })), minRows: 8, autosize: true, maxRows: 16, required: true }), _jsx(Select, { label: "Status", data: [{ value: 'published', label: 'Published' }, { value: 'draft', label: 'Draft' }, { value: 'archived', label: 'Archived' }], value: form.status, onChange: (val) => setForm((f) => ({ ...f, status: val || 'draft' })), required: true }), saveError && _jsx(Text, { size: "sm", c: "red", children: saveError }), _jsxs(Group, { justify: "flex-end", mt: "md", children: [_jsx(Button, { variant: "default", onClick: closeModal, children: "Cancel" }), _jsx(Button, { color: ACTION_BLUE, onClick: handleSave, disabled: !form.title.trim() || !form.content.trim(), loading: saving, children: editingArticle ? 'Save changes' : 'Create article' })] })] }) }), _jsx(Modal, { opened: importModalOpened, onClose: () => { closeImportModal(); setUploadResult(null); }, title: _jsx(Text, { fw: 600, size: "lg", children: "Import content" }), size: "lg", radius: "md", children: uploadResult ? (_jsxs(Stack, { gap: "md", ta: "center", py: "lg", children: [_jsx(Text, { size: "xl", children: String.fromCodePoint(0x2705) }), _jsx(Title, { order: 3, children: "Import successful" }), _jsxs(Text, { c: "dimmed", children: ["Created ", uploadResult.entries_created, " ", uploadResult.entries_created === 1 ? 'entry' : 'entries', " from", ' ', uploadResult.source_filename || uploadResult.source_url || 'document', ' ', "(", Math.round(uploadResult.total_chars / 1000), "K characters)"] }), _jsx(Group, { justify: "center", mt: "md", children: _jsx(Button, { color: ACTION_BLUE, onClick: handleImportDone, children: "Back to knowledge base" }) })] })) : (_jsxs(Tabs, { defaultValue: "file", children: [_jsxs(Tabs.List, { mb: "lg", children: [_jsx(Tabs.Tab, { value: "file", children: "Upload file" }), _jsx(Tabs.Tab, { value: "url", children: "Import URL" })] }), _jsx(Tabs.Panel, { value: "file", children: _jsxs(Stack, { gap: "md", children: [_jsx("input", { ref: fileInputRef, type: "file", accept: ACCEPTED_FILE_TYPES, onChange: handleFileInputChange, style: { display: 'none' } }), _jsx(Paper, { p: "xl", radius: "md", withBorder: true, onDragOver: (e) => { e.preventDefault(); setDragOver(true); }, onDragLeave: () => setDragOver(false), onDrop: handleFileDrop, onClick: () => !uploading && fileInputRef.current?.click(), style: {
                                            cursor: uploading ? 'default' : 'pointer',
                                            borderStyle: 'dashed',
                                            borderColor: dragOver ? BRAND_RED : undefined,
                                            backgroundColor: dragOver ? `${BRAND_RED}08` : undefined,
                                            textAlign: 'center',
                                            opacity: uploading ? 0.7 : 1,
                                            transition: 'all 0.2s ease',
                                        }, children: uploading ? (_jsxs(Stack, { gap: "sm", align: "center", children: [_jsx(Loader, { size: "sm", color: BRAND_RED }), _jsx(Text, { size: "sm", fw: 500, children: uploadProgress === 'uploading' ? 'Uploading...' : 'Processing document...' }), _jsx(Progress, { value: uploadProgress === 'uploading' ? 40 : 80, color: BRAND_RED, w: 200, size: "xs", animated: true })] })) : (_jsxs(Stack, { gap: "xs", align: "center", children: [_jsx(Text, { size: "xl", children: String.fromCodePoint(0x1F4C4) }), _jsx(Text, { size: "sm", fw: 500, children: "Drop a file here or click to browse" }), _jsx(Text, { size: "xs", c: "dimmed", children: "Supported: PDF, DOCX, CSV, TXT (max 50MB)" })] })) }), uploadError && _jsx(Text, { size: "sm", c: "red", children: uploadError })] }) }), _jsx(Tabs.Panel, { value: "url", children: _jsxs(Stack, { gap: "md", children: [_jsx(TextInput, { label: "Website URL", placeholder: "https://example.com/faq", value: importUrl2, onChange: (e) => setImportUrl2(e.currentTarget.value), disabled: importing }), _jsx(Text, { size: "xs", c: "dimmed", children: "We'll extract text content from the page and create knowledge base entries." }), importError && _jsx(Text, { size: "sm", c: "red", children: importError }), _jsx(Group, { justify: "flex-end", children: _jsx(Button, { color: ACTION_BLUE, onClick: handleUrlImport, disabled: !importUrl2.trim(), loading: importing, children: "Import" }) })] }) })] })) }), _jsxs(Modal, { opened: scanModalOpened, onClose: closeScanModal, title: _jsx(Text, { fw: 600, size: "lg", children: "Conflict scan results" }), size: "xl", radius: "md", children: [scanError && (_jsx(Alert, { color: "red", title: "Scan error", mb: "md", children: scanError })), scanResult && (_jsxs(Stack, { gap: "md", children: [_jsxs(SimpleGrid, { cols: { base: 2, xs: 4 }, spacing: "sm", children: [_jsxs(Paper, { p: "sm", radius: "md", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, children: "Entries scanned" }), _jsx(Text, { size: "lg", fw: 700, children: scanResult.totalEntriesScanned })] }), _jsxs(Paper, { p: "sm", radius: "md", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, children: "With embeddings" }), _jsx(Text, { size: "lg", fw: 700, children: scanResult.entriesWithEmbeddings })] }), _jsxs(Paper, { p: "sm", radius: "md", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, children: "Scan time" }), _jsx(Text, { size: "lg", fw: 700, children: scanResult.scanDurationMs < 1000 ? `${scanResult.scanDurationMs}ms` : `${(scanResult.scanDurationMs / 1000).toFixed(1)}s` })] }), _jsxs(Paper, { p: "sm", radius: "md", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, children: "Issues found" }), _jsx(Text, { size: "lg", fw: 700, c: scanResult.highCount > 0 ? 'red' : scanResult.mediumCount > 0 ? 'orange' : 'green', children: scanResult.highCount + scanResult.mediumCount + scanResult.lowCount })] })] }), (scanResult.highCount > 0 || scanResult.mediumCount > 0 || scanResult.lowCount > 0) && (_jsxs(Group, { gap: "sm", children: [scanResult.highCount > 0 && (_jsxs(Badge, { size: "lg", color: "red", variant: "light", children: [scanResult.highCount, " high severity"] })), scanResult.mediumCount > 0 && (_jsxs(Badge, { size: "lg", color: "orange", variant: "light", children: [scanResult.mediumCount, " medium"] })), scanResult.lowCount > 0 && (_jsxs(Badge, { size: "lg", color: "yellow", variant: "light", children: [scanResult.lowCount, " low"] }))] })), scanResult.conflicts.length === 0 && (_jsx(Alert, { color: "green", title: "All clear", variant: "light", children: "No conflicts, duplicates, or overlapping content detected in your knowledge base." })), scanResult.conflicts.length > 0 && (_jsx(Accordion, { variant: "separated", radius: "md", children: scanResult.conflicts.map((conflict, idx) => (_jsxs(Accordion.Item, { value: `conflict-${idx}`, children: [_jsx(Accordion.Control, { children: _jsxs(Group, { gap: "sm", wrap: "nowrap", children: [_jsx(Badge, { size: "sm", color: severityColorMap[conflict.severity] || 'gray', variant: "filled", style: { flexShrink: 0 }, children: conflict.severity.toUpperCase() }), _jsx(Badge, { size: "sm", color: "gray", variant: "light", style: { flexShrink: 0 }, children: conflictTypeLabel[conflict.conflictType] || conflict.conflictType }), _jsxs(Text, { size: "sm", truncate: "end", style: { flex: 1 }, children: [conflict.entryATitle, " \u2194 ", conflict.entryBTitle] })] }) }), _jsx(Accordion.Panel, { children: _jsxs(Stack, { gap: "sm", children: [_jsxs(SimpleGrid, { cols: 2, spacing: "sm", children: [_jsxs(Paper, { p: "sm", radius: "sm", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, mb: 4, children: "Article A" }), _jsx(Text, { size: "sm", fw: 500, children: conflict.entryATitle })] }), _jsxs(Paper, { p: "sm", radius: "sm", withBorder: true, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, mb: 4, children: "Article B" }), _jsx(Text, { size: "sm", fw: 500, children: conflict.entryBTitle })] })] }), _jsxs(Group, { gap: "lg", children: [_jsx(Tooltip, { label: "How similar the article content embeddings are (0-1)", children: _jsxs(Text, { size: "xs", c: "dimmed", children: ["Embedding similarity: ", _jsxs(Text, { span: true, fw: 600, children: [(conflict.embeddingSimilarity * 100).toFixed(1), "%"] })] }) }), _jsx(Tooltip, { label: "Percentage of overlapping content between the two articles", children: _jsxs(Text, { size: "xs", c: "dimmed", children: ["Content overlap: ", _jsxs(Text, { span: true, fw: 600, children: [(conflict.contentOverlap * 100).toFixed(1), "%"] })] }) }), _jsx(Tooltip, { label: "How similar the article titles are (0-1)", children: _jsxs(Text, { size: "xs", c: "dimmed", children: ["Title similarity: ", _jsxs(Text, { span: true, fw: 600, children: [(conflict.titleSimilarity * 100).toFixed(1), "%"] })] }) })] }), conflict.conflictingFacts.length > 0 && (_jsx(Alert, { color: "orange", variant: "light", title: "Conflicting facts", icon: _jsx(AlertTriangleIcon, {}), children: _jsx(Stack, { gap: 4, children: conflict.conflictingFacts.map((fact, fi) => (_jsx(Text, { size: "sm", children: fact }, fi))) }) })), _jsxs(Paper, { p: "sm", radius: "sm", style: { backgroundColor: 'var(--mantine-color-dark-7)' }, children: [_jsx(Text, { size: "xs", c: "dimmed", fw: 600, mb: 4, children: "Suggested resolution" }), _jsx(Text, { size: "sm", children: conflict.resolution })] })] }) })] }, `${conflict.entryAId}-${conflict.entryBId}-${idx}`))) })), _jsxs(Group, { justify: "space-between", mt: "sm", children: [_jsxs(Text, { size: "xs", c: "dimmed", children: ["Scanned at ", (() => {
                                                try {
                                                    return new Date(scanResult.scannedAt).toLocaleString();
                                                }
                                                catch {
                                                    return scanResult.scannedAt;
                                                }
                                            })(), scanResult.entriesWithoutEmbeddings > 0 && (_jsxs(_Fragment, { children: [" \u00B7 ", scanResult.entriesWithoutEmbeddings, " entries skipped (no embeddings)"] }))] }), _jsxs(Group, { gap: "sm", children: [_jsx(Button, { variant: "default", size: "sm", onClick: () => handleScan(true), loading: scanning, children: "Re-scan (force)" }), _jsx(Button, { color: ACTION_BLUE, size: "sm", onClick: closeScanModal, children: "Close" })] })] })] }))] })] }));
};
//# sourceMappingURL=KnowledgeBase.js.map