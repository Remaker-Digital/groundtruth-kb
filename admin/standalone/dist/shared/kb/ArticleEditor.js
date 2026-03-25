import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * ArticleEditor — create / edit form for a single KB article.
 * Handles title, category (existing or new), status, content textarea,
 * save, and delete with confirmation.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback } from 'react';
import { HelpTooltip } from '../HelpTooltip';
import { COLOR_TEXT, COLOR_DANGER, BORDER_RADIUS, inputStyle, buttonStyle, } from './styles';
export const ArticleEditor = ({ article, categories, saving, saveError, onSave, onDelete, onCancel, deleting, }) => {
    const [title, setTitle] = useState(article.title || '');
    const [content, setContent] = useState(article.content || '');
    const [category, setCategory] = useState(article.category || '');
    const [status, setStatus] = useState(article.status || 'draft');
    const [newCategory, setNewCategory] = useState('');
    const [showNewCategory, setShowNewCategory] = useState(false);
    const isNew = !article.id;
    const canSave = title.trim().length > 0 && content.trim().length > 0 && (category.trim().length > 0 || newCategory.trim().length > 0);
    const handleSubmit = useCallback(() => {
        const resolvedCategory = showNewCategory ? newCategory.trim() : category;
        if (!title.trim() || !content.trim() || !resolvedCategory)
            return;
        onSave({
            ...(article.id ? { id: article.id } : {}),
            title: title.trim(),
            content: content.trim(),
            category: resolvedCategory,
            status,
            // Backend requires entry_type — default to 'custom' for manual articles
            entryType: 'custom',
        });
    }, [article.id, title, content, category, newCategory, showNewCategory, status, onSave]);
    const [confirmDelete, setConfirmDelete] = useState(false);
    return (_jsxs("div", { style: { padding: '24px' }, children: [_jsxs("div", { style: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }, children: [_jsx("h2", { style: { margin: 0, fontSize: '18px', fontWeight: 600, color: COLOR_TEXT }, children: isNew ? 'New article' : 'Edit article' }), _jsx("button", { onClick: onCancel, style: buttonStyle('secondary'), children: "Back to list" })] }), saveError && (_jsx("div", { style: {
                    padding: '10px 14px',
                    backgroundColor: '#ffeef0',
                    border: `1px solid ${COLOR_DANGER}33`,
                    borderRadius: BORDER_RADIUS,
                    marginBottom: '16px',
                    fontSize: '13px',
                    color: COLOR_DANGER,
                }, children: saveError })), _jsxs("div", { style: { marginBottom: '16px' }, children: [_jsxs("label", { style: {
                            display: 'block',
                            fontSize: '13px',
                            fontWeight: 600,
                            color: COLOR_TEXT,
                            marginBottom: '6px',
                        }, children: ["Title ", _jsx("span", { style: { color: COLOR_DANGER }, children: "*" }), _jsx(HelpTooltip, { text: "A clear, descriptive title helps the AI match articles to customer questions.", docLink: "https://agentredcx.com/docs/admin-guide/knowledge-base-management#article-structure" })] }), _jsx("input", { type: "text", value: title, onChange: (e) => setTitle(e.target.value), placeholder: "Article title...", style: inputStyle() })] }), _jsxs("div", { style: { marginBottom: '16px' }, children: [_jsxs("label", { style: {
                            display: 'block',
                            fontSize: '13px',
                            fontWeight: 600,
                            color: COLOR_TEXT,
                            marginBottom: '6px',
                        }, children: ["Category ", _jsx("span", { style: { color: COLOR_DANGER }, children: "*" })] }), !showNewCategory ? (_jsxs("div", { style: { display: 'flex', gap: '8px' }, children: [_jsxs("select", { value: category, onChange: (e) => setCategory(e.target.value), style: inputStyle({ flex: '1' }), children: [_jsx("option", { value: "", children: "Select category..." }), categories.map((cat) => (_jsx("option", { value: cat, children: cat }, cat)))] }), _jsx("button", { onClick: () => setShowNewCategory(true), style: buttonStyle('secondary'), title: "Create new category", children: "+ New" })] })) : (_jsxs("div", { style: { display: 'flex', gap: '8px' }, children: [_jsx("input", { type: "text", value: newCategory, onChange: (e) => setNewCategory(e.target.value), placeholder: "New category name...", style: inputStyle({ flex: '1' }) }), _jsx("button", { onClick: () => {
                                    setShowNewCategory(false);
                                    setNewCategory('');
                                }, style: buttonStyle('secondary'), children: "Cancel" })] }))] }), _jsxs("div", { style: { marginBottom: '16px' }, children: [_jsx("label", { style: {
                            display: 'block',
                            fontSize: '13px',
                            fontWeight: 600,
                            color: COLOR_TEXT,
                            marginBottom: '6px',
                        }, children: "Status" }), _jsxs("select", { value: status, onChange: (e) => setStatus(e.target.value), style: inputStyle({ width: '200px' }), children: [_jsx("option", { value: "draft", children: "Draft" }), _jsx("option", { value: "published", children: "Published" }), _jsx("option", { value: "archived", children: "Archived" })] })] }), _jsxs("div", { style: { marginBottom: '24px' }, children: [_jsxs("label", { style: {
                            display: 'block',
                            fontSize: '13px',
                            fontWeight: 600,
                            color: COLOR_TEXT,
                            marginBottom: '6px',
                        }, children: ["Content ", _jsx("span", { style: { color: COLOR_DANGER }, children: "*" }), _jsx(HelpTooltip, { text: "The full article text the AI will reference when answering questions." })] }), _jsx("textarea", { value: content, onChange: (e) => setContent(e.target.value), placeholder: "Write article content...", rows: 14, style: inputStyle({ resize: 'vertical', lineHeight: '1.6' }) })] }), _jsxs("div", { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' }, children: [_jsxs("div", { children: [!isNew && !confirmDelete && (_jsx("button", { onClick: () => setConfirmDelete(true), style: buttonStyle('danger'), children: "Delete" })), !isNew && confirmDelete && (_jsxs("div", { style: { display: 'flex', gap: '8px', alignItems: 'center' }, children: [_jsx("span", { style: { fontSize: '13px', color: COLOR_DANGER, fontWeight: 500 }, children: "Are you sure?" }), _jsx("button", { disabled: deleting, onClick: () => {
                                            if (article.id)
                                                onDelete(article.id);
                                        }, style: buttonStyle('danger', deleting), children: deleting ? 'Deleting...' : 'Confirm delete' }), _jsx("button", { onClick: () => setConfirmDelete(false), style: buttonStyle('secondary'), children: "Cancel" })] }))] }), _jsxs("div", { style: { display: 'flex', gap: '8px' }, children: [_jsx("button", { onClick: onCancel, style: buttonStyle('secondary'), children: "Cancel" }), _jsx("button", { disabled: !canSave || saving, onClick: handleSubmit, style: buttonStyle('primary', !canSave || saving), children: saving ? 'Saving...' : isNew ? 'Create article' : 'Save changes' })] })] })] }));
};
//# sourceMappingURL=ArticleEditor.js.map