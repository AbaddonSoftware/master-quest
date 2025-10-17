import { API_BASE_URL, apiRequestJson } from "./http";
import type { User } from "../types/user";

export function beginGoogleOAuth() {
  window.location.href = `${API_BASE_URL}/auth/google/login`;
}

export function getCurrentUser() {
  return apiRequestJson<User>("/me", { method: "GET" });
}

export function setDisplayName(display_name: string) {
  return apiRequestJson("/auth/set-profile", {
    method: "POST",
    body: JSON.stringify({ display_name }),
  });
}

export function signOut() {
  return apiRequestJson("/auth/logout", { method: "POST" });
}

