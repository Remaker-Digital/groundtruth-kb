/**
 * Avatar upload + delete hooks for the agent avatar image.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { useState, useCallback } from 'react';
/**
 * Upload an agent avatar image (PNG or JPEG, max 256 KB).
 * Returns a base64 data URI on success.
 */
export function useAvatarUpload(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [progress, setProgress] = useState('idle');
    const upload = useCallback(async (file) => {
        setLoading(true);
        setError(null);
        setProgress('uploading');
        try {
            const formData = new FormData();
            formData.append('file', file);
            setProgress('processing');
            const resp = await apiFetch('/api/admin/avatar/upload', {
                method: 'POST',
                body: formData,
            });
            if (!resp.ok) {
                const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
                // RequestBodyLimitMiddleware returns { error: "..." } (not { detail }),
                // so check both fields. For 413, provide a user-friendly file-size hint.
                const serverMsg = body.detail || body.error;
                if (resp.status === 413) {
                    const maxKB = body.max_bytes ? Math.round(body.max_bytes / 1024) : 256;
                    throw new Error(`File too large. Maximum size is ${maxKB} KB — please resize and try again.`);
                }
                throw new Error(serverMsg || `Upload failed: ${resp.status}`);
            }
            setProgress('done');
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Upload failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    const reset = useCallback(() => {
        setProgress('idle');
        setError(null);
    }, []);
    return { upload, loading, error, progress, reset };
}
/**
 * Delete the current agent avatar (resets to initials fallback).
 */
export function useDeleteAvatar(apiFetch) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const deleteAvatar = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const resp = await apiFetch('/api/admin/avatar', { method: 'DELETE' });
            if (!resp.ok) {
                const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
                throw new Error(body.detail || `Delete failed: ${resp.status}`);
            }
            return await resp.json();
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : 'Delete failed';
            setError(msg);
            return null;
        }
        finally {
            setLoading(false);
        }
    }, [apiFetch]);
    return { deleteAvatar, loading, error };
}
//# sourceMappingURL=useAvatar.js.map