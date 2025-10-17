import { useState } from "react";
import SetDisplayNameForm from "../templates/SetDisplayNameForm";
import { setDisplayName } from "../services/authService";
import { useAuth } from "../app/providers/AuthProvider";
import { useNavigate } from "react-router-dom";

export default function SetDisplayNamePage() {
  const { currentUser, refresh } = useAuth();
  const navigate = useNavigate();
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!currentUser) return <div style={{ padding: 24 }}>Please sign in first.</div>;

  async function submit() {
    setError(null); setIsSubmitting(true);
    try {
      await setDisplayName(value);
      await refresh();
      navigate("/rooms/new", { replace: true });
    } catch (e: any) {
      setError(e?.status === 409 ? "Display name is already taken." : (e?.message || "Could not save display name."));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <SetDisplayNameForm
      value={value}
      onChange={setValue}
      onSubmit={submit}
      isSubmitting={isSubmitting}
      error={error}
    />
  );
}
