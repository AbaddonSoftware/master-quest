import { apiRequestJson } from "./http";

export type BoardSummaryResponse = { boards: string[] };

export type CardDto = {
  id: string;
  title: string;
  description: string | null;
  position: number;
  column_id: number;
};

export type BoardColumnDto = {
  id: number;
  title: string;
  position: number;
  wip_limit: number | null;
  column_type: string;
  parent_id: number | null;
  cards: CardDto[];
};

export type BoardDetailResponse = {
  board: {
    public_id: string;
    name: string;
    room_id: string;
  };
  columns: BoardColumnDto[];
};

export type BoardArchiveResponse = {
  columns: { id: number; title: string; deleted_at: string | null }[];
  cards: { public_id: string; title: string; column_id: number; deleted_at: string | null }[];
};

export async function fetchBoardIdsForRoom(roomId: string) {
  const data = await apiRequestJson<BoardSummaryResponse>(
    `/api/rooms/${roomId}/boards`,
    { method: "GET" }
  );
  return data.boards;
}

export async function fetchBoardDetail(roomId: string, boardId: string) {
  return apiRequestJson<BoardDetailResponse>(
    `/api/rooms/${roomId}/boards/${boardId}`,
    { method: "GET" }
  );
}

export function createBoardColumn(roomId: string, boardId: string, payload: { title: string; wip_limit?: number | null }) {
  return apiRequestJson<{ board_id: string; column: BoardColumnDto }>(
    `/api/rooms/${roomId}/boards/${boardId}/columns`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}

export function createCard(roomId: string, boardId: string, columnId: number, payload: { title: string; description?: string }) {
  return apiRequestJson<{ card: CardDto }>(
    `/api/rooms/${roomId}/boards/${boardId}/columns/${columnId}/cards`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}

export function updateBoard(roomId: string, boardId: string, name: string) {
  return apiRequestJson<{ board: { public_id: string; name: string } }>(
    `/api/rooms/${roomId}/boards/${boardId}`,
    {
      method: "PATCH",
      body: JSON.stringify({ name }),
    }
  );
}

export function updateBoardColumn(
  roomId: string,
  boardId: string,
  columnId: number,
  payload: { title?: string; wip_limit?: number | null }
) {
  return apiRequestJson<{ column: { id: number; title: string; wip_limit: number | null; position: number } }>(
    `/api/rooms/${roomId}/boards/${boardId}/columns/${columnId}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    }
  );
}

export function reorderBoardColumns(roomId: string, boardId: string, columnIds: number[]) {
  return apiRequestJson<{ columns: { id: number; position: number }[] }>(
    `/api/rooms/${roomId}/boards/${boardId}/columns/reorder`,
    {
      method: "PATCH",
      body: JSON.stringify({ column_ids: columnIds }),
    }
  );
}

export function reorderColumnCards(
  roomId: string,
  boardId: string,
  columnId: number,
  cardIds: string[]
) {
  return apiRequestJson<{ cards: { id: string; column_id: number; position: number }[] }>(
    `/api/rooms/${roomId}/boards/${boardId}/columns/${columnId}/cards/reorder`,
    {
      method: "PATCH",
      body: JSON.stringify({ card_ids: cardIds }),
    }
  );
}

export function updateCard(
  roomId: string,
  boardId: string,
  currentColumnId: number,
  cardId: string,
  payload: { title?: string; description?: string; column_id?: number }
) {
  return apiRequestJson<{ card: CardDto }>(
    `/api/rooms/${roomId}/boards/${boardId}/columns/${currentColumnId}/cards/${cardId}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    }
  );
}

export function archiveColumn(roomId: string, boardId: string, columnId: number) {
  return apiRequestJson<{ message: string }>(
    `/api/rooms/${roomId}/boards/${boardId}/columns/${columnId}`,
    { method: "DELETE" }
  );
}

export function restoreColumn(roomId: string, boardId: string, columnId: number) {
  return apiRequestJson<{ column: { id: number; title: string; wip_limit: number | null; position: number } }>(
    `/api/rooms/${roomId}/boards/${boardId}/columns/${columnId}/restore`,
    { method: "POST" }
  );
}

export function hardDeleteArchivedColumn(
  roomId: string,
  boardId: string,
  columnId: number,
  options?: { force?: boolean }
) {
  const forceQuery = options?.force ? "?force=true" : "";
  return apiRequestJson<{ message: string }>(
    `/api/rooms/${roomId}/boards/${boardId}/archive/columns/${columnId}${forceQuery}`,
    { method: "DELETE" }
  );
}

export function archiveCard(
  roomId: string,
  boardId: string,
  columnId: number,
  cardId: string
) {
  return apiRequestJson<{ message: string }>(
    `/api/rooms/${roomId}/boards/${boardId}/columns/${columnId}/cards/${cardId}`,
    { method: "DELETE" }
  );
}

export function restoreCard(
  roomId: string,
  boardId: string,
  columnId: number,
  cardId: string
) {
  return apiRequestJson<{ card: CardDto }>(
    `/api/rooms/${roomId}/boards/${boardId}/columns/${columnId}/cards/${cardId}/restore`,
    { method: "POST" }
  );
}

export function hardDeleteArchivedCard(
  roomId: string,
  boardId: string,
  columnId: number,
  cardId: string
) {
  return apiRequestJson<{ message: string }>(
    `/api/rooms/${roomId}/boards/${boardId}/columns/${columnId}/cards/${cardId}/hard`,
    { method: "DELETE" }
  );
}

export function fetchBoardArchive(roomId: string, boardId: string) {
  return apiRequestJson<BoardArchiveResponse>(
    `/api/rooms/${roomId}/boards/${boardId}/archive`,
    { method: "GET" }
  );
}
