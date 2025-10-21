import { apiRequestJson } from "./http";

export type RoomDto = { public_id: string; name: string };
export type RoomSummary = {
  public_id: string;
  name: string;
  boards: { public_id: string; name: string }[];
};

export type Role = "OWNER" | "ADMIN" | "MEMBER" | "VIEWER";

type CreateRoomResp = { public_id: string; name: string };

type RoomsResponse = { rooms: RoomSummary[] };

export type RoomMember = {
  user_public_id: string;
  display_name: string | null;
  name: string;
  email: string | null;
  role: Role;
};

type MembersResponse = { members: RoomMember[] };

export type RoomInvite = {
  code: string;
  role: Role;
  expires_at: string | null;
  max_uses: number;
  used: number;
  remaining: number;
};

type InvitesResponse = { invites: RoomInvite[] };

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

export function fetchRoomMembers(roomId: string) {
  return apiRequestJson<MembersResponse>(`/api/rooms/${roomId}/members`, {
    method: "GET",
  });
}

export function updateRoomMemberRole(
  roomId: string,
  memberPublicId: string,
  payload: { role: Role; confirmation_name?: string }
) {
  return apiRequestJson<{ member: RoomMember }>(
    `/api/rooms/${roomId}/members/${memberPublicId}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    }
  );
}

export function fetchRoomInvites(roomId: string) {
  return apiRequestJson<InvitesResponse>(`/api/rooms/${roomId}/invites`, {
    method: "GET",
  });
}

export function createRoomInvite(
  roomId: string,
  payload: { role: Role; max_uses?: number; expires_in_hours?: number }
) {
  return apiRequestJson<{ invite: RoomInvite }>(
    `/api/rooms/${roomId}/invites`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}

export function revokeRoomInvite(roomId: string, inviteCode: string) {
  return apiRequestJson<{ message: string; code: string }>(
    `/api/rooms/${roomId}/invites/${inviteCode}`,
    { method: "DELETE" }
  );
}

export function acceptInvite(inviteCode: string) {
  return apiRequestJson<{
    room: { public_id: string; name: string };
    membership: { role: Role };
    invite: { code: string; role: Role };
  }>(`/api/invites/${inviteCode}/accept`, {
    method: "POST",
  });
}
