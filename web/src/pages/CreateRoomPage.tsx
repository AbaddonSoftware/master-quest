// import { useNavigate } from "react-router-dom";
import { useState } from "react";
import CreateRoomForm from "../templates/CreateRoomForm";
import { useCreateRoom } from "../hooks/useCreateRoom";
import { useAuth } from "../app/providers/AuthProvider";
import RoundedButton from "../components/RoundedButton";

export default function CreateRoomPage() {
  const { currentUser } = useAuth();
  // const navigate = useNavigate();
  const { submit, isSubmitting, error, setError, createdRoom } = useCreateRoom();
  const [value, setValue] = useState("");

  if (!currentUser) return <div style={{ padding: 24 }}>Please sign in first.</div>;
  if (!currentUser.display_name?.trim()) return <div style={{ padding: 24 }}>Finish setup first.</div>;

  async function onSubmit() {
    try {
      await submit(value);
    } catch {
      /* error set in hook */
    }
  }

  if (createdRoom) {
    return (
      <div className="card">
        <h1 className="text-2xl font-bold">Room created!</h1>
        <p className="mb-4 text-stone-700">
          <strong>{createdRoom.name}</strong> is ready. Share the link or jump in now.
        </p>
        <RoundedButton
          href={`/rooms/${createdRoom.public_id}`}
          className="btn-primary"
          size="md"
        >
          Go to room
        </RoundedButton>
      </div>
    );
  }

  return (
    <CreateRoomForm
      value={value}
      onChange={(v) => {
        setError(null);
        setValue(v);
      }}
      onSubmit={onSubmit}
      isSubmitting={isSubmitting}
      error={error}
    />
  );
}
