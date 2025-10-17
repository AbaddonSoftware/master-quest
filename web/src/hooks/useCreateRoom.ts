import { useState } from "react";
import { createRoom } from "../services/roomService";

export function useCreateRoom() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function submit(name: string): Promise<string> {
    setError(null); setIsSubmitting(true);
    try {
      return await createRoom(name);
    } catch (e: any) {
      setError(e?.message || "Failed to create room");
      throw e;
    } finally {
      setIsSubmitting(false);
    }
  }

  return { submit, isSubmitting, error, setError };
}
