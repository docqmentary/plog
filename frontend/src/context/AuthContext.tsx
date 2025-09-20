import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";

import type { SessionPayload } from "../types/api";

const STORAGE_KEY = "plog.session";

interface AuthContextValue {
  session: SessionPayload | null;
  setSession: (session: SessionPayload | null) => void;
  logout: () => void;
  isBootstrapping: boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: PropsWithChildren): JSX.Element {
  const [session, setSessionState] = useState<SessionPayload | null>(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as SessionPayload;
        setSessionState(parsed);
      }
    } catch (error) {
      console.warn("Failed to restore session", error);
    } finally {
      setIsBootstrapping(false);
    }
  }, []);

  const setSession = useCallback((value: SessionPayload | null) => {
    setSessionState(value);
    if (value) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const logout = useCallback(() => {
    setSession(null);
  }, [setSession]);

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      setSession,
      logout,
      isBootstrapping,
    }),
    [session, setSession, logout, isBootstrapping]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }
  return context;
}
