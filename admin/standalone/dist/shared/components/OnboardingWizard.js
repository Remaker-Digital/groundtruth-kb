import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * OnboardingWizard — First-login modal that guides merchants through:
 *   Step 1: Select product category (from template registry) + optional storefront URL
 *   Step 2: Apply template + storefront ingestion (Shopify or URL) → progress
 *   Step 3: Show config suggestions → Activate now (one-click) or dismiss
 *
 * Supports two ingestion paths:
 *   - Shopify merchants: Uses Shopify Admin API via shopDomain prop
 *   - Non-Shopify merchants: Crawls storefront URL entered in Step 1
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { Modal, Button, Stack, Text, Group, SimpleGrid, Card, ThemeIcon, Loader, Progress, Badge, Alert, Divider, Box, TextInput, Textarea, Anchor, } from '@mantine/core';
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
/** Validate a URL string (basic check for protocol + domain). */
function isValidUrl(url) {
    try {
        const parsed = new URL(url);
        return parsed.protocol === 'http:' || parsed.protocol === 'https:';
    }
    catch {
        return false;
    }
}
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export const OnboardingWizard = ({ opened, onClose, apiFetch, shopDomain, onNavigate, }) => {
    const [step, setStep] = useState(1);
    const [templates, setTemplates] = useState([]);
    const [templatesLoading, setTemplatesLoading] = useState(false);
    const [selectedCategory, setSelectedCategory] = useState(null);
    const [storefrontUrl, setStorefrontUrl] = useState('');
    const [applyLoading, setApplyLoading] = useState(false);
    const [applyResult, setApplyResult] = useState(null);
    const [applyError, setApplyError] = useState(null);
    const [ingestionJob, setIngestionJob] = useState(null);
    const [ingestionRunning, setIngestionRunning] = useState(false);
    const [suggestions, setSuggestions] = useState(null);
    const [suggestionsLoading, setSuggestionsLoading] = useState(false);
    const [activating, setActivating] = useState(false);
    const [activateError, setActivateError] = useState(null);
    const [customInstructions, setCustomInstructions] = useState('');
    const [existingArticleCount, setExistingArticleCount] = useState(0);
    const pollRef = useRef(null);
    // The effective ingestion URL for non-Shopify merchants
    const effectiveUrl = !shopDomain && storefrontUrl.trim() ? storefrontUrl.trim() : null;
    const urlValid = !effectiveUrl || isValidUrl(effectiveUrl);
    const selectedTemplate = templates.find((t) => t.id === selectedCategory);
    // Load templates on open
    useEffect(() => {
        if (!opened)
            return;
        setTemplatesLoading(true);
        apiFetch('/api/admin/knowledge/templates')
            .then((r) => r.json())
            .then((data) => setTemplates(data.templates || data || []))
            .catch(() => setTemplates([]))
            .finally(() => setTemplatesLoading(false));
    }, [opened, apiFetch]);
    // Check for existing KB articles when wizard opens (duplicate warning)
    useEffect(() => {
        if (!opened)
            return;
        apiFetch('/api/admin/knowledge?limit=1')
            .then((r) => r.json())
            .then((data) => {
            const total = data.total ?? data.entries?.length ?? 0;
            setExistingArticleCount(total);
        })
            .catch(() => setExistingArticleCount(0));
    }, [opened, apiFetch]);
    // Clean up polling on unmount
    useEffect(() => {
        return () => {
            if (pollRef.current)
                clearInterval(pollRef.current);
        };
    }, []);
    // -------------------------------------------------------------------
    // Shared ingestion polling logic
    // -------------------------------------------------------------------
    const startIngestionPolling = useCallback(() => {
        if (pollRef.current)
            clearInterval(pollRef.current);
        pollRef.current = setInterval(async () => {
            try {
                const statusRes = await apiFetch('/api/admin/knowledge/ingest/status');
                if (statusRes.ok) {
                    const status = await statusRes.json();
                    if (!status || !status.status) {
                        // No active job — ingestion finished or was never started
                        if (pollRef.current)
                            clearInterval(pollRef.current);
                        pollRef.current = null;
                        setIngestionRunning(false);
                        return;
                    }
                    setIngestionJob(status);
                    if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
                        if (pollRef.current)
                            clearInterval(pollRef.current);
                        pollRef.current = null;
                        setIngestionRunning(false);
                    }
                }
            }
            catch { /* continue polling */ }
        }, 3000);
    }, [apiFetch]);
    // -------------------------------------------------------------------
    // Step 2: Apply template
    // -------------------------------------------------------------------
    const handleApplyTemplate = useCallback(async () => {
        if (!selectedCategory)
            return;
        setApplyLoading(true);
        setApplyError(null);
        setStep(2);
        try {
            const res = await apiFetch(`/api/admin/knowledge/templates/${selectedCategory}/apply`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({}),
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: 'Template application failed' }));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }
            const result = await res.json();
            setApplyResult({
                articlesCreated: result.articles_created ?? result.articlesCreated ?? 0,
                articlesFailed: result.articles_failed ?? result.articlesFailed ?? 0,
                totalChars: result.total_chars ?? result.totalChars ?? 0,
                configSuggestions: result.config_suggestions ?? result.configSuggestions,
            });
            // Start storefront ingestion: Shopify path or URL path
            if (shopDomain) {
                startStorefrontIngestion();
            }
            else if (effectiveUrl) {
                startUrlIngestion(effectiveUrl);
            }
        }
        catch (e) {
            setApplyError(e.message || 'Failed to apply template');
        }
        finally {
            setApplyLoading(false);
        }
    }, [selectedCategory, apiFetch, shopDomain, effectiveUrl]);
    // -------------------------------------------------------------------
    // Shopify ingestion
    // -------------------------------------------------------------------
    const startStorefrontIngestion = useCallback(async () => {
        setIngestionRunning(true);
        try {
            const res = await apiFetch('/api/admin/knowledge/ingest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sourceType: 'shopify' }),
            });
            if (res.ok) {
                const job = await res.json();
                setIngestionJob(job);
                startIngestionPolling();
            }
            else {
                const err = await res.json().catch(() => ({ detail: 'Storefront import failed' }));
                setIngestionJob({
                    job_id: '', status: 'failed', source_type: 'shopify',
                    error: typeof err.detail === 'string' ? err.detail : 'Could not connect to Shopify store',
                });
                setIngestionRunning(false);
            }
        }
        catch {
            setIngestionJob({
                job_id: '', status: 'failed', source_type: 'shopify',
                error: 'Network error while starting storefront import',
            });
            setIngestionRunning(false);
        }
    }, [apiFetch, startIngestionPolling]);
    // -------------------------------------------------------------------
    // URL ingestion (non-Shopify merchants)
    // -------------------------------------------------------------------
    const startUrlIngestion = useCallback(async (url) => {
        setIngestionRunning(true);
        try {
            const res = await apiFetch('/api/admin/knowledge/ingest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sourceType: 'url', url, maxPages: 20 }),
            });
            if (res.ok) {
                const job = await res.json();
                setIngestionJob(job);
                startIngestionPolling();
            }
            else {
                const err = await res.json().catch(() => ({ detail: 'Storefront crawl failed' }));
                setIngestionJob({
                    job_id: '', status: 'failed', source_type: 'url',
                    error: typeof err.detail === 'string' ? err.detail : 'Could not crawl storefront URL',
                });
                setIngestionRunning(false);
            }
        }
        catch {
            setIngestionJob({
                job_id: '', status: 'failed', source_type: 'url',
                error: 'Network error while starting storefront crawl',
            });
            setIngestionRunning(false);
        }
    }, [apiFetch, startIngestionPolling]);
    // -------------------------------------------------------------------
    // Step 3: Load suggestions + Activate
    // -------------------------------------------------------------------
    const handleViewSuggestions = useCallback(async () => {
        setStep(3);
        setSuggestionsLoading(true);
        setActivateError(null);
        try {
            const res = await apiFetch('/api/admin/knowledge/suggestions');
            if (res.ok) {
                const data = await res.json();
                setSuggestions(Array.isArray(data) ? data : data.suggestions || []);
            }
        }
        catch { /* suggestions are best-effort */ }
        setSuggestionsLoading(false);
    }, [apiFetch]);
    /** Extract a human-readable error message from API error responses. */
    const extractErrorMessage = (detail, fallback) => {
        if (typeof detail === 'string')
            return detail;
        if (detail && typeof detail === 'object') {
            const obj = detail;
            if (Array.isArray(obj.errors) && obj.errors.length > 0) {
                // Config save: errors are {field_name, message} objects
                // Activation: errors are plain strings
                return obj.errors
                    .map((e) => (typeof e === 'string' ? e : e?.message ?? String(e)))
                    .join('; ');
            }
            if (typeof obj.detail === 'string')
                return obj.detail;
            if (typeof obj.message === 'string')
                return obj.message;
        }
        return fallback;
    };
    /** Derive a brand name fallback from shopDomain or template category. */
    const inferBrandName = () => {
        if (shopDomain) {
            // "blanco-9939.myshopify.com" → "Blanco 9939" → "Blanco"
            const storeName = shopDomain.replace('.myshopify.com', '').replace(/[._]/g, ' ');
            // Capitalize each word, drop trailing numbers-only segments
            const parts = storeName.split(/[-\s]+/).filter((p) => !/^\d+$/.test(p));
            if (parts.length > 0) {
                return parts.map((p) => p.charAt(0).toUpperCase() + p.slice(1).toLowerCase()).join(' ');
            }
        }
        if (selectedTemplate) {
            return selectedTemplate.name;
        }
        return null;
    };
    /** One-click activation: save suggested config fields, then activate. */
    const handleActivateWithSuggestions = useCallback(async () => {
        setActivating(true);
        setActivateError(null);
        try {
            // Build fields from suggestions — keep arrays as-is for list fields
            const fields = {};
            for (const s of suggestions || []) {
                fields[s.fieldName] = s.value;
            }
            // Include custom instructions from wizard
            if (customInstructions.trim()) {
                fields.custom_instructions = customInstructions.trim();
            }
            // Ensure mandatory fields have values — fall back to inference
            if (!fields.brand_name) {
                const inferred = inferBrandName();
                if (inferred)
                    fields.brand_name = inferred;
            }
            if (!fields.brand_voice && selectedTemplate?.suggestedBrandVoice) {
                fields.brand_voice = selectedTemplate.suggestedBrandVoice;
            }
            // Hard fallback — brand_voice is mandatory for activation
            if (!fields.brand_voice) {
                fields.brand_voice = 'professional and friendly';
            }
            // Save config draft
            if (Object.keys(fields).length > 0) {
                const saveRes = await apiFetch('/api/config', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ fields }),
                });
                if (!saveRes.ok) {
                    const err = await saveRes.json().catch(() => ({ detail: 'Failed to save configuration' }));
                    throw new Error(extractErrorMessage(err.detail ?? err, `Save failed: HTTP ${saveRes.status}`));
                }
            }
            // Activate the draft
            const activateRes = await apiFetch('/api/config/draft/activate', {
                method: 'POST',
            });
            if (!activateRes.ok) {
                const err = await activateRes.json().catch(() => ({ detail: 'Activation failed' }));
                throw new Error(extractErrorMessage(err.detail ?? err, `Activate failed: HTTP ${activateRes.status}`));
            }
            // Success — close wizard and go to dashboard
            handleClose();
            if (onNavigate)
                onNavigate('/');
        }
        catch (e) {
            setActivateError(typeof e?.message === 'string' ? e.message : 'Activation failed');
        }
        finally {
            setActivating(false);
        }
    }, [suggestions, apiFetch, onNavigate, shopDomain, selectedTemplate, customInstructions]);
    // Navigate to config page (fallback for manual review)
    const handleGoToConfig = useCallback(() => {
        onClose();
        if (onNavigate)
            onNavigate('/configuration');
    }, [onClose, onNavigate]);
    // Reset on close
    const handleClose = useCallback(() => {
        setStep(1);
        setSelectedCategory(null);
        setStorefrontUrl('');
        setApplyResult(null);
        setApplyError(null);
        setIngestionJob(null);
        setIngestionRunning(false);
        setSuggestions(null);
        setActivating(false);
        setActivateError(null);
        setCustomInstructions('');
        if (pollRef.current) {
            clearInterval(pollRef.current);
            pollRef.current = null;
        }
        onClose();
    }, [onClose]);
    // The label shown during ingestion progress
    const ingestionLabel = shopDomain
        ? `Importing pages from ${shopDomain}...`
        : effectiveUrl
            ? `Scanning ${new URL(effectiveUrl).hostname}...`
            : 'Scanning your storefront...';
    return (_jsxs(Modal, { opened: opened, onClose: handleClose, title: _jsxs(Group, { gap: "xs", children: [_jsx(ThemeIcon, { size: "md", variant: "light", color: "action", children: _jsx("svg", { width: "16", height: "16", viewBox: "0 0 16 16", fill: "none", xmlns: "http://www.w3.org/2000/svg", children: _jsx("path", { d: "M8 0L9.8 6.2L16 8L9.8 9.8L8 16L6.2 9.8L0 8L6.2 6.2L8 0Z", fill: "currentColor" }) }) }), _jsxs(Text, { fw: 600, size: "lg", children: [step === 1 && 'Set up your AI assistant', step === 2 && 'Building your knowledge base', step === 3 && 'Custom AI instructions'] })] }), centered: true, size: "lg", closeOnClickOutside: false, closeOnEscape: step === 1, children: [step === 1 && (_jsxs(Stack, { gap: "md", children: [_jsx(Text, { size: "sm", c: "dimmed", children: "What type of products or services does your store sell? We'll create starter knowledge base articles tailored to your industry." }), existingArticleCount > 0 && (_jsx(Alert, { variant: "light", color: "yellow", radius: "sm", title: "Existing articles detected", children: _jsxs(Text, { size: "sm", children: ["Your knowledge base already contains ", _jsx("strong", { children: existingArticleCount }), " article", existingArticleCount === 1 ? '' : 's', ". Running the wizard again will ", _jsx("strong", { children: "add new articles" }), " alongside existing ones. Previously added articles will not be removed automatically \u2014 you should review and remove duplicates from the", ' ', _jsx(Anchor, { size: "sm", onClick: () => { onClose(); onNavigate?.('/knowledge-base'); }, children: "Knowledge Base" }), ' ', "page after setup."] }) })), templatesLoading ? (_jsxs(Group, { justify: "center", py: "xl", children: [_jsx(Loader, { size: "sm" }), _jsx(Text, { size: "sm", c: "dimmed", children: "Loading categories..." })] })) : (_jsx(SimpleGrid, { cols: { base: 2, sm: 3 }, spacing: "xs", children: templates.map((t) => (_jsxs(Card, { padding: "sm", radius: "sm", withBorder: true, style: {
                                cursor: 'pointer',
                                borderColor: selectedCategory === t.id ? 'var(--mantine-color-action-6)' : undefined,
                                backgroundColor: selectedCategory === t.id ? 'var(--mantine-color-action-light)' : undefined,
                                color: selectedCategory === t.id ? 'var(--mantine-color-action-light-color)' : undefined,
                            }, onClick: () => setSelectedCategory(t.id), children: [_jsx(Text, { size: "sm", fw: 500, lineClamp: 1, children: t.name }), _jsx(Text, { size: "xs", c: "dimmed", lineClamp: 2, mt: 2, children: t.description })] }, t.id))) })), selectedTemplate && (_jsx(Alert, { variant: "light", color: "action", radius: "sm", children: _jsxs(Text, { size: "xs", children: [_jsxs("strong", { children: [selectedTemplate.articleCount, " articles"] }), " will be created for ", _jsx("strong", { children: selectedTemplate.name }), ".", selectedTemplate.suggestedBrandVoice && (_jsxs(_Fragment, { children: [" Suggested voice: ", _jsx("em", { children: selectedTemplate.suggestedBrandVoice }), "."] }))] }) })), shopDomain ? (_jsx(Alert, { variant: "light", color: "green", radius: "sm", title: "Storefront detected", children: _jsxs(Text, { size: "sm", children: ["We'll import products and policies from", ' ', _jsx("strong", { children: shopDomain }), " to build your knowledge base."] }) })) : (_jsx(TextInput, { label: "Your storefront URL (optional)", placeholder: "https://www.yourstore.com", description: "We'll scan your website to create knowledge base articles about your products and policies.", value: storefrontUrl, onChange: (e) => setStorefrontUrl(e.currentTarget.value), error: storefrontUrl.trim() && !urlValid ? 'Enter a valid URL starting with https://' : undefined, size: "sm" })), _jsxs(Group, { justify: "space-between", mt: "xs", children: [_jsx(Button, { variant: "subtle", color: "dimmed", onClick: handleClose, size: "sm", children: "Skip for now" }), _jsx(Button, { color: "action", onClick: handleApplyTemplate, disabled: !selectedCategory || (!!storefrontUrl.trim() && !urlValid), size: "sm", children: "Continue" })] })] })), step === 2 && (_jsxs(Stack, { gap: "md", children: [applyLoading && (_jsxs(Group, { justify: "center", py: "lg", children: [_jsx(Loader, { size: "sm" }), _jsxs(Text, { size: "sm", children: ["Applying ", selectedTemplate?.name, " template..."] })] })), applyError && (_jsxs(Alert, { color: "red", radius: "sm", title: "Template Error", children: [_jsx(Text, { size: "sm", children: applyError }), _jsx(Button, { size: "xs", variant: "light", color: "red", mt: "xs", onClick: () => { setApplyError(null); setStep(1); }, children: "Go back" })] })), applyResult && !applyLoading && (_jsxs(_Fragment, { children: [_jsx(Alert, { variant: "light", color: "green", radius: "sm", title: "Knowledge base created", children: _jsxs(Text, { size: "sm", children: [_jsx("strong", { children: applyResult.articlesCreated }), " articles added", applyResult.articlesFailed > 0 && (_jsxs(_Fragment, { children: [" (", applyResult.articlesFailed, " failed)"] }))] }) }), ingestionRunning && ingestionJob && (_jsxs(_Fragment, { children: [_jsx(Divider, { label: "Scanning your storefront", labelPosition: "center" }), _jsxs(Stack, { gap: "xs", children: [_jsxs(Group, { justify: "space-between", children: [_jsx(Text, { size: "sm", children: ingestionLabel }), _jsx(Badge, { size: "sm", color: "yellow", variant: "light", children: ingestionJob.status })] }), _jsx(Progress, { value: ingestionJob.progress_pct ?? 0, animated: true, size: "sm", color: "action" }), ingestionJob.pages_crawled != null && (_jsxs(Text, { size: "xs", c: "dimmed", children: [ingestionJob.pages_crawled, " pages crawled,", ' ', ingestionJob.articles_created ?? 0, " articles created"] }))] })] })), ingestionJob && !ingestionRunning && ingestionJob.status === 'completed' && (_jsxs(_Fragment, { children: [_jsx(Divider, { label: "Storefront scan complete", labelPosition: "center" }), _jsx(Alert, { variant: "light", color: "green", radius: "sm", children: _jsxs(Text, { size: "sm", children: ["Imported ", _jsx("strong", { children: ingestionJob.articles_created ?? 0 }), " additional articles from your storefront."] }) })] })), ingestionJob && !ingestionRunning && ingestionJob.status === 'failed' && (_jsx(Alert, { variant: "light", color: "yellow", radius: "sm", title: "Storefront import issue", children: _jsxs(Text, { size: "sm", children: [ingestionJob.error || 'Storefront scan encountered an issue.', ' ', "Your template articles are still available. You can retry the scan later from the Knowledge Base page."] }) })), _jsx(Group, { justify: "flex-end", mt: "xs", children: _jsx(Button, { color: "action", onClick: handleViewSuggestions, disabled: ingestionRunning, size: "sm", children: ingestionRunning ? 'Please wait...' : 'Continue' }) })] }))] })), step === 3 && (_jsx(Stack, { gap: "md", children: suggestionsLoading ? (_jsxs(Group, { justify: "center", py: "lg", children: [_jsx(Loader, { size: "sm" }), _jsx(Text, { size: "sm", children: "Analyzing your knowledge base..." })] })) : (_jsxs(_Fragment, { children: [_jsx(Group, { justify: "space-between", align: "flex-start", children: _jsxs(Text, { size: "sm", c: "dimmed", style: { flex: 1 }, children: ["Optionally add custom instructions to shape how your AI assistant responds. Then click ", _jsx("strong", { children: "Activate now" }), " to go live."] }) }), _jsx(Textarea, { label: "Custom instructions (optional)", placeholder: "e.g., Always recommend our premium products first. Never discuss competitor pricing. Use a warm, conversational tone.", description: "These instructions guide your AI's behavior in every conversation. You can edit them later on the Agent Configuration page.", value: customInstructions, onChange: (e) => setCustomInstructions(e.currentTarget.value), minRows: 3, maxRows: 6, autosize: true, size: "sm" }), suggestions && suggestions.length > 0 && (_jsx(Divider, { label: "Suggested settings", labelPosition: "center" })), suggestions && suggestions.length > 0 ? (_jsx(Stack, { gap: "xs", children: suggestions.map((suggestion) => (_jsx(Card, { padding: "xs", radius: "sm", withBorder: true, children: _jsxs(Group, { justify: "space-between", wrap: "nowrap", children: [_jsxs(Box, { children: [_jsx(Text, { size: "xs", fw: 500, tt: "capitalize", children: suggestion.fieldName.replace(/_/g, ' ') }), _jsx(Text, { size: "xs", c: "dimmed", lineClamp: 2, children: Array.isArray(suggestion.value)
                                                        ? suggestion.value.join(', ')
                                                        : String(suggestion.value) })] }), _jsx(Badge, { size: "xs", color: "grape", variant: "light", children: "Suggested" })] }) }, suggestion.fieldName))) })) : (_jsx(Alert, { variant: "light", color: "blue", radius: "sm", children: _jsx(Text, { size: "sm", children: "No configuration suggestions were generated. You can still activate with default settings or configure manually." }) })), activateError && (_jsx(Alert, { variant: "light", color: "red", radius: "sm", children: _jsx(Text, { size: "sm", children: activateError }) })), _jsx(Divider, {}), _jsxs(Text, { size: "xs", c: "dimmed", children: ["For full control, use the sidebar:", ' ', _jsx(Anchor, { size: "xs", onClick: () => { onClose(); onNavigate?.('/configuration'); }, children: "Agent Configuration" }), ', ', _jsx(Anchor, { size: "xs", onClick: () => { onClose(); onNavigate?.('/knowledge-base'); }, children: "Knowledge Base" }), ', ', _jsx(Anchor, { size: "xs", onClick: () => { onClose(); onNavigate?.('/widget'); }, children: "Widget Configuration" })] }), _jsxs(Group, { justify: "space-between", children: [_jsx(Button, { variant: "subtle", color: "dimmed", onClick: handleClose, size: "sm", children: "I'll configure later" }), _jsxs(Group, { gap: "xs", children: [_jsx(Button, { variant: "light", color: "action", onClick: handleGoToConfig, size: "sm", children: "Review first" }), _jsx(Button, { color: "green", onClick: handleActivateWithSuggestions, loading: activating, size: "sm", children: "Activate now" })] })] })] })) }))] }));
};
export default OnboardingWizard;
//# sourceMappingURL=OnboardingWizard.js.map