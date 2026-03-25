import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
/**
 * FileUploadZone — drag-and-drop file upload area for importing KB content
 * from PDF, DOCX, CSV, or TXT files.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback, useRef } from 'react';
import { BRAND_PRIMARY, COLOR_BORDER, COLOR_LIGHT_GRAY, COLOR_TEXT, COLOR_TEXT_SECONDARY, COLOR_DANGER, BORDER_RADIUS, } from './styles';
const ACCEPTED_TYPES = '.pdf,.docx,.csv,.txt';
const ACCEPTED_LABELS = 'PDF, DOCX, CSV, TXT';
const MAX_FILE_SIZE_MB = 50;
export const FileUploadZone = ({ onFileSelected, uploading, progress, error }) => {
    const inputRef = useRef(null);
    const [dragOver, setDragOver] = useState(false);
    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setDragOver(false);
        if (uploading)
            return;
        const file = e.dataTransfer.files?.[0];
        if (file)
            onFileSelected(file);
    }, [onFileSelected, uploading]);
    const handleFileChange = useCallback((e) => {
        const file = e.target.files?.[0];
        if (file)
            onFileSelected(file);
        if (inputRef.current)
            inputRef.current.value = '';
    }, [onFileSelected]);
    const progressLabel = progress === 'uploading' ? 'Uploading...' : progress === 'processing' ? 'Processing document...' : '';
    return (_jsxs("div", { children: [_jsxs("div", { onDragOver: (e) => { e.preventDefault(); setDragOver(true); }, onDragLeave: () => setDragOver(false), onDrop: handleDrop, onClick: () => !uploading && inputRef.current?.click(), style: {
                    border: `2px dashed ${dragOver ? BRAND_PRIMARY : COLOR_BORDER}`,
                    borderRadius: BORDER_RADIUS,
                    padding: '40px 24px',
                    textAlign: 'center',
                    cursor: uploading ? 'default' : 'pointer',
                    backgroundColor: dragOver ? `${BRAND_PRIMARY}08` : COLOR_LIGHT_GRAY,
                    transition: 'all 0.2s ease',
                    opacity: uploading ? 0.7 : 1,
                }, children: [_jsx("input", { ref: inputRef, type: "file", accept: ACCEPTED_TYPES, onChange: handleFileChange, style: { display: 'none' } }), _jsx("div", { style: { fontSize: '32px', marginBottom: '8px' }, children: uploading ? String.fromCodePoint(0x23F3) : String.fromCodePoint(0x1F4C4) }), uploading ? (_jsxs("div", { children: [_jsx("span", { style: { fontSize: '14px', fontWeight: 500, color: COLOR_TEXT }, children: progressLabel }), _jsx("div", { style: { marginTop: '12px' }, children: _jsx("div", { style: {
                                        width: '200px', height: '4px', backgroundColor: COLOR_BORDER,
                                        borderRadius: '2px', margin: '0 auto', overflow: 'hidden',
                                    }, children: _jsx("div", { style: {
                                            height: '100%', backgroundColor: BRAND_PRIMARY,
                                            width: progress === 'uploading' ? '40%' : '80%',
                                            transition: 'width 0.5s ease',
                                            borderRadius: '2px',
                                        } }) }) })] })) : (_jsxs(_Fragment, { children: [_jsx("span", { style: { fontSize: '14px', fontWeight: 500, color: COLOR_TEXT }, children: "Drop a file here or click to browse" }), _jsx("br", {}), _jsxs("span", { style: { fontSize: '12px', color: COLOR_TEXT_SECONDARY, marginTop: '4px', display: 'inline-block' }, children: ["Supported: ", ACCEPTED_LABELS, " (max ", MAX_FILE_SIZE_MB, "MB)"] })] }))] }), error && (_jsx("div", { style: {
                    marginTop: '8px', padding: '8px 12px', backgroundColor: '#ffeef0',
                    border: `1px solid ${COLOR_DANGER}33`, borderRadius: BORDER_RADIUS,
                    fontSize: '13px', color: COLOR_DANGER,
                }, children: error }))] }));
};
//# sourceMappingURL=FileUploadZone.js.map