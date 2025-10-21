import type { ReactElement } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../app/providers/AuthProvider";

export default function RequireAuth({ children }: { children: ReactElement }) {
  const { currentUser, isLoading } = useAuth();
  if (isLoading) return null;
  return currentUser ? children : <Navigate to="/" replace />;
}
