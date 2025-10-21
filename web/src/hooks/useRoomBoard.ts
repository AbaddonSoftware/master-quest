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
  board: BoardDetailResponse["board"] | null;
  columns: BoardDetailResponse["columns"];
  room: RoomDto | null;
};

export function useRoomBoard(roomId: string | undefined) {
  const [state, setState] = useState<State>({
    isLoading: true,
    error: null,
    activeBoardId: null,
    board: null,
    columns: [],
    room: null,
  });
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (!roomId) {
      setState({
        isLoading: false,
        error: null,
        activeBoardId: null,
        board: null,
        columns: [],
        room: null,
      });
      return;
    }

    const roomPublicId = roomId;
    let cancelled = false;
    async function load() {
      setState((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
        room: prev.room?.public_id === roomPublicId ? prev.room : null,
      }));
      try {
        const [roomData, boardsInRoom] = await Promise.all([
          fetchRoom(roomPublicId),
          fetchBoardIdsForRoom(roomPublicId),
        ]);
        if (!boardsInRoom.length) {
          if (!cancelled) {
            setState({
              isLoading: false,
              error: null,
              activeBoardId: null,
              board: null,
              columns: [],
              room: roomData,
            });
          }
          return;
        }
        const boardId = boardsInRoom[0];
        const detail = await fetchBoardDetail(roomPublicId, boardId);
        const sortedColumns = detail.columns
          .slice()
          .sort((a, b) => a.position - b.position)
          .map((column) => ({
            ...column,
            cards: column.cards
              .slice()
              .sort((a, b) => a.position - b.position),
          }));
        if (!cancelled) {
          setState({
            isLoading: false,
            error: null,
            activeBoardId: boardId,
            board: detail.board,
            columns: sortedColumns,
            room: roomData,
          });
        }
      } catch (err: any) {
        if (!cancelled) {
          setState((prev) => ({
            ...prev,
            isLoading: false,
            error: err?.message || "Failed to load board.",
            activeBoardId: null,
            board: null,
            columns: [],
          }));
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

  return { ...state, reload };
}
