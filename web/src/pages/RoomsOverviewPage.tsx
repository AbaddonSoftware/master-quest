import { useEffect, useMemo, useState, type FormEvent } from "react";
import AppHeader from "../components/AppHeader";
import RoundedButton from "../components/RoundedButton";
import Modal from "../components/Modal";
import TextField from "../components/TextField";
import {
  acceptInvite,
  deleteRoom,
  fetchRooms,
  type RoomMember,
  type RoomSummary,
  type Role,
} from "../services/roomService";
import { useNavigate } from "react-router-dom";

const ROLE_LABELS: Record<Role, string> = {
  OWNER: "Owner",
  ADMIN: "Admin",
  MEMBER: "Member",
  VIEWER: "Viewer",
};

function describeMembershipRole(role: Role) {
  switch (role) {
    case "OWNER":
      return "You own this room";
    case "ADMIN":
      return "You can manage this room";
    case "MEMBER":
      return "You can collaborate here";
    default:
      return "You can view this room";
  }
}

function memberDisplayName(member: RoomMember) {
  return member.display_name?.trim() || member.name;
}

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

  const ownedRooms = useMemo(
    () => rooms.filter((room) => room.membership?.role === "OWNER"),
    [rooms]
  );
  const joinedRooms = useMemo(
    () => rooms.filter((room) => room.membership?.role !== "OWNER"),
    [rooms]
  );
  const hasRooms = ownedRooms.length > 0 || joinedRooms.length > 0;

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

  function renderRoomCard(room: RoomSummary) {
    const currentUserId = room.membership?.user_public_id ?? null;
    const visibleMembers = room.members.slice(0, 5);
    const remainingMemberCount = room.members.length - visibleMembers.length;
    const membershipLabel = describeMembershipRole(room.membership.role);
    const membershipBadgeTone =
      room.membership.role === "OWNER"
        ? "border-amber-200 bg-amber-100 text-amber-800"
        : "border-blue-200 bg-blue-100 text-blue-800";

    return (
      <div
        key={room.public_id}
        className="flex flex-col gap-3 rounded-2xl border border-amber-200 bg-white/85 p-5 shadow-sm"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex flex-col gap-2">
            <h2 className="text-lg font-semibold text-stone-900">
              {room.name}
            </h2>
            <span
              className={`inline-flex items-center gap-2 self-start rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-wide ${membershipBadgeTone}`}
            >
              {membershipLabel}
            </span>
          </div>
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
          <p className="text-xs uppercase tracking-wide text-stone-500">
            Members ({room.members.length})
          </p>
          <ul className="mt-2 flex flex-wrap gap-2">
            {visibleMembers.map((member) => {
              const label =
                member.user_public_id === currentUserId
                  ? "You"
                  : ROLE_LABELS[member.role];
              return (
                <li
                  key={member.user_public_id}
                  className="inline-flex items-center gap-2 rounded-full border border-stone-200 bg-stone-100 px-3 py-1 text-sm text-stone-700"
                >
                  <span className="font-medium text-stone-900">
                    {memberDisplayName(member)}
                  </span>
                  <span className="text-[11px] uppercase tracking-wide text-stone-500">
                    {label}
                  </span>
                </li>
              );
            })}
            {remainingMemberCount > 0 && (
              <li className="inline-flex items-center rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-sm text-stone-500">
                +{remainingMemberCount} more
              </li>
            )}
          </ul>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-stone-500">
            Boards
          </p>
          <ul className="mt-2 flex flex-col gap-2 text-sm text-stone-700">
            {room.boards.length ? (
              room.boards.map((board) => (
                <li
                  key={board.public_id}
                  className="flex items-center justify-between gap-3"
                >
                  <span className="line-clamp-2 break-words">{board.name}</span>
                </li>
              ))
            ) : (
              <li className="text-stone-500">No boards yet.</li>
            )}
          </ul>
        </div>

        {room.membership.role === "OWNER" && (
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
        )}
      </div>
    );
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

      <main className="flex flex-1 flex-col gap-6 p-6">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-stone-900">Your Rooms</h1>
            <p className="text-sm text-stone-600">
              Hop back into an existing board or create a new space for your next quest.
            </p>
          </div>
        </header>
        {isLoading && <p className="text-stone-600">Loading your rooms…</p>}
        {error && <p className="text-red-600">{error}</p>}

        {!isLoading && !error && !hasRooms && (
          <div className="rounded-2xl border border-dashed border-blue-200 bg-white/80 p-5 text-sm text-amber-700 shadow-sm">
            <p>You don’t have any rooms yet. Create your first one to get started.</p>
              <RoundedButton
              size="sm"
              className="btn-primary m-3"
              onClick={() => navigate("/rooms/new")}
              >
              Create your first room.
              </RoundedButton>
          </div>
        )}

        {ownedRooms.length > 0 && (
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-semibold text-stone-900">Rooms you own</h2>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {ownedRooms.map((room) => renderRoomCard(room))}
            </div>
          </section>
        )}

        {joinedRooms.length > 0 && (
          <section className="flex flex-col gap-3">
            <h2 className="text-xl font-semibold text-stone-900">
              Rooms you’re a member of
            </h2>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {joinedRooms.map((room) => renderRoomCard(room))}
            </div>
          </section>
        )}

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
      </main>
    </div>
  );
}
