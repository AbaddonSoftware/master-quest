import { useCallback, useEffect, useRef, useState } from "react";
import {
  fetchBoardDetail,
  fetchBoardIdsForRoom,
  type BoardDetailResponse,
} from "../services/boardService";
import { fetchRoom, type RoomDto } from "../services/roomService";

type State = {
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  activeBoardId: string | null;

  room: RoomDto | null;
};

type BoardColumns = BoardDetailResponse["columns"];
type BoardInfo = BoardDetailResponse["board"] | null;

const INITIAL_STATE: State = {
  isLoading: true,
  isRefreshing: false,
  error: null,
  activeBoardId: null,
  room: null,
};

export function useRoomBoard(roomId: string | undefined) {
  const [basics, setBasics] = useState<State>(INITIAL_STATE);
  const [board, setBoard] = useState<BoardInfo>(null);
  const [columns, setColumns] = useState<BoardColumns>([]);
  const [reloadKey, setReloadKey] = useState(0);
  const hasLoadedOnce = useRef(false);
  const previousRoomId = useRef<string | undefined>();
  const previousBoardIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (!roomId) {
      hasLoadedOnce.current = false;
      previousRoomId.current = undefined;
      previousBoardIdRef.current = null;
      setBasics({ ...INITIAL_STATE, isLoading: false });
      setBoard(null);
      setColumns([]);
      return;
    }

    const isRoomChange = previousRoomId.current !== roomId;
    if (isRoomChange) {
      hasLoadedOnce.current = false;
    }
    previousRoomId.current = roomId;

    let cancelled = false;
    async function load() {
      setBasics((prev) => ({
        ...prev,
        isLoading: isRoomChange || !hasLoadedOnce.current,
        isRefreshing: !isRoomChange && hasLoadedOnce.current,
        error: null,
        room: isRoomChange ? null : prev.room,
      }));
      try {
        const [roomData, boardsInRoom] = await Promise.all([
          fetchRoom(roomId),
          fetchBoardIdsForRoom(roomId),
        ]);
        if (!boardsInRoom.length) {
          if (!cancelled) {
            hasLoadedOnce.current = true;
            previousBoardIdRef.current = null;
            setBasics({
              isLoading: false,
              isRefreshing: false,
              error: null,
              activeBoardId: null,
              room: roomData,
            });
            setBoard(null);
            setColumns([]);
          }
          return;
        }

        const previousBoardId = previousBoardIdRef.current;
        const boardId = previousBoardId && boardsInRoom.includes(previousBoardId)
          ? previousBoardId
          : boardsInRoom[0];
        const detail = await fetchBoardDetail(roomId, boardId);
        const sortedColumns = detail.columns
          .slice()
          .sort((a, b) => a.position - b.position)
          .map((column) => ({
            ...column,
            cards: column.cards.slice().sort((a, b) => a.position - b.position),
          }));

        if (!cancelled) {
          hasLoadedOnce.current = true;
          setBasics({
            isLoading: false,
            isRefreshing: false,
            error: null,
            activeBoardId: boardId,
            room: roomData,
          });
          previousBoardIdRef.current = detail.board?.public_id ?? null;
          setBoard(detail.board);
          setColumns(sortedColumns);
        }
      } catch (error: unknown) {
        if (!cancelled) {
          const message =
            error instanceof Error && error.message ? error.message : "Failed to load board.";
          setBasics((prev) => ({
            ...prev,
            isLoading: false,
            isRefreshing: false,
            error: message,
            activeBoardId: prev.activeBoardId,
          }));
          if (!hasLoadedOnce.current) {
            previousBoardIdRef.current = null;
            setBoard(null);
            setColumns([]);
          }
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
