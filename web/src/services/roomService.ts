import { apiRequestJson } from "./http";

type CreateRoomResp = { public_id: string; name: string };
export type RoomDto = { public_id: string; name: string };
export type RoomSummary = {
  public_id: string;
  name: string;
  boards: { public_id: string; name: string }[];
};

type RoomsResponse = { rooms: RoomSummary[] };

export async function createRoom(name: string): Promise<string> {
  const data = await apiRequestJson<CreateRoomResp>("/api/rooms", {
    method: "POST",
    body: JSON.stringify({ name }),
  });

  const id = data?.public_id;
  if (typeof id !== "string" || !id.trim()) {
    throw new Error("API did not return a valid public_id");
  }
  return id;
}

export function fetchRoom(roomId: string) {
  return apiRequestJson<RoomDto>(`/api/rooms/${roomId}`, { method: "GET" });
}

export function fetchRooms() {
  return apiRequestJson<RoomsResponse>("/api/rooms", { method: "GET" });
}

export function deleteRoom(roomId: string) {
  return apiRequestJson<{ message: string }>(`/api/rooms/${roomId}`, {
    method: "DELETE",
  });
}
