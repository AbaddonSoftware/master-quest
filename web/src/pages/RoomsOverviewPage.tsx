import { useEffect, useMemo, useState, type FormEvent } from "react";
import RoundedButton from "../components/RoundedButton";
import Modal from "../components/Modal";
import TextField from "../components/TextField";
import { acceptInvite, deleteRoom, fetchRooms, type RoomSummary } from "../services/roomService";
import { useNavigate } from "react-router-dom";

export default function RoomsOverviewPage() {
  const navigate = useNavigate();
  const [rooms, setRooms] = useState<RoomSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setLoading] = useState(true);
  const [roomToDelete, setRoomToDelete] = useState<RoomSummary | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState("");
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [isDeleting, setDeleting] = useState(false);
  const [inviteCode, setInviteCode] = useState("");
  const [joinError, setJoinError] = useState<string | null>(null);
  const [joinNotice, setJoinNotice] = useState<string | null>(null);
  const [isJoining, setJoining] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchRooms()
      .then((data) => {
        setRooms(data.rooms ?? []);
      })
      .catch((err: any) => {
        setError(err?.message || "Unable to load your rooms right now.");
      })
      .finally(() => setLoading(false));
  }, []);

  const hasRooms = useMemo(() => rooms.length > 0, [rooms]);

  async function handleJoin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = inviteCode.trim();
    if (!trimmed) {
      setJoinError("Enter an invite code to join a room.");
      return;
    }
    setJoining(true);
    setJoinError(null);
    setJoinNotice(null);
    try {
      const response = await acceptInvite(trimmed);
      setJoinNotice(`Joined ${response.room.name}.`);
      setInviteCode("");
      const refreshed = await fetchRooms();
      setRooms(refreshed.rooms ?? []);
    } catch (err: any) {
      setJoinError(err?.message || "Could not join the room.");
    } finally {
      setJoining(false);
    }
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-stone-900">Your Rooms</h1>
          <p className="text-sm text-stone-600">
            Hop back into an existing board or create a new space for your next quest.
          </p>
        </div>
        <RoundedButton
          className="btn-primary"
          onClick={() => navigate("/rooms/new")}
        >
          + Create room
        </RoundedButton>
      </header>

      <section className="rounded-2xl border border-blue-200 bg-white/80 p-4 shadow-sm">
        <form onSubmit={handleJoin} className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <TextField
            label="Have an invite code?"
            value={inviteCode}
            onChange={setInviteCode}
            placeholder="Enter code"
            maxLength={40}
            required
          />
          <RoundedButton type="submit" className="btn-sort" disabled={isJoining}>
            {isJoining ? "Joining…" : "Join room"}
          </RoundedButton>
        </form>
        {(joinError || joinNotice) && (
          <p className={`mt-2 text-sm ${joinError ? "text-red-600" : "text-green-700"}`}>
            {joinError ?? joinNotice}
          </p>
        )}
      </section>

      {isLoading && <p className="text-stone-600">Loading your rooms…</p>}
      {error && <p className="text-red-600">{error}</p>}

      {!isLoading && !error && !hasRooms && (
        <div className="rounded-2xl border border-dashed border-amber-300 bg-amber-50/70 p-5 text-sm text-amber-700">
          You don’t have any rooms yet. Create your first one to get started.
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {rooms.map((room) => (
        <div
          key={room.public_id}
          className="flex flex-col gap-3 rounded-2xl border border-amber-200 bg-white/85 p-5 shadow-sm"
        >
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-stone-900">{room.name}</h2>
              <RoundedButton
                size="sm"
                className="btn-sort"
                onClick={() => navigate(`/rooms/${room.public_id}`)}
              >
                Open room
              </RoundedButton>
            </div>

            <p className="text-xs text-stone-500">
              Room ID: <code className="text-[11px]">{room.public_id}</code>
            </p>

            <div>
              <p className="text-xs uppercase tracking-wide text-stone-500">Boards</p>
              <ul className="mt-2 flex flex-col gap-2 text-sm text-stone-700">
                {room.boards.length ? (
                  room.boards.map((board) => (
                    <li key={board.public_id} className="flex items-center justify-between gap-3">
                      <span className="line-clamp-2 break-words">{board.name}</span>
                      <RoundedButton
                        size="sm"
                        className="btn-login"
                        onClick={() => navigate(`/rooms/${room.public_id}`)}
                      >
                        Enter
                      </RoundedButton>
                    </li>
                  ))
                ) : (
                  <li className="text-stone-500">No boards yet.</li>
                )}
              </ul>
            </div>

            <RoundedButton
              size="sm"
              className="btn-sort self-end text-red-700 hover:text-red-900"
              onClick={() => {
                setRoomToDelete(room);
                setDeleteConfirm("");
                setDeleteError(null);
              }}
            >
              Delete room
            </RoundedButton>
          </div>
        ))}
      </div>

      <Modal
        open={roomToDelete !== null}
        onClose={() => {
          if (isDeleting) return;
          setRoomToDelete(null);
          setDeleteConfirm("");
          setDeleteError(null);
        }}
        title="Delete room"
      >
        {roomToDelete && (
          <form
            onSubmit={async (event) => {
              event.preventDefault();
              if (!roomToDelete) return;
              if (deleteConfirm.trim().toUpperCase() !== "DELETE") {
                setDeleteError("Type DELETE to confirm.");
                return;
              }
              setDeleting(true);
              setDeleteError(null);
              try {
                await deleteRoom(roomToDelete.public_id);
                setRooms((prev) => prev.filter((r) => r.public_id !== roomToDelete.public_id));
                setRoomToDelete(null);
                setDeleteConfirm("");
              } catch (err: any) {
                setDeleteError(err?.message || "Failed to delete room.");
              } finally {
                setDeleting(false);
              }
            }}
            className="flex flex-col gap-4"
          >
            <p className="text-sm text-stone-700">
              This will permanently delete <strong>{roomToDelete.name}</strong> and every board, column, and card inside it.
              There is no undo.
            </p>
            <TextField
              label="Type DELETE to confirm"
              value={deleteConfirm}
              onChange={setDeleteConfirm}
              required
            />
            {deleteError && <p style={{ color: "crimson" }}>{deleteError}</p>}
            <RoundedButton type="submit" disabled={isDeleting} className="btn-sort text-red-700 hover:text-red-900">
              {isDeleting ? "Deleting…" : "Delete room"}
            </RoundedButton>
          </form>
        )}
      </Modal>
    </div>
  );
}
