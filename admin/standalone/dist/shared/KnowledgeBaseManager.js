import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * KnowledgeBaseManager - CRUD manager for knowledge base articles.
 *
 * List view: all KB articles with title, category, status badge, last updated.
 * Editor view: title, content textarea, category dropdown, status select.
 * Filtering: category dropdown, status filter, search by title.
 * Actions: create, edit, save, delete.
 *
 * Framework-agnostic React component — no Polaris, no Tailwind, pure inline styles.
 * Receives auth, API fetch, and notification callbacks from the shell.
 *
 * Sub-components and utilities are extracted into ./kb/ for maintainability.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback, useMemo } from 'react';
import { useKnowledgeBase, useSaveKBArticle, useUploadFile, useImportUrl, useExportCSV, useStalenessSummary, useVerifyEntry, useConflictScan } from './hooks';
import { HelpTooltip } from './HelpTooltip';
// Sub-components extracted into ./kb/
import { 
// Style constants & helpers
BRAND_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_GRAY, COLOR_LIGHT_GRAY, COLOR_BORDER, COLOR_WHITE, COLOR_TEXT, COLOR_TEXT_SECONDARY, COLOR_WARNING, FONT_FAMILY, BORDER_RADIUS, inputStyle, buttonStyle, 
// Utilities
extractCategories, FileUploadZone, URLImportForm, UploadResultDisplay, ArticleEditor, ArticleRow, LoadingSpinner, EmptyState, ErrorBanner, WebsiteSourcesPanel, } from './kb';
// ---------------------------------------------------------------------------
// Filter option constants
// ---------------------------------------------------------------------------
const ALL_STATUSES = [
    { value: '', label: 'All statuses' },
    { value: 'draft', label: 'Draft' },
    { value: 'published', label: 'Published' },
    { value: 'archived', label: 'Archived' },
];
// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
export const KnowledgeBaseManager = ({ tenantContext, apiFetch, onNotify, }) => {
    // View state: 'list', 'editor', or 'import'
    const [view, setView] = useState('list');
    const [kbTab, setKbTab] = useState('articles');
    const [editingArticle, setEditingArticle] = useState(null);
    const [deleting, setDeleting] = useState(false);
    const [uploadResult, setUploadResult] = useState(null);
    const [importTab, setImportTab] = useState('file');
    // Filters
    const [searchQuery, setSearchQuery] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    // Data hooks
    const { data: kbData, loading: kbLoading, error: kbError, refetch: refetchKB, } = useKnowledgeBase(apiFetch);
    const articles = kbData?.articles ?? [];
    // Save hook
    const { save, loading: saving, error: saveError } = useSaveKBArticle(apiFetch);
    // Upload/import/export hooks
    const { upload: uploadFile, loading: uploading, error: uploadError, progress: uploadProgress, reset: resetUpload } = useUploadFile(apiFetch);
    const { importUrl, loading: importing, error: importError } = useImportUrl(apiFetch);
    const { exportCSV, loading: exporting, error: exportError } = useExportCSV(apiFetch);
    // Staleness hooks
    const { data: stalenessData, refetch: refetchStaleness } = useStalenessSummary(apiFetch);
    const { verify, loading: verifying } = useVerifyEntry(apiFetch);
    // Conflict scanner hooks
    const { scan: runConflictScan, result: scanResult, loading: scanning, error: scanError } = useConflictScan(apiFetch);
    const [showScanResults, setShowScanResults] = useState(false);
    const [dismissedPairs, setDismissedPairs] = useState(new Set());
    // Extract categories from articles for the filter dropdown and editor
    const categories = useMemo(() => extractCategories(articles), [articles]);
    // Filter articles
    const filteredArticles = useMemo(() => {
        let result = articles;
        if (searchQuery.trim()) {
            const q = searchQuery.trim().toLowerCase();
            result = result.filter((a) => a.title.toLowerCase().includes(q));
        }
        if (categoryFilter) {
            result = result.filter((a) => a.category === categoryFilter);
        }
        if (statusFilter) {
            result = result.filter((a) => a.status === statusFilter);
        }
        return result;
    }, [articles, searchQuery, categoryFilter, statusFilter]);
    // Handlers
    const handleOpenNew = useCallback(() => {
        setEditingArticle({ title: '', content: '', category: '', status: 'draft' });
        setView('editor');
    }, []);
    const handleOpenImport = useCallback(() => {
        setUploadResult(null);
        resetUpload();
        setImportTab('file');
        setView('import');
    }, [resetUpload]);
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
    const handleUrlImport = useCallback(async (url, crawl, maxPages) => {
        const result = await importUrl(url, undefined, crawl, maxPages);
        if (result) {
            setUploadResult(result);
            const label = crawl ? `Crawled and imported ${result.entries_created} entries` : `Imported ${result.entries_created} entries from URL`;
            onNotify(label, 'success');
        }
        else {
            onNotify('URL import failed', 'error');
        }
    }, [importUrl, onNotify]);
    const handleImportDone = useCallback(() => {
        setUploadResult(null);
        setView('list');
        refetchKB();
    }, [refetchKB]);
    const handleExport = useCallback(async () => {
        const ok = await exportCSV();
        if (ok) {
            onNotify('Knowledge base exported as CSV', 'success');
        }
        else {
            onNotify(exportError || 'Export failed', 'error');
        }
    }, [exportCSV, exportError, onNotify]);
    const handleVerify = useCallback(async (entryId) => {
        const result = await verify(entryId);
        if (result) {
            onNotify('Article verified as current', 'success');
            refetchKB();
            refetchStaleness();
        }
        else {
            onNotify('Failed to verify article', 'error');
        }
    }, [verify, onNotify, refetchKB, refetchStaleness]);
    const handleOpenEdit = useCallback((article) => {
        setEditingArticle(article);
        setView('editor');
    }, []);
    const handleCancel = useCallback(() => {
        setEditingArticle(null);
        setView('list');
    }, []);
    const handleSave = useCallback(async (article) => {
        const result = await save(article);
        if (result) {
            onNotify(article.id ? 'Article updated successfully' : 'Article created successfully', 'success');
            refetchKB();
            setEditingArticle(null);
            setView('list');
        }
        else {
            onNotify('Failed to save article', 'error');
        }
    }, [save, onNotify, refetchKB]);
    const handleDelete = useCallback(async (articleId) => {
        setDeleting(true);
        try {
            const resp = await apiFetch(`/api/admin/knowledge/${articleId}`, { method: 'DELETE' });
            if (!resp.ok)
                throw new Error(`${resp.status}`);
            onNotify('Article deleted', 'success');
            refetchKB();
            setEditingArticle(null);
            setView('list');
        }
        catch {
            onNotify('Failed to delete article', 'error');
        }
        finally {
            setDeleting(false);
        }
    }, [apiFetch, onNotify, refetchKB]);
    // Editor view
    if (view === 'editor' && editingArticle !== null) {
        return (_jsx("div", { style: {
                fontFamily: FONT_FAMILY,
                border: `1px solid ${COLOR_BORDER}`,
                borderRadius: BORDER_RADIUS,
                backgroundColor: COLOR_WHITE,
                minHeight: '500px',
            }, children: _jsx(ArticleEditor, { article: editingArticle, categories: categories, saving: saving, saveError: saveError, onSave: handleSave, onDelete: handleDelete, onCancel: handleCancel, deleting: deleting }) }));
    }
    // Import view
    if (view === 'import') {
        return (_jsx("div", { style: {
                fontFamily: FONT_FAMILY,
                border: `1px solid ${COLOR_BORDER}`,
                borderRadius: BORDER_RADIUS,
                backgroundColor: COLOR_WHITE,
                minHeight: '500px',
            }, children: _jsxs("div", { style: { padding: '24px' }, children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }, children: [_jsxs("h2", { style: { margin: 0, fontSize: '18px', fontWeight: 600, color: COLOR_TEXT }, children: ["Import Content", _jsx(HelpTooltip, { text: "Upload PDF, DOCX, CSV, or TXT files to automatically create knowledge base entries.", docLink: "https://agentredcx.com/docs/admin-guide/knowledge-base-management#uploading-documents" })] }), _jsx("button", { onClick: () => { setView('list'); refetchKB(); }, style: buttonStyle('secondary'), children: "Back to list" })] }), uploadResult ? (_jsx(UploadResultDisplay, { result: uploadResult, onDone: handleImportDone })) : (_jsxs(_Fragment, { children: [_jsx("div", { style: { display: 'flex', gap: '0', marginBottom: '24px', borderBottom: `1px solid ${COLOR_BORDER}` }, children: ['file', 'url'].map((tab) => (_jsx("button", { onClick: () => setImportTab(tab), style: {
                                        padding: '10px 20px',
                                        border: 'none',
                                        borderBottom: importTab === tab ? `2px solid ${BRAND_PRIMARY}` : '2px solid transparent',
                                        backgroundColor: 'transparent',
                                        color: importTab === tab ? BRAND_PRIMARY : COLOR_TEXT_SECONDARY,
                                        fontWeight: importTab === tab ? 600 : 400,
                                        fontSize: '14px',
                                        fontFamily: FONT_FAMILY,
                                        cursor: 'pointer',
                                        transition: 'all 0.15s ease',
                                    }, children: tab === 'file' ? 'Upload file' : 'Import URL' }, tab))) }), importTab === 'file' ? (_jsx(FileUploadZone, { onFileSelected: handleFileUpload, uploading: uploading, progress: uploadProgress, error: uploadError })) : (_jsx(URLImportForm, { onImport: handleUrlImport, importing: importing, error: importError }))] }))] }) }));
    }
    // List view
    return (_jsxs("div", { style: {
            fontFamily: FONT_FAMILY,
            border: `1px solid ${COLOR_BORDER}`,
            borderRadius: BORDER_RADIUS,
            backgroundColor: COLOR_WHITE,
            minHeight: '500px',
        }, children: [_jsx("div", { style: { display: 'flex', gap: '0', borderBottom: `1px solid ${COLOR_BORDER}` }, children: ([
                    { key: 'articles', label: 'Articles' },
                    { key: 'sources', label: 'Website Sources' },
                ]).map(({ key, label }) => (_jsx("button", { onClick: () => setKbTab(key), style: {
                        padding: '12px 24px',
                        border: 'none',
                        borderBottom: kbTab === key ? `2px solid ${BRAND_PRIMARY}` : '2px solid transparent',
                        backgroundColor: 'transparent',
                        color: kbTab === key ? BRAND_PRIMARY : COLOR_TEXT_SECONDARY,
                        fontWeight: kbTab === key ? 600 : 400,
                        fontSize: '14px',
                        fontFamily: FONT_FAMILY,
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                    }, children: label }, key))) }), kbTab === 'sources' && (_jsx(WebsiteSourcesPanel, { apiFetch: apiFetch, onNotify: onNotify })), kbTab === 'articles' && _jsxs(_Fragment, { children: [_jsxs("div", { style: {
                            padding: '16px 20px',
                            borderBottom: `1px solid ${COLOR_BORDER}`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                        }, children: [_jsxs("div", { children: [_jsxs("h2", { style: { margin: 0, fontSize: '18px', fontWeight: 600, color: COLOR_TEXT }, children: ["Knowledge Base", _jsx(HelpTooltip, { text: "Articles, FAQs, and policies that the AI searches to answer customer questions. Keep it accurate and up to date.", docLink: "https://agentredcx.com/docs/admin-guide/knowledge-base-management" })] }), _jsxs("span", { style: { fontSize: '13px', color: COLOR_TEXT_SECONDARY }, children: [articles.length, " article", articles.length !== 1 ? 's' : '', filteredArticles.length !== articles.length && ` (${filteredArticles.length} shown)`] })] }), _jsxs("div", { style: { display: 'flex', gap: '8px' }, children: [_jsxs("span", { style: { display: 'inline-flex', alignItems: 'center', gap: 2 }, children: [_jsx("button", { onClick: async () => {
                                                    const res = await runConflictScan(true);
                                                    if (res)
                                                        setShowScanResults(true);
                                                }, disabled: scanning || articles.length < 2, style: buttonStyle('secondary', scanning || articles.length < 2), children: scanning ? 'Scanning...' : 'Scan for conflicts' }), _jsx(HelpTooltip, { text: "Detect duplicate, overlapping, or contradictory knowledge base entries that may cause inconsistent AI responses.", docLink: "https://agentredcx.com/docs/admin-guide/conflict-scanner" })] }), _jsxs("span", { style: { display: 'inline-flex', alignItems: 'center', gap: 2 }, children: [_jsx("button", { onClick: handleExport, disabled: exporting || articles.length === 0, style: buttonStyle('secondary', exporting || articles.length === 0), children: exporting ? 'Exporting...' : 'Export CSV' }), _jsx(HelpTooltip, { text: "Download all knowledge base entries as a CSV file for backup or editing.", docLink: "https://agentredcx.com/docs/admin-guide/knowledge-base" })] }), _jsxs("span", { style: { display: 'inline-flex', alignItems: 'center', gap: 2 }, children: [_jsx("button", { onClick: handleOpenImport, style: buttonStyle('secondary'), children: "Import" }), _jsx(HelpTooltip, { text: "Upload PDF, DOCX, CSV, or TXT files, or import from a URL to bulk-create knowledge base entries.", docLink: "https://agentredcx.com/docs/admin-guide/knowledge-base" })] }), _jsx("button", { onClick: handleOpenNew, style: buttonStyle('primary'), children: "+ New Article" })] })] }), stalenessData && (stalenessData.staleCount > 0 || stalenessData.veryStaleCount > 0) && (_jsxs("div", { style: {
                            padding: '10px 20px',
                            borderBottom: `1px solid ${COLOR_BORDER}`,
                            backgroundColor: '#ffeef0',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '16px',
                            fontSize: '13px',
                        }, children: [_jsxs("span", { style: { color: COLOR_DANGER, fontWeight: 600 }, children: [stalenessData.staleCount + stalenessData.veryStaleCount, " article", (stalenessData.staleCount + stalenessData.veryStaleCount) !== 1 ? 's' : '', " need attention"] }), _jsxs("span", { style: { color: COLOR_TEXT_SECONDARY }, children: [stalenessData.freshCount, " fresh, ", stalenessData.agingCount, " aging, ", stalenessData.staleCount, " stale", stalenessData.veryStaleCount > 0 && `, ${stalenessData.veryStaleCount} very stale`] })] })), showScanResults && scanResult && (_jsxs("div", { style: {
                            padding: '16px 20px',
                            borderBottom: `1px solid ${COLOR_BORDER}`,
                            backgroundColor: COLOR_LIGHT_GRAY,
                        }, children: [_jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }, children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '12px' }, children: [_jsx("span", { style: { fontWeight: 600, fontSize: '14px', color: COLOR_TEXT }, children: "Conflict scan results" }), scanResult.highCount > 0 && (_jsxs("span", { style: { padding: '2px 8px', borderRadius: '10px', fontSize: '12px', fontWeight: 600, backgroundColor: '#ffeef0', color: COLOR_DANGER }, children: [scanResult.highCount, " high"] })), scanResult.mediumCount > 0 && (_jsxs("span", { style: { padding: '2px 8px', borderRadius: '10px', fontSize: '12px', fontWeight: 600, backgroundColor: '#fff8c5', color: COLOR_WARNING }, children: [scanResult.mediumCount, " medium"] })), scanResult.lowCount > 0 && (_jsxs("span", { style: { padding: '2px 8px', borderRadius: '10px', fontSize: '12px', fontWeight: 600, backgroundColor: COLOR_LIGHT_GRAY, color: COLOR_GRAY }, children: [scanResult.lowCount, " low"] })), scanResult.conflicts.length === 0 && (_jsx("span", { style: { fontSize: '13px', color: COLOR_SUCCESS, fontWeight: 600 }, children: "No conflicts found" })), _jsxs("span", { style: { fontSize: '12px', color: COLOR_TEXT_SECONDARY }, children: [scanResult.totalEntriesScanned, " entries scanned in ", scanResult.scanDurationMs, "ms", scanResult.entriesWithoutEmbeddings > 0 && ` (${scanResult.entriesWithoutEmbeddings} not yet embedded)`] })] }), _jsx("button", { onClick: () => setShowScanResults(false), style: { background: 'none', border: 'none', cursor: 'pointer', color: COLOR_GRAY, fontSize: '16px', padding: '4px' }, children: String.fromCodePoint(0x2715) })] }), scanResult.conflicts.filter(c => !dismissedPairs.has(`${c.entryAId}-${c.entryBId}`)).map((conflict, idx) => {
                                const pairKey = `${conflict.entryAId}-${conflict.entryBId}`;
                                const severityColors = {
                                    high: { bg: '#ffeef0', color: COLOR_DANGER },
                                    medium: { bg: '#fff8c5', color: COLOR_WARNING },
                                    low: { bg: COLOR_LIGHT_GRAY, color: COLOR_GRAY },
                                };
                                const sev = severityColors[conflict.severity] || severityColors.low;
                                const typeLabels = {
                                    near_duplicate: 'Near-duplicate',
                                    conflicting: 'Conflicting info',
                                    topical_overlap: 'Topical overlap',
                                    similar_titles: 'Similar titles',
                                };
                                return (_jsx("div", { style: {
                                        padding: '12px 16px',
                                        marginBottom: '8px',
                                        borderRadius: BORDER_RADIUS,
                                        border: `1px solid ${COLOR_BORDER}`,
                                        backgroundColor: COLOR_WHITE,
                                    }, children: _jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }, children: [_jsxs("div", { style: { flex: 1 }, children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }, children: [_jsx("span", { style: { padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 600, backgroundColor: sev.bg, color: sev.color }, children: conflict.severity.toUpperCase() }), _jsx("span", { style: { fontSize: '12px', color: COLOR_TEXT_SECONDARY, fontWeight: 500 }, children: typeLabels[conflict.conflictType] || conflict.conflictType }), _jsxs("span", { style: { fontSize: '11px', color: COLOR_TEXT_SECONDARY }, children: ["Similarity: ", Math.round(conflict.embeddingSimilarity * 100), "% | Overlap: ", Math.round(conflict.contentOverlap * 100), "%"] })] }), _jsxs("div", { style: { fontSize: '13px', color: COLOR_TEXT, marginBottom: '4px' }, children: [_jsx("strong", { children: conflict.entryATitle }), _jsx("span", { style: { color: COLOR_TEXT_SECONDARY, margin: '0 6px' }, children: "vs" }), _jsx("strong", { children: conflict.entryBTitle })] }), conflict.conflictingFacts.length > 0 && (_jsx("div", { style: { fontSize: '12px', color: COLOR_DANGER, marginBottom: '4px' }, children: conflict.conflictingFacts.map((fact, fi) => (_jsxs("div", { children: [String.fromCodePoint(0x26A0), " ", fact] }, fi))) })), _jsx("div", { style: { fontSize: '12px', color: COLOR_TEXT_SECONDARY, lineHeight: '1.5' }, children: conflict.resolution })] }), _jsx("button", { onClick: () => setDismissedPairs(prev => new Set([...prev, pairKey])), style: { background: 'none', border: 'none', cursor: 'pointer', color: COLOR_GRAY, fontSize: '12px', padding: '4px 8px', marginLeft: '12px', whiteSpace: 'nowrap' }, children: "Dismiss" })] }) }, pairKey));
                            }), scanError && (_jsxs("div", { style: { fontSize: '13px', color: COLOR_DANGER, marginTop: '8px' }, children: ["Scan error: ", scanError] }))] })), _jsxs("div", { style: {
                            padding: '12px 20px',
                            borderBottom: `1px solid ${COLOR_BORDER}`,
                            display: 'flex',
                            gap: '12px',
                            alignItems: 'center',
                            flexWrap: 'wrap',
                            backgroundColor: COLOR_LIGHT_GRAY,
                        }, children: [_jsx("input", { type: "text", value: searchQuery, onChange: (e) => setSearchQuery(e.target.value), placeholder: "Search articles...", "aria-label": "Search articles by title", style: inputStyle({ width: '240px', flex: 'none' }) }), _jsxs("label", { style: { display: 'flex', alignItems: 'center', gap: '6px' }, children: [_jsx("span", { style: { fontSize: '12px', color: COLOR_TEXT_SECONDARY, whiteSpace: 'nowrap' }, title: "Filter articles by category", children: "Category" }), _jsxs("select", { value: categoryFilter, onChange: (e) => setCategoryFilter(e.target.value), style: inputStyle({ width: '160px', flex: 'none' }), "aria-label": "Filter by category", title: "Filter articles by category", children: [_jsx("option", { value: "", children: "All" }), categories.map((cat) => (_jsx("option", { value: cat, children: cat }, cat)))] })] }), _jsxs("label", { style: { display: 'flex', alignItems: 'center', gap: '6px' }, children: [_jsx("span", { style: { fontSize: '12px', color: COLOR_TEXT_SECONDARY, whiteSpace: 'nowrap' }, title: "Filter articles by publication status", children: "Status" }), _jsx("select", { value: statusFilter, onChange: (e) => setStatusFilter(e.target.value), style: inputStyle({ width: '140px', flex: 'none' }), "aria-label": "Filter by status", title: "Filter articles by publication status", children: ALL_STATUSES.map((s) => (_jsx("option", { value: s.value, children: s.label }, s.value))) })] }), (searchQuery || categoryFilter || statusFilter) && (_jsx("button", { onClick: () => {
                                    setSearchQuery('');
                                    setCategoryFilter('');
                                    setStatusFilter('');
                                }, style: {
                                    padding: '6px 12px',
                                    border: 'none',
                                    borderRadius: BORDER_RADIUS,
                                    backgroundColor: 'transparent',
                                    color: BRAND_PRIMARY,
                                    fontSize: '12px',
                                    fontFamily: FONT_FAMILY,
                                    cursor: 'pointer',
                                    fontWeight: 500,
                                }, children: "Clear filters" }))] }), kbLoading && articles.length === 0 && (_jsx(LoadingSpinner, { text: "Loading articles..." })), kbError && articles.length === 0 && (_jsx(ErrorBanner, { message: kbError, onRetry: refetchKB })), !kbLoading && !kbError && articles.length === 0 && (_jsx(EmptyState, { icon: String.fromCodePoint(0x1F4DA), title: "No articles yet", subtitle: "Create your first knowledge base article to help your AI agent answer customer questions." })), !kbLoading && !kbError && articles.length > 0 && filteredArticles.length === 0 && (_jsx(EmptyState, { icon: String.fromCodePoint(0x1F50D), title: "No matching articles", subtitle: "Try adjusting your search query or filters." })), filteredArticles.length > 0 && (_jsx("div", { style: { overflowX: 'auto' }, children: _jsxs("table", { style: {
                                width: '100%',
                                borderCollapse: 'collapse',
                                fontSize: '14px',
                            }, children: [_jsx("thead", { children: _jsxs("tr", { style: { backgroundColor: COLOR_LIGHT_GRAY }, children: [_jsx("th", { style: {
                                                    padding: '10px 16px',
                                                    textAlign: 'left',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    color: COLOR_TEXT_SECONDARY,
                                                    borderBottom: `1px solid ${COLOR_BORDER}`,
                                                    textTransform: 'uppercase',
                                                    letterSpacing: '0.5px',
                                                }, children: "Title" }), _jsxs("th", { style: {
                                                    padding: '10px 16px',
                                                    textAlign: 'left',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    color: COLOR_TEXT_SECONDARY,
                                                    borderBottom: `1px solid ${COLOR_BORDER}`,
                                                    textTransform: 'uppercase',
                                                    letterSpacing: '0.5px',
                                                    width: '160px',
                                                }, children: ["Category", _jsx(HelpTooltip, { text: "Organize articles by topic for easier management. The AI uses categories to narrow searches.", docLink: "https://agentredcx.com/docs/admin-guide/knowledge-base-management#organizing-with-categories" })] }), _jsxs("th", { style: {
                                                    padding: '10px 16px',
                                                    textAlign: 'left',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    color: COLOR_TEXT_SECONDARY,
                                                    borderBottom: `1px solid ${COLOR_BORDER}`,
                                                    textTransform: 'uppercase',
                                                    letterSpacing: '0.5px',
                                                    width: '110px',
                                                }, children: ["Status", _jsx(HelpTooltip, { text: "Draft articles are not used by the AI. Publish when ready.", docLink: "https://agentredcx.com/docs/admin-guide/knowledge-base-management#article-status-lifecycle" })] }), _jsxs("th", { style: {
                                                    padding: '10px 16px',
                                                    textAlign: 'left',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    color: COLOR_TEXT_SECONDARY,
                                                    borderBottom: `1px solid ${COLOR_BORDER}`,
                                                    textTransform: 'uppercase',
                                                    letterSpacing: '0.5px',
                                                    width: '100px',
                                                }, children: ["Freshness", _jsx(HelpTooltip, { text: "How recently the article content has been verified. Stale articles may contain outdated information.", docLink: "https://agentredcx.com/docs/admin-guide/knowledge-base-management#staleness-and-freshness" })] }), _jsx("th", { style: {
                                                    padding: '10px 16px',
                                                    textAlign: 'left',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    color: COLOR_TEXT_SECONDARY,
                                                    borderBottom: `1px solid ${COLOR_BORDER}`,
                                                    textTransform: 'uppercase',
                                                    letterSpacing: '0.5px',
                                                    width: '140px',
                                                }, children: "Last Updated" }), _jsx("th", { style: {
                                                    padding: '10px 16px',
                                                    textAlign: 'left',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    color: COLOR_TEXT_SECONDARY,
                                                    borderBottom: `1px solid ${COLOR_BORDER}`,
                                                    textTransform: 'uppercase',
                                                    letterSpacing: '0.5px',
                                                    width: '90px',
                                                }, children: "Actions" })] }) }), _jsx("tbody", { children: filteredArticles.map((article) => (_jsx(ArticleRow, { article: article, onClick: () => handleOpenEdit(article), onVerify: handleVerify, verifying: verifying }, article.id))) })] }) }))] })] }));
};
export default KnowledgeBaseManager;
//# sourceMappingURL=KnowledgeBaseManager.js.map