import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import SetDisplayNameForm from "../templates/SetDisplayNameForm";
import { setDisplayName } from "../services/authService";
import { fetchRooms, type RoomSummary } from "../services/roomService";
import { useAuth } from "../app/providers/AuthProvider";
import RoundedButton from "../components/RoundedButton";
import AppHeader from "../components/AppHeader";

export default function SetDisplayNamePage() {
  const { currentUser, refresh } = useAuth();
  const navigate = useNavigate();
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [rooms, setRooms] = useState<RoomSummary[]>([]);
  const [roomsError, setRoomsError] = useState<string | null>(null);
  const [isLoadingRooms, setLoadingRooms] = useState(false);

  useEffect(() => {
    if (!currentUser) return;
    setLoadingRooms(true);
    setRoomsError(null);
    fetchRooms()
      .then((data) => {
        setRooms(data.rooms ?? []);
      })
      .catch((err: any) => {
        setRoomsError(err?.message || "Unable to load your rooms right now.");
      })
      .finally(() => setLoadingRooms(false));
  }, [currentUser]);

  const hasRooms = useMemo(() => rooms.length > 0, [rooms]);

  if (!currentUser) return <div style={{ padding: 24 }}>Please sign in first.</div>;

  async function submit() {
    setError(null);
    setIsSubmitting(true);
    try {
      await setDisplayName(value);
      await refresh();
      navigate("/rooms", { replace: true });
    } catch (e: any) {
      setError(
        e?.status === 409
          ? "Display name is already taken."
          : e?.message || "Could not save display name."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-[#fffaf2]">
      <AppHeader
        extraActions={
          <RoundedButton
            size="sm"
            className="btn-primary"
            onClick={() => navigate("/rooms/new")}
          >
            + Create room
          </RoundedButton>
        }
      />

      <main className="flex flex-1 flex-col gap-8 p-6">
        <SetDisplayNameForm
          value={value}
          onChange={setValue}
          onSubmit={submit}
          isSubmitting={isSubmitting}
          error={error}
        />

        <section className="flex flex-col gap-4">
          <header>
            <h2 className="text-xl font-semibold text-stone-900">Your rooms & boards</h2>
            <p className="text-sm text-stone-600">
              Jump back into a board you already crafted or head to the room creator when you’re ready for a fresh quest.
            </p>
          </header>

          {isLoadingRooms && <p className="text-stone-600">Loading your rooms…</p>}
          {roomsError && <p className="text-red-600">{roomsError}</p>}

          {!isLoadingRooms && !roomsError && !hasRooms && (
            <div className="rounded-xl border border-dashed border-amber-300 bg-amber-50/70 p-4 text-sm text-amber-700">
              No rooms yet. Create your first one to get started.
            </div>
          )}

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {rooms.map((room) => (
              <div
                key={room.public_id}
                className="rounded-2xl border border-amber-200 bg-white/80 p-4 shadow-sm"
              >
                <h3 className="text-lg font-semibold text-stone-900">{room.name}</h3>
                <p className="mt-1 text-xs uppercase tracking-wide text-stone-500">Boards</p>
                <ul className="mt-2 flex flex-col gap-2 text-sm text-stone-700">
                  {room.boards.length ? (
                    room.boards.map((board) => (
                      <li key={board.public_id} className="flex items-center justify-between gap-3">
                        <span className="line-clamp-2 break-words">{board.name}</span>
                        <RoundedButton
                          size="sm"
                          className="btn-sort"
                          onClick={() => navigate(`/rooms/${room.public_id}`)}
                        >
                          Open
                        </RoundedButton>
                      </li>
                    ))
                  ) : (
                    <li className="text-stone-500">This room has no boards yet.</li>
                  )}
                </ul>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
