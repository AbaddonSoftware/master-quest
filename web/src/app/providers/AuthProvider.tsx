import React, { createContext, useContext, useEffect, useState } from "react";
import { getCurrentUser, signOut, beginGoogleOAuth } from "../../services/authService";
import { useNavigate } from "react-router-dom";
import type { User } from "../../types/user";

type AuthContext = {
  currentUser: User | null;
  isLoading: boolean;
  refresh: () => Promise<void>;
  beginGoogleOAuth: () => void;
  signOut: () => Promise<void>;
};

const Ctx = createContext<AuthContext | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  const refresh = async () => {
    try {
      const me = await getCurrentUser();
      setCurrentUser(me);
    } catch {
      setCurrentUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { void refresh(); }, []);

  return (
    <Ctx.Provider value={{
      currentUser, isLoading, refresh,
      beginGoogleOAuth,
      signOut: async () => { try { await signOut(); } finally { setCurrentUser(null); navigate("/", { replace: true }); } }
    }}>
      {children}
    </Ctx.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
