// import { useNavigate } from "react-router-dom";
import { useState } from "react";
import CreateRoomForm from "../templates/CreateRoomForm";
import { useCreateRoom } from "../hooks/useCreateRoom";
import { useAuth } from "../app/providers/AuthProvider";

export default function CreateRoomPage() {
  const { currentUser } = useAuth();
  // const navigate = useNavigate();
  const { submit, isSubmitting, error, setError } = useCreateRoom();
  const [value, setValue] = useState("");

  if (!currentUser) return <div style={{ padding: 24 }}>Please sign in first.</div>;
  if (!currentUser.display_name?.trim()) return <div style={{ padding: 24 }}>Finish setup first.</div>;

  async function onSubmit() {
    try {
      const public_id  = await submit(value);
      window.location.assign(`/api/rooms/${public_id}`);
    } catch {
      /* error already set in hook */
    }
  }

  return (
    <CreateRoomForm
      value={value}
      onChange={(v) => { setError(null); setValue(v); }}
      onSubmit={onSubmit}
      isSubmitting={isSubmitting}
      error={error}
    />
  );
}
