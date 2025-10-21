import { useEffect, useMemo, useState, type FormEvent } from "react";
import Modal from "./Modal";
import RoundedButton from "./RoundedButton";
import TextField from "./TextField";
import {
  createRoomInvite,
  fetchRoomInvites,
  fetchRoomMembers,
  revokeRoomInvite,
  updateRoomMemberRole,
  type Role,
  type RoomInvite,
  type RoomMember,
} from "../services/roomService";

type Props = {
  roomId: string;
  open: boolean;
  onClose: () => void;
};

type MemberDraft = {
  selectedRole: Role;
  confirmName: string;
  isSaving: boolean;
  error: string | null;
};

type InviteForm = {
  role: Role;
  maxUses: string;
  expiresInDays: string;
};

const ROLE_PRIORITY: Record<Role, number> = {
  OWNER: 4,
  ADMIN: 3,
  MEMBER: 2,
  VIEWER: 1,
};

const ROLE_LABELS: Record<Role, string> = {
  OWNER: "Owner",
  ADMIN: "Admin",
  MEMBER: "Member",
  VIEWER: "Viewer",
};

const EDITABLE_ROLES: Role[] = ["VIEWER", "MEMBER", "ADMIN"];
const INVITE_ROLES: Role[] = ["VIEWER", "MEMBER"];

function formatDate(value: string | null) {
  if (!value) return "Never";
  try {
    const dt = new Date(value);
    return dt.toLocaleString();
  } catch {
    return value;
  }
}

export default function ManageMembersModal({ roomId, open, onClose }: Props) {
  const [members, setMembers] = useState<RoomMember[]>([]);
  const [memberDrafts, setMemberDrafts] = useState<Record<string, MemberDraft>>({});
  const [invites, setInvites] = useState<RoomInvite[]>([]);
  const [isLoading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [inviteForm, setInviteForm] = useState<InviteForm>({
    role: "MEMBER",
    maxUses: "1",
    expiresInDays: "7",
  });
  const [inviteError, setInviteError] = useState<string | null>(null);
  const [isCreatingInvite, setCreatingInvite] = useState(false);
  const [revokingCode, setRevokingCode] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([fetchRoomMembers(roomId), fetchRoomInvites(roomId)])
      .then(([memberResp, inviteResp]) => {
        if (cancelled) return;
        const fetchedMembers = memberResp.members ?? [];
        setMembers(fetchedMembers);
        const drafts: Record<string, MemberDraft> = {};
        for (const member of fetchedMembers) {
          drafts[member.user_public_id] = {
            selectedRole: member.role,
            confirmName: "",
            isSaving: false,
            error: null,
          };
        }
        setMemberDrafts(drafts);
        setInvites(inviteResp.invites ?? []);
      })
      .catch((err: any) => {
        if (cancelled) return;
        setError(err?.message || "Unable to load members right now.");
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [open, roomId]);

  const ownerId = useMemo(
    () => members.find((member) => member.role === "OWNER")?.user_public_id,
    [members]
  );

  function handleRoleChange(member: RoomMember, role: Role) {
    setMemberDrafts((prev) => {
      const existing = prev[member.user_public_id] ?? {
        selectedRole: member.role,
        confirmName: "",
        isSaving: false,
        error: null,
      };
      const requiresConfirm = ROLE_PRIORITY[role] > ROLE_PRIORITY[member.role];
      return {
        ...prev,
        [member.user_public_id]: {
          ...existing,
          selectedRole: role,
          error: null,
          confirmName: requiresConfirm ? existing.confirmName : "",
        },
      };
    });
  }

  async function handleSaveMember(member: RoomMember) {
    const draft = memberDrafts[member.user_public_id];
    if (!draft) return;
    if (draft.selectedRole === member.role) {
      return;
    }
    const isPromotion =
      ROLE_PRIORITY[draft.selectedRole] > ROLE_PRIORITY[member.role];
    if (isPromotion && !draft.confirmName.trim()) {
      setMemberDrafts((prev) => ({
        ...prev,
        [member.user_public_id]: {
          ...draft,
          error: `Type ${member.display_name || member.name} to confirm promotion.`,
        },
      }));
      return;
    }
    setMemberDrafts((prev) => ({
      ...prev,
      [member.user_public_id]: {
        ...draft,
        isSaving: true,
        error: null,
      },
    }));

    try {
      const payload: { role: Role; confirmation_name?: string } = {
        role: draft.selectedRole,
      };
      if (isPromotion) {
        payload.confirmation_name = draft.confirmName.trim();
      }
      const resp = await updateRoomMemberRole(
        roomId,
        member.user_public_id,
        payload
      );
      const updated = resp.member;
      setMembers((prev) =>
        prev.map((m) =>
          m.user_public_id === member.user_public_id ? updated : m
        )
      );
      setMemberDrafts((prev) => ({
        ...prev,
        [member.user_public_id]: {
          selectedRole: updated.role,
          confirmName: "",
          isSaving: false,
          error: null,
        },
      }));
    } catch (err: any) {
      setMemberDrafts((prev) => ({
        ...prev,
        [member.user_public_id]: {
          ...draft,
          isSaving: false,
          error: err?.message || "Could not update role.",
        },
      }));
    }
  }

  function renderMember(member: RoomMember) {
    const draft = memberDrafts[member.user_public_id];
    const selectedRole = draft?.selectedRole ?? member.role;
    const requiresConfirm =
      ROLE_PRIORITY[selectedRole] > ROLE_PRIORITY[member.role];
    const isOwner = member.role === "OWNER" || member.user_public_id === ownerId;
    const disableChanges = isOwner;
    return (
      <li
        key={member.user_public_id}
        className="rounded-xl border border-stone-200 bg-white/80 p-4 shadow-sm"
      >
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold text-stone-900">
              {member.display_name || member.name}
            </p>
            <p className="text-xs uppercase tracking-wide text-stone-500">
              {ROLE_LABELS[member.role]}
            </p>
            {member.email && (
              <p className="text-xs text-stone-500">{member.email}</p>
            )}
          </div>
          <div className="flex flex-col gap-2 sm:items-end">
            <label className="text-xs font-semibold uppercase text-stone-500">
              Role
              <select
                className="mt-1 rounded-lg border border-stone-300 px-2 py-1 text-sm"
                value={selectedRole}
                disabled={disableChanges}
                onChange={(event) =>
                  handleRoleChange(member, event.currentTarget.value as Role)
                }
              >
                {EDITABLE_ROLES.map((roleOption) => (
                  <option key={roleOption} value={roleOption}>
                    {ROLE_LABELS[roleOption]}
                  </option>
                ))}
              </select>
            </label>
            {requiresConfirm && (
              <TextField
                label={`Type ${member.display_name || member.name} to confirm`}
                value={draft?.confirmName ?? ""}
                onChange={(value) =>
                  setMemberDrafts((prev) => ({
                    ...prev,
                    [member.user_public_id]: {
                      ...(prev[member.user_public_id] ?? {
                        selectedRole,
                        confirmName: "",
                        isSaving: false,
                        error: null,
                      }),
                      confirmName: value,
                    },
                  }))
                }
              />
            )}
            {draft?.error && (
              <p className="text-xs text-red-600">{draft.error}</p>
            )}
            <RoundedButton
              size="sm"
              className="btn-sort"
              disabled={
                disableChanges || draft?.isSaving || selectedRole === member.role
              }
              onClick={() => handleSaveMember(member)}
            >
              {draft?.isSaving ? "Saving…" : "Save role"}
            </RoundedButton>
          </div>
        </div>
      </li>
    );
  }

  async function handleCreateInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setInviteError(null);
    setCreatingInvite(true);
    try {
      const payload: { role: Role; max_uses?: number; expires_in_hours?: number } = {
        role: inviteForm.role,
      };
      const parsedMax = Number(inviteForm.maxUses);
      if (!Number.isNaN(parsedMax) && parsedMax > 0) {
        payload.max_uses = parsedMax;
      }
      const parsedDays = Number(inviteForm.expiresInDays);
      if (!Number.isNaN(parsedDays) && parsedDays > 0) {
        payload.expires_in_hours = parsedDays * 24;
      }
      const resp = await createRoomInvite(roomId, payload);
      setInvites((prev) => [resp.invite, ...prev]);
      setInviteForm({ role: inviteForm.role, maxUses: "1", expiresInDays: "7" });
    } catch (err: any) {
      setInviteError(err?.message || "Could not create invite.");
    } finally {
      setCreatingInvite(false);
    }
  }

  async function handleRevokeInvite(code: string) {
    setRevokingCode(code);
    try {
      await revokeRoomInvite(roomId, code);
      setInvites((prev) => prev.filter((invite) => invite.code !== code));
    } catch (err: any) {
      setInviteError(err?.message || "Could not revoke invite.");
    } finally {
      setRevokingCode(null);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Manage members">
      {isLoading ? (
        <p className="text-sm text-stone-600">Loading members…</p>
      ) : error ? (
        <p className="text-sm text-red-600">{error}</p>
      ) : (
        <div className="flex max-h-[70vh] flex-col gap-5 overflow-y-auto pr-1">
          <section className="flex flex-col gap-3">
            <h3 className="text-lg font-semibold text-stone-900">Members</h3>
            <p className="text-sm text-stone-600">
              Promote carefully — you&rsquo;ll need to type their name when giving someone more power.
            </p>
            {members.length ? (
              <ul className="flex flex-col gap-3">{members.map(renderMember)}</ul>
            ) : (
              <p className="text-sm text-stone-500">No other members yet.</p>
            )}
          </section>

          <section className="flex flex-col gap-3">
            <h3 className="text-lg font-semibold text-stone-900">Invites</h3>
            <form onSubmit={handleCreateInvite} className="flex flex-col gap-3 rounded-xl border border-amber-200 bg-amber-50/70 p-4">
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold uppercase text-stone-500">
                  Role for invitees
                  <select
                    className="mt-1 rounded-lg border border-stone-300 px-2 py-1 text-sm"
                    value={inviteForm.role}
                    onChange={(event) =>
                      setInviteForm((prev) => ({
                        ...prev,
                        role: event.currentTarget.value as Role,
                      }))
                    }
                  >
                    {INVITE_ROLES.map((role) => (
                      <option key={role} value={role}>
                        {ROLE_LABELS[role]}
                      </option>
                    ))}
                  </select>
                </label>
                <TextField
                  label="Max uses"
                  type="number"
                  min={1}
                  value={inviteForm.maxUses}
                  onChange={(value) =>
                    setInviteForm((prev) => ({ ...prev, maxUses: value }))
                  }
                />
                <TextField
                  label="Expires in (days)"
                  type="number"
                  min={1}
                  value={inviteForm.expiresInDays}
                  onChange={(value) =>
                    setInviteForm((prev) => ({ ...prev, expiresInDays: value }))
                  }
                />
              </div>
              {inviteError && (
                <p className="text-xs text-red-600">{inviteError}</p>
              )}
              <RoundedButton
                type="submit"
                className="btn-primary"
                disabled={isCreatingInvite}
              >
                {isCreatingInvite ? "Creating…" : "Create invite"}
              </RoundedButton>
            </form>

            {invites.length ? (
              <ul className="flex flex-col gap-3">
                {invites.map((invite) => (
                  <li
                    key={invite.code}
                    className="flex flex-col gap-2 rounded-xl border border-stone-200 bg-white/80 p-4 shadow-sm"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-stone-900">
                          {ROLE_LABELS[invite.role]} invite
                        </p>
                        <p className="text-xs text-stone-500">
                          Code: <code className="text-[11px]">{invite.code}</code>
                        </p>
                      </div>
                      <RoundedButton
                        size="sm"
                        className="btn-sort text-red-600 hover:text-red-800"
                        disabled={revokingCode === invite.code}
                        onClick={() => handleRevokeInvite(invite.code)}
                      >
                        {revokingCode === invite.code ? "Revoking…" : "Revoke"}
                      </RoundedButton>
                    </div>
                    <div className="flex flex-wrap gap-4 text-xs text-stone-600">
                      <span>Uses: {invite.used} / {invite.max_uses}</span>
                      <span>Expires: {formatDate(invite.expires_at)}</span>
                      <span>Remaining: {invite.remaining}</span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-stone-500">No active invites.</p>
            )}
          </section>
        </div>
      )}
    </Modal>
  );
}
