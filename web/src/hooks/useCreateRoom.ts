import { useState } from "react";
import { createRoom } from "../services/roomService";

type CreatedRoom = { public_id: string; name: string };

export function useCreateRoom() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createdRoom, setCreatedRoom] = useState<CreatedRoom | null>(null);
  async function submit(name: string): Promise<CreatedRoom> {
    setError(null); setIsSubmitting(true);
    try {
      const id = await createRoom(name);
      const room = { public_id: id, name };
      setCreatedRoom(room);
      return room;
    } catch (e: any) {
      setError(e?.message || "Failed to create room");
      throw e;
    } finally {
      setIsSubmitting(false);
    }
  }

  return { submit, isSubmitting, error, setError, createdRoom };
}
