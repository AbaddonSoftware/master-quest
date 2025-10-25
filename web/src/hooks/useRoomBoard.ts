import { useCallback, useEffect, useState } from "react";
import {
  fetchBoardDetail,
  fetchBoardIdsForRoom,
  type BoardDetailResponse,
} from "../services/boardService";
import { fetchRoom, type RoomDto } from "../services/roomService";

type State = {
  isLoading: boolean;
  error: string | null;
  activeBoardId: string | null;

  room: RoomDto | null;
};

type BoardColumns = BoardDetailResponse["columns"];
type BoardInfo = BoardDetailResponse["board"] | null;

export function useRoomBoard(roomId: string | undefined) {
  const [basics, setBasics] = useState<Omit<State, "columns" | "board">>({
    isLoading: true,
    error: null,
    activeBoardId: null,
    room: null,
  });
  const [board, setBoard] = useState<BoardInfo>(null);
  const [columns, setColumns] = useState<BoardColumns>([]);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!roomId) {
      setBasics({ isLoading: false, error: null, activeBoardId: null, room: null });
      setBoard(null);
      setColumns([]);
      return;
    }

    let cancelled = false;
    async function load() {
      setBasics((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
        room: prev.room?.public_id === roomId ? prev.room : null,
      }));
      try {
        const [roomData, boardsInRoom] = await Promise.all([
          fetchRoom(roomId),
          fetchBoardIdsForRoom(roomId),
        ]);
        if (!boardsInRoom.length) {
          if (!cancelled) {
            setBasics({
              isLoading: false,
              error: null,
              activeBoardId: null,
              room: roomData,
            });
            setBoard(null);
            setColumns([]);
          }
          return;
        }

        const boardId = boardsInRoom[0];
        const detail = await fetchBoardDetail(roomId, boardId);
        const sortedColumns = detail.columns
          .slice()
          .sort((a, b) => a.position - b.position)
          .map((column) => ({
            ...column,
            cards: column.cards.slice().sort((a, b) => a.position - b.position),
          }));

        if (!cancelled) {
          setBasics({
            isLoading: false,
            error: null,
            activeBoardId: boardId,
            room: roomData,
          });
          setBoard(detail.board);
          setColumns(sortedColumns);
        }
      } catch (err: any) {
        if (!cancelled) {
          setBasics((prev) => ({
            ...prev,
            isLoading: false,
            error: err?.message || "Failed to load board.",
            activeBoardId: null,
          }));
          setBoard(null);
          setColumns([]);
        }
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [roomId, reloadKey]);

  const reload = useCallback(() => {
    setReloadKey((key) => key + 1);
  }, []);

  return { ...basics, board, columns, reload };
}
