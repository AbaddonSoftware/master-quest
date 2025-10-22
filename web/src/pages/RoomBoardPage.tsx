import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import type { FormEvent } from "react";
import { useParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import AppHeader from "../components/AppHeader";
import BoardColumn from "../components/BoardColumn";
import Modal from "../components/Modal";
import TextField from "../components/TextField";
import RoundedButton from "../components/RoundedButton";
import ManageRoomModal from "../components/ManageRoomModal";
import { useRoomBoard } from "../hooks/useRoomBoard";
import {
  createBoardColumn,
  createCard,
  updateBoard,
  updateBoardColumn,
  updateCard,
  archiveColumn,
  archiveCard,
  restoreColumn,
  restoreCard,
  fetchBoardArchive,
  type BoardArchiveResponse,
} from "../services/boardService";
import { leaveRoom } from "../services/roomService";
import type { Role, RoomMember } from "../services/roomService";

const ROLE_LABELS: Record<Role, string> = {
  OWNER: "Owner",
  ADMIN: "Admin",
  MEMBER: "Member",
  VIEWER: "Viewer",
};

const ROLE_WEIGHT: Record<Role, number> = {
  OWNER: 0,
  ADMIN: 1,
  MEMBER: 2,
  VIEWER: 3,
};

function memberDisplayName(member: RoomMember) {
  return member.display_name?.trim() || member.name;
}

export default function RoomBoardPage() {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();
  const { isLoading, error, board, columns, room, reload } = useRoomBoard(roomId);

  const [isBoardModalOpen, setBoardModalOpen] = useState(false);
  const [boardDraft, setBoardDraft] = useState("");
  const [boardError, setBoardError] = useState<string | null>(null);
  const [isBoardSaving, setBoardSaving] = useState(false);
  const [isMembersModalOpen, setMembersModalOpen] = useState(false);

  const [editingColumn, setEditingColumn] = useState<{
    id: number;
    title: string;
    wipLimit: number | null;
  } | null>(null);
  const [columnDraft, setColumnDraft] = useState({ title: "", wip_limit: "" });
  const [columnError, setColumnError] = useState<string | null>(null);
  const [isColumnSaving, setColumnSaving] = useState(false);
  const [isCreatingColumn, setCreatingColumn] = useState(false);

  const [editingCard, setEditingCard] = useState<{
    mode: "edit" | "create";
    id?: string;
    columnId: number;
    title: string;
    description: string;
  } | null>(null);
  const [cardDraft, setCardDraft] = useState({
    title: "",
    description: "",
    column_id: 0,
  });
  const [cardError, setCardError] = useState<string | null>(null);
  const [isCardSaving, setCardSaving] = useState(false);
  const [archive, setArchive] = useState<BoardArchiveResponse>({ columns: [], cards: [] });
  const [archiveError, setArchiveError] = useState<string | null>(null);
  const [archiveNotice, setArchiveNotice] = useState<string | null>(null);
  const [isArchiveLoading, setArchiveLoading] = useState(false);
  const [isArchiveOpen, setArchiveOpen] = useState(false);
  const [isMembersListOpen, setMembersListOpen] = useState(false);
  const [leaveError, setLeaveError] = useState<string | null>(null);
  const [isLeaving, setLeaving] = useState(false);

  const groupedColumns = useMemo(
    () => columns.filter((column) => column.parent_id === null),
    [columns]
  );

  useEffect(() => {
    if (board) {
      setBoardDraft(board.name);
    }
  }, [board?.name]);

  const loadArchive = useCallback(async () => {
    if (!roomId || !board?.public_id) return;
    setArchiveLoading(true);
    setArchiveNotice(null);
    try {
      const data = await fetchBoardArchive(roomId, board.public_id);
      setArchive(data);
      setArchiveError(null);
    } catch (err: any) {
      setArchiveError(err?.message || "Could not load archived items.");
    } finally {
      setArchiveLoading(false);
    }
  }, [roomId, board?.public_id]);

  useEffect(() => {
    if (board) {
      void loadArchive();
    }
  }, [board?.public_id, loadArchive]);

  const columnOptions = useMemo(
    () =>
      groupedColumns.map((column) => ({
        id: column.id,
        title: column.title,
      })),
    [groupedColumns]
  );

  const membershipRole: Role = room?.membership?.role ?? "VIEWER";
  const membershipUserPublicId = room?.membership?.user_public_id ?? null;
  const sortedMembers = useMemo(() => {
    const members = room?.members ?? [];
    return members.slice().sort((a, b) => {
      const weightDiff = ROLE_WEIGHT[a.role] - ROLE_WEIGHT[b.role];
      if (weightDiff !== 0) return weightDiff;
      const aHasDisplay = a.display_name ? 0 : 1;
      const bHasDisplay = b.display_name ? 0 : 1;
      if (aHasDisplay !== bHasDisplay) return aHasDisplay - bHasDisplay;
      const nameA = memberDisplayName(a).toLocaleLowerCase();
      const nameB = memberDisplayName(b).toLocaleLowerCase();
      if (nameA < nameB) return -1;
      if (nameA > nameB) return 1;
      return 0;
    });
  }, [room?.members]);
  const membershipLabel = ROLE_LABELS[membershipRole];
  const canManageRoom = membershipRole === "OWNER" || membershipRole === "ADMIN";
  const canLeaveRoom = membershipRole !== "OWNER";

  async function handleLeaveRoom() {
    if (!roomId) return;
    const confirmed = window.confirm(
      "Leave this room? You’ll lose access to its boards until someone invites you back."
    );
    if (!confirmed) return;
    setLeaving(true);
    setLeaveError(null);
    try {
      await leaveRoom(roomId);
      navigate("/rooms");
    } catch (err: any) {
      setLeaveError(err?.message || "Could not leave the room.");
    } finally {
      setLeaving(false);
    }
  }

  let mainContent: ReactNode;
  if (isLoading) {
    mainContent = <p className="text-stone-700">Loading board…</p>;
  } else if (error) {
    mainContent = (
      <div className="rounded-2xl border border-red-200 bg-red-50/70 p-4 text-sm text-red-700">
        <p className="font-semibold">Unable to load board.</p>
        <p className="mt-1 text-red-600">{error}</p>
      </div>
    );
  } else if (!board) {
    mainContent = (
      <div className="rounded-2xl border border-amber-200 bg-white/85 p-6 text-stone-700">
        <h1 className="text-xl font-semibold text-stone-900">No boards yet</h1>
        <p className="mt-2 text-sm text-stone-600">
          Create your first board to start organising tasks in this room.
        </p>
      </div>
    );
  } else {
    mainContent = (
      <>
        <section className="flex flex-1 flex-col gap-4 pb-4 -mx-2 px-2 sm:px-4 md:flex-row md:flex-nowrap md:overflow-x-auto">
          {groupedColumns.length ? (
            groupedColumns.map((column) => (
              <BoardColumn
                key={column.id}
                id={column.id}
                title={column.title}
                wipLimit={column.wip_limit}
                cards={column.cards.map((card) => ({
                  id: card.id,
                  title: card.title,
                  description: card.description,
                  columnId: column.id,
                }))}
                onEditColumn={openColumnModal}
                onColumnDoubleClick={(columnId) =>
                  openColumnModal(columnId, column.title, column.wip_limit ?? null)
                }
                onEditCard={(cardId, columnId, initial) =>
                  openCardModal(columnId, initial, "edit", cardId)
                }
                onAddCard={(columnId) =>
                  openCardModal(columnId, { title: "", description: "" }, "create")
                }
                onArchiveColumn={handleArchiveColumn}
                onArchiveCard={handleArchiveCard}
              />
            ))
          ) : (
            <div className="mt-8 text-stone-600">
              This board does not have any columns yet. Create one to get started.
            </div>
          )}
          <div className="flex flex-1 flex-col md:flex-none">
            <button
              type="button"
              onClick={() => {
                setCreatingColumn(true);
                setEditingColumn({ id: 0, title: "", wipLimit: null });
                setColumnDraft({ title: "", wip_limit: "" });
                setColumnError(null);
              }}
              className="flex w-full flex-shrink-0 items-center justify-center rounded-2xl border border-dashed border-blue-300 bg-blue-50/50 p-4 text-sm font-semibold text-blue-700 transition hover:border-blue-500 hover:bg-blue-100 md:w-52 lg:w-56 xl:w-60"
            >
              + Add column
            </button>
          </div>
        </section>

        <div className="fixed bottom-6 right-6 flex flex-col items-end gap-2">
          <RoundedButton
            size="sm"
            className="btn-sort"
            onClick={() => setArchiveOpen((prev) => !prev)}
          >
            {isArchiveOpen
              ? "Hide archived"
              : `Archived (${archive.columns.length + archive.cards.length})`}
          </RoundedButton>
          {isArchiveOpen && (
            <div className="w-80 max-h-96 overflow-y-auto rounded-2xl border border-amber-200 bg-white/95 p-4 shadow-xl">
              <h3 className="text-lg font-semibold text-stone-900">Archived items</h3>
              {archiveNotice && <p className="text-xs text-green-700">{archiveNotice}</p>}
              {archiveError && <p className="text-xs text-red-600">{archiveError}</p>}
              {isArchiveLoading ? (
                <p className="text-sm text-stone-600">Loading…</p>
              ) : (
                <div className="mt-2 flex flex-col gap-4 text-sm text-stone-700">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-stone-500">Columns</p>
                    {archive.columns.length ? (
                      <ul className="mt-1 flex flex-col gap-2">
                        {archive.columns.map((column) => (
                          <li
                            key={column.id}
                            className="flex items-center justify-between gap-2"
                          >
                            <span className="line-clamp-2 break-words">{column.title}</span>
                            <RoundedButton
                              size="sm"
                              className="btn-login"
                              onClick={() => handleRestoreColumn(column.id)}
                            >
                              Restore
                            </RoundedButton>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-xs text-stone-500">No archived columns.</p>
                    )}
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-stone-500">Cards</p>
                    {archive.cards.length ? (
                      <ul className="mt-1 flex flex-col gap-2">
                        {archive.cards.map((card) => (
                          <li
                            key={card.public_id}
                            className="flex items-center justify-between gap-2"
                          >
                            <span className="line-clamp-2 break-words">{card.title}</span>
                            <RoundedButton
                              size="sm"
                              className="btn-login"
                              onClick={() => handleRestoreCard(card.public_id, card.column_id)}
                            >
                              Restore
                            </RoundedButton>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-xs text-stone-500">No archived cards.</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </>
    );
  }

  const headerActions = (
    <>
      <RoundedButton
        size="sm"
        className="btn-sort"
        onClick={() => setMembersListOpen(true)}
      >
        View members
      </RoundedButton>
      {canManageRoom && (
        <RoundedButton
          size="sm"
          className="btn-login"
          onClick={() => setMembersModalOpen(true)}
        >
          Manage Room
        </RoundedButton>
      )}
      {board && (
        <RoundedButton
          size="sm"
          className="btn-sort"
          onClick={() => setBoardModalOpen(true)}
        >
          Edit board
        </RoundedButton>
      )}
      {canLeaveRoom && room && (
        <RoundedButton
          size="sm"
          className="btn-sort text-red-700 hover:text-red-900"
          disabled={isLeaving}
          onClick={handleLeaveRoom}
        >
          {isLeaving ? "Leaving…" : "Leave room"}
        </RoundedButton>
      )}
    </>
  );

  async function handleBoardSave(event: FormEvent) {
    event.preventDefault();
    if (!roomId || !board) return;
    setBoardSaving(true);
    setBoardError(null);
    try {
      await updateBoard(roomId, board.public_id, boardDraft.trim());
      setBoardModalOpen(false);
      reload();
      void loadArchive();
    } catch (err: any) {
      setBoardError(err?.message || "Could not update board name.");
    } finally {
      setBoardSaving(false);
    }
  }

  function openColumnModal(columnId: number, title: string, wipLimit: number | null) {
    setCreatingColumn(false);
    setEditingColumn({
      id: columnId,
      title,
      wipLimit,
    });
    setColumnDraft({
      title,
      wip_limit: wipLimit != null ? String(wipLimit) : "",
    });
    setColumnError(null);
  }

  async function handleColumnSave(event: FormEvent) {
    event.preventDefault();
    if (!roomId || !board) return;
    setColumnSaving(true);
    setColumnError(null);
    try {
      if (isCreatingColumn) {
       const trimmed = columnDraft.title.trim();
       if (trimmed.length < 3) {
          setColumnError("Column title must be at least 3 characters long.");
          setColumnSaving(false);
          return;
        }
        const payload = {
          title: trimmed,
          wip_limit:
            columnDraft.wip_limit === ""
              ? null
              : Number.isNaN(Number(columnDraft.wip_limit))
              ? null
              : Number(columnDraft.wip_limit),
        };
        await createBoardColumn(roomId, board.public_id, payload);
        setCreatingColumn(false);
        setEditingColumn(null);
        setColumnDraft({ title: "", wip_limit: "" });
        reload();
        void loadArchive();
        return;
      }
      if (!editingColumn) return;
      const payload = {
        title: columnDraft.title.trim() || editingColumn.title,
        wip_limit:
          columnDraft.wip_limit === ""
            ? null
            : Number.isNaN(Number(columnDraft.wip_limit))
            ? editingColumn.wipLimit
            : Number(columnDraft.wip_limit),
      };
      await updateBoardColumn(roomId, board.public_id, editingColumn.id, payload);
      setEditingColumn(null);
      reload();
      void loadArchive();
    } catch (err: any) {
      setColumnError(err?.message || "Could not update column.");
    } finally {
      setColumnSaving(false);
    }
  }

  function openCardModal(
    columnId: number,
    initial: { title: string; description: string | null },
    mode: "edit" | "create",
    cardId?: string
  ) {
    setEditingCard({
      mode,
      id: cardId,
      columnId,
      title: initial.title,
      description: initial.description ?? "",
    });
    setCardDraft({
      title: initial.title,
      description: initial.description ?? "",
      column_id: columnId,
    });
    setCardError(null);
  }

  async function handleCardSave(event: FormEvent) {
    event.preventDefault();
    if (!roomId || !editingCard || !board) return;
    setCardSaving(true);
    setCardError(null);
    try {
      if (editingCard.mode === "create") {
        const trimmed = cardDraft.title.trim();
        if (!trimmed.length) {
          setCardError("Please provide a card title.");
          setCardSaving(false);
          return;
        }
        await createCard(roomId, board.public_id, cardDraft.column_id, {
          title: trimmed,
          description: cardDraft.description,
        });
      } else if (editingCard.id) {
        const trimmed = cardDraft.title.trim();
        if (!trimmed.length) {
          setCardError("Card title cannot be empty.");
          setCardSaving(false);
          return;
        }
        await updateCard(roomId, board.public_id, editingCard.columnId, editingCard.id, {
          title: trimmed || editingCard.title,
          description: cardDraft.description,
          column_id: cardDraft.column_id,
        });
      }
      setEditingCard(null);
      reload();
      void loadArchive();
    } catch (err: any) {
      setCardError(err?.message || "Could not update card.");
    } finally {
      setCardSaving(false);
    }
  }

  async function handleArchiveColumn(columnId: number) {
    if (!roomId || !board) return;
    const confirmed = window.confirm("Archive this entire column and its cards?");
    if (!confirmed) return;
    try {
      await archiveColumn(roomId, board.public_id, columnId);
      setArchiveNotice("Column archived.");
      reload();
      await loadArchive();
    } catch (err: any) {
      setArchiveError(err?.message || "Could not archive column.");
    }
  }

  async function handleRestoreColumn(columnId: number) {
    if (!roomId || !board) return;
    try {
      await restoreColumn(roomId, board.public_id, columnId);
      setArchiveNotice("Column restored.");
      reload();
      await loadArchive();
    } catch (err: any) {
      setArchiveError(err?.message || "Could not restore column.");
    }
  }

  async function handleArchiveCard(cardId: string, columnId: number) {
    if (!roomId || !board) return;
    try {
      await archiveCard(roomId, board.public_id, columnId, cardId);
      setArchiveNotice("Card archived.");
      reload();
      await loadArchive();
    } catch (err: any) {
      setArchiveError(err?.message || "Could not archive card.");
    }
  }

  async function handleRestoreCard(cardId: string, columnId: number) {
    if (!roomId || !board) return;
    try {
      await restoreCard(roomId, board.public_id, columnId, cardId);
      setArchiveNotice("Card restored.");
      reload();
      await loadArchive();
    } catch (err: any) {
      setArchiveError(err?.message || "Could not restore card.");
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-[#fffaf2]">
      <AppHeader extraActions={headerActions}>
        {room ? (
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex flex-col gap-1">
              <p className="text-xs uppercase tracking-wide text-stone-500">
                Room · {room.name}
              </p>
              {board && (
                <p className="text-sm text-stone-600">
                  Active board:{" "}
                  <span className="font-semibold text-stone-900">{board.name}</span>
                </p>
              )}
              <p className="text-xs text-stone-500">Your role: {membershipLabel}</p>
            </div>
            <div className="flex flex-col gap-1 md:items-end">
              <p className="text-xs uppercase tracking-wide text-stone-500">
                Members ({sortedMembers.length})
              </p>
              <div className="flex flex-wrap gap-2">
                {sortedMembers.length ? (
                  sortedMembers.map((member) => (
                    <span
                      key={member.user_public_id}
                      className="inline-flex items-center gap-2 rounded-full border border-stone-200 bg-white/70 px-3 py-1 text-xs text-stone-700"
                    >
                      <span className="font-medium text-stone-900">
                        {memberDisplayName(member)}
                      </span>
                      <span className="text-[10px] uppercase tracking-wide text-stone-500">
                        {member.user_public_id === membershipUserPublicId
                          ? "You"
                          : ROLE_LABELS[member.role]}
                      </span>
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-stone-500">No members yet.</span>
                )}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-sm text-stone-600">Loading room details…</p>
        )}
      </AppHeader>

      <main className="flex flex-1 flex-col gap-4 p-6">
        {leaveError && (
          <div className="rounded-xl border border-red-200 bg-red-50/70 p-3 text-sm text-red-700">
            {leaveError}
          </div>
        )}
        {mainContent}
      </main>

      <Modal
        open={isMembersListOpen}
        onClose={() => setMembersListOpen(false)}
        title="Room members"
      >
        {sortedMembers.length ? (
          <ul className="flex flex-col gap-3">
            {sortedMembers.map((member) => {
              const descriptor =
                member.user_public_id === membershipUserPublicId
                  ? `You — ${ROLE_LABELS[member.role]}`
                  : ROLE_LABELS[member.role];
              return (
                <li
                  key={member.user_public_id}
                  className="rounded-xl border border-stone-200 bg-white/80 p-3"
                >
                  <p className="text-sm font-semibold text-stone-900">
                    {memberDisplayName(member)}
                  </p>
                  <p className="text-xs uppercase tracking-wide text-stone-500">
                    {descriptor}
                  </p>
                  {member.email && (
                    <p className="text-xs text-stone-500">{member.email}</p>
                  )}
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="text-sm text-stone-600">No other members yet.</p>
        )}
      </Modal>

      <Modal
        open={isBoardModalOpen}
        onClose={() => setBoardModalOpen(false)}
        title="Rename board"
      >
        <form onSubmit={handleBoardSave} className="flex flex-col gap-4">
          <TextField
            label="Board name"
            value={boardDraft}
            onChange={setBoardDraft}
            minLength={3}
            maxLength={64}
            required
          />
          {boardError && <p style={{ color: "crimson" }}>{boardError}</p>}
          <RoundedButton type="submit" disabled={isBoardSaving} className="btn-primary">
            {isBoardSaving ? "Saving…" : "Save"}
          </RoundedButton>
        </form>
      </Modal>

      {roomId && (
        <ManageRoomModal
          roomId={roomId}
          open={isMembersModalOpen}
          onClose={() => {
            setMembersModalOpen(false);
            reload();
          }}
        />
      )}

      <Modal
        open={editingColumn !== null}
        onClose={() => {
          setEditingColumn(null);
          setCreatingColumn(false);
        }}
        title={isCreatingColumn ? "Add column" : "Edit column"}
      >
        {editingColumn && (
          <form onSubmit={handleColumnSave} className="flex flex-col gap-4">
            <TextField
              label="Title"
              value={columnDraft.title}
              onChange={(value) => setColumnDraft((prev) => ({ ...prev, title: value }))}
              minLength={3}
              maxLength={64}
              required
            />
            <TextField
              label="WIP limit (leave blank for no limit)"
              type="number"
              value={columnDraft.wip_limit}
              onChange={(value) => setColumnDraft((prev) => ({ ...prev, wip_limit: value }))}
              min={0}
            />
            {columnError && <p style={{ color: "crimson" }}>{columnError}</p>}
            <RoundedButton type="submit" disabled={isColumnSaving} className="btn-primary">
              {isColumnSaving ? "Saving…" : isCreatingColumn ? "Create" : "Save"}
            </RoundedButton>
          </form>
        )}
      </Modal>

      <Modal
        open={editingCard !== null}
        onClose={() => setEditingCard(null)}
        title={editingCard?.mode === "create" ? "Add card" : "Edit card"}
      >
        {editingCard && (
          <form onSubmit={handleCardSave} className="flex flex-col gap-4">
            <TextField
              label="Title"
              value={cardDraft.title}
              onChange={(value) => setCardDraft((prev) => ({ ...prev, title: value }))}
              minLength={1}
              maxLength={255}
              required
            />
            <label className="flex flex-col gap-1 text-sm font-medium text-stone-700">
              Description
              <textarea
                value={cardDraft.description}
                onChange={(event) =>
                  setCardDraft((prev) => ({ ...prev, description: event.target.value }))
                }
                rows={4}
                className="rounded-lg border border-[#cbb98e] bg-[#fffaf2] px-3 py-2 focus:border-[#b2925a] focus:outline-none focus:ring-2 focus:ring-[rgba(178,146,90,0.30)]"
              />
            </label>
            <label className="flex flex-col gap-1 text-sm font-medium text-stone-700">
              Column
              <select
                value={cardDraft.column_id}
                onChange={(event) =>
                  setCardDraft((prev) => ({ ...prev, column_id: Number(event.target.value) }))
                }
                className="rounded-lg border border-[#cbb98e] bg-[#fffaf2] px-3 py-2 text-sm focus:border-[#b2925a] focus:outline-none focus:ring-2 focus:ring-[rgba(178,146,90,0.30)]"
              >
                {columnOptions.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.title}
                  </option>
                ))}
              </select>
            </label>
            {cardError && <p style={{ color: "crimson" }}>{cardError}</p>}
            <RoundedButton type="submit" disabled={isCardSaving} className="btn-primary">
              {isCardSaving ? "Saving…" : editingCard.mode === "create" ? "Create" : "Save"}
            </RoundedButton>
          </form>
        )}
      </Modal>

    </div>
  );
}
