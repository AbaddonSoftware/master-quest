import { Navigate } from "react-router-dom";
import { useAuth } from "../app/providers/AuthProvider";

export default function RequireDisplayName({ children }: { children: JSX.Element }) {
  const { currentUser } = useAuth();
  const ok = !!currentUser?.display_name && currentUser.display_name.trim() !== "";
  return ok ? children : <Navigate to="/onboarding" replace />;
}
