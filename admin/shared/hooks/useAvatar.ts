/**
 * Avatar upload + delete hooks for the agent avatar image.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { useState, useCallback } from 'react';
import type { ApiFetch } from './useApi';

export interface AvatarUploadResult {
  success: boolean;
  avatar_url: string | null;
  size_bytes: number;
  message: string;
}

export interface AvatarDeleteResult {
  success: boolean;
  message: string;
}

/**
 * Upload an agent avatar image (PNG or JPEG, max 256 KB).
 * Returns a base64 data URI on success.
 */
export function useAvatarUpload(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<'idle' | 'uploading' | 'processing' | 'done'>('idle');

  const upload = useCallback(
    async (file: File): Promise<AvatarUploadResult | null> => {
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
          throw new Error(body.detail || `Upload failed: ${resp.status}`);
        }
        setProgress('done');
        return await resp.json();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Upload failed';
        setError(msg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFetch],
  );

  const reset = useCallback(() => {
    setProgress('idle');
    setError(null);
  }, []);

  return { upload, loading, error, progress, reset };
}

/**
 * Delete the current agent avatar (resets to initials fallback).
 */
export function useDeleteAvatar(apiFetch: ApiFetch) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const deleteAvatar = useCallback(async (): Promise<AvatarDeleteResult | null> => {
    setLoading(true);
    setError(null);
    try {
      const resp = await apiFetch('/api/admin/avatar', { method: 'DELETE' });
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({ detail: `${resp.status}` }));
        throw new Error(body.detail || `Delete failed: ${resp.status}`);
      }
      return await resp.json();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Delete failed';
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, [apiFetch]);

  return { deleteAvatar, loading, error };
}
