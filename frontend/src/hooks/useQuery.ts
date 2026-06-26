import { useState } from 'react';
import { submitQuery } from '../api/client';
import { useSessionStore } from '../store/sessionStore';
import type { AnswerResponse } from '../types';

export const useQuery = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionId = useSessionStore((state) => state.sessionId);

  const query = async (question: string): Promise<AnswerResponse | null> => {
    setIsLoading(true);
    setError(null);

    if (!sessionId) {
      setError('No active session. Please upload a file first.');
      setIsLoading(false);
      console.error('No active session');
      return null;
    }

    if (!question.trim()) {
      setError('Question cannot be empty');
      setIsLoading(false);
      console.error('Empty question');
      return null;
    }

    try {
      console.log('Submitting query:', { sessionId, question });
      const response = await submitQuery(sessionId, question);
      console.log('Query response received:', response);
      setIsLoading(false);
      return response;
    } catch (err: any) {
      console.error('Query error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to process query';
      setError(errorMessage);
      setIsLoading(false);
      return null;
    }
  };

  return { query, isLoading, error };
};
