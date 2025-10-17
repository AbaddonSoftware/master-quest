import { apiRequestJson } from "./http";

type CreateRoomResp = { public_id: string; name: string; };

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
