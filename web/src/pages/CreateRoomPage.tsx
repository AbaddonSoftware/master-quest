import { useState } from "react";
import AppHeader from "../components/AppHeader";
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

  return (
    <div className="flex min-h-screen flex-col bg-[#fffaf2]">
      <AppHeader />
      <main className="flex flex-1 items-center justify-center p-6">
        {createdRoom ? (
          <div className="w-full max-w-lg rounded-2xl border border-amber-200 bg-white/85 p-6 text-center shadow-sm">
            <h1 className="text-2xl font-bold text-stone-900">Room created!</h1>
            <p className="mb-4 mt-2 text-sm text-stone-700">
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
        ) : (
          <div className="w-full max-w-lg rounded-2xl border border-amber-200 bg-white/85 p-6 shadow-sm">
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
          </div>
        )}
      </main>
    </div>
  );
}
