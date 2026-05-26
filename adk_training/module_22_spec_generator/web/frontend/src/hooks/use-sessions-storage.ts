import * as React from "react";
import type { Epic } from "@/api/client";

const STORAGE_KEY = "zagi.sessions.v1";
const MAX_SESSIONS = 20;

export interface StoredSession {
  id: string;
  issueKey: string;
  createdAt: number;
  mode: "real" | "scaffold";
  hldMarkdown: string;
  epics: Epic[];
  approved: boolean;
  iterations: number;
}

function read(): StoredSession[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function write(items: StoredSession[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items.slice(0, MAX_SESSIONS)));
  } catch {
    /* quota - silent */
  }
}

export function useSessionsStorage() {
  const [sessions, setSessions] = React.useState<StoredSession[]>(() => read());

  React.useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY) setSessions(read());
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const upsert = React.useCallback((s: StoredSession) => {
    setSessions((prev) => {
      const next = [s, ...prev.filter((x) => x.id !== s.id)].slice(0, MAX_SESSIONS);
      write(next);
      return next;
    });
  }, []);

  const remove = React.useCallback((id: string) => {
    setSessions((prev) => {
      const next = prev.filter((x) => x.id !== id);
      write(next);
      return next;
    });
  }, []);

  const clear = React.useCallback(() => {
    write([]);
    setSessions([]);
  }, []);

  return { sessions, upsert, remove, clear };
}
