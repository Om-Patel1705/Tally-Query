import { useState } from 'react';
import { uploadFile } from '../api/client';
import { useSessionStore } from '../store/sessionStore';
import type { SchemaPreview } from '../types';

export const useUpload = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setSession = useSessionStore((state) => state.setSession);

  const upload = async (file: File) => {
    setIsLoading(true);
    setError(null);

    // Validate file type
    if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
      setError('Only .csv and .xlsx files are supported');
      setIsLoading(false);
      return null;
    }

    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('File size exceeds maximum of 10MB');
      setIsLoading(false);
      return null;
    }

    try {
      const response = await uploadFile(file);
      setSession(response.session_id, response.schema_preview.file_name, response.schema_preview);
      setIsLoading(false);
      return response;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to upload file';
      setError(errorMessage);
      setIsLoading(false);
      return null;
    }
  };

  return { upload, isLoading, error };
};
