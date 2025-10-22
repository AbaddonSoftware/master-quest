import { useId, useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../app/providers/AuthProvider";
import RoundedButton from "./RoundedButton";
import EyeIcon from "./icons/EyeIcon";
import EyeOffIcon from "./icons/EyeOffIcon";

type AppHeaderProps = {
  extraActions?: ReactNode;
  children?: ReactNode;
};

export default function AppHeader({ extraActions, children }: AppHeaderProps) {
  const navigate = useNavigate();
  const { signOut } = useAuth();
  const panelId = useId();
  const [isExpanded, setExpanded] = useState<boolean>(() => {
    if (typeof window === "undefined") return true;
    return window.matchMedia("(min-width: 768px)").matches;
  });

  const ToggleIcon = isExpanded ? EyeIcon : EyeOffIcon;

  return (
    <header className="sticky top-0 z-20 flex flex-col border-b border-stone-200 bg-[#fffaf2]/95 backdrop-blur">
      <div className="flex h-16 items-center justify-between gap-3 px-4 sm:px-6">
        <button
          type="button"
          onClick={() => navigate("/rooms")}
          className="text-lg font-semibold uppercase tracking-widest text-stone-700 transition hover:text-stone-900"
        >
        <img
        src="/logo/Master-Quest.svg"
        alt="Master Quest Logo"
        className="w-50 h-auto mx-auto"
        />
        </button>
        <div className="flex items-center gap-2">
          <div className="hidden items-center gap-2 md:flex">
            <RoundedButton
              size="sm"
              className="btn-login"
              onClick={() => navigate("/rooms")}
            >
              Rooms
            </RoundedButton>
            {extraActions}
            <RoundedButton
              size="sm"
              className="btn-sort text-red-700 hover:text-red-900"
              onClick={() => {
                void signOut();
              }}
            >
              Logout
            </RoundedButton>
          </div>
          <button
            type="button"
            aria-expanded={isExpanded}
            aria-controls={panelId}
            onClick={() => setExpanded((prev) => !prev)}
            className="inline-flex items-center gap-2 rounded-full border border-stone-300 px-2.5 py-1 text-xs font-semibold uppercase tracking-wide text-stone-600 transition hover:border-stone-400 hover:text-stone-900"
          >
            <ToggleIcon />
          </button>
        </div>
      </div>
      <div
        id={panelId}
        className={`${
          isExpanded ? "flex" : "hidden"
        } flex-col gap-4 border-t border-stone-200 bg-white/80 px-4 py-4 text-sm text-stone-700 md:flex-row md:items-center md:justify-between md:px-6 md:py-3`}
      >
        <div className="flex flex-col gap-2 md:hidden [&>*]:w-full">
          <RoundedButton
            size="sm"
            className="btn-login"
            onClick={() => navigate("/rooms")}
          >
            Rooms
          </RoundedButton>
          {extraActions}
          <RoundedButton
            size="sm"
            className="btn-sort text-red-700 hover:text-red-900"
            onClick={() => {
              void signOut();
            }}
          >
            Logout
          </RoundedButton>
        </div>
        {children ? <div className="md:flex-1">{children}</div> : null}
      </div>
    </header>
  );
}
