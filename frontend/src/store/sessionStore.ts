import { create } from 'zustand';
import type { SchemaPreview } from '../types';

interface SessionState {
  sessionId: string | null;
  fileName: string | null;
  schemaPreview: SchemaPreview | null;
  setSession: (id: string, fileName: string, schema: SchemaPreview) => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  fileName: null,
  schemaPreview: null,
  setSession: (id, fileName, schema) =>
    set({ sessionId: id, fileName, schemaPreview: schema }),
  clearSession: () =>
    set({ sessionId: null, fileName: null, schemaPreview: null }),
}));
