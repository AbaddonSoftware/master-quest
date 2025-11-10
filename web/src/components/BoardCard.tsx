type BoardCardProps = {
  title: string;
  description?: string | null;
  onEdit?: () => void;
  onDoubleClick?: () => void;
  onArchive?: () => void;
  onMoveUp?: () => void;
  onMoveDown?: () => void;
  disableReorder?: boolean;
};

export default function BoardCard({
  title,
  description,
  onEdit,
  onDoubleClick,
  onArchive,
  onMoveUp,
  onMoveDown,
  disableReorder = false,
}: BoardCardProps) {
  const showReorder = Boolean(onMoveUp || onMoveDown);
  return (
    <div
      className="rounded-xl border border-[#d8c8a0] bg-white/90 p-3 shadow-sm transition hover:shadow-md"
      onDoubleClick={onDoubleClick}
      role={onDoubleClick ? "button" : undefined}
      tabIndex={onDoubleClick ? 0 : undefined}
      onKeyDown={(event) => {
        if (!onDoubleClick) return;
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onDoubleClick();
        }
      }}
    >
      <div className="mb-2 flex items-start justify-between gap-2">
        <h4 className="text-base font-semibold text-stone-800 break-words flex-1">{title}</h4>
        {showReorder && (
          <div className="flex items-center rounded-full border border-amber-200 bg-white/70 shadow-sm">
            <button
              type="button"
              onClick={(event) => {
                event.stopPropagation();
                onMoveUp?.();
              }}
              disabled={!onMoveUp || disableReorder}
              aria-label="Move card up"
              className="px-2 py-1 text-xs font-semibold text-stone-600 transition hover:text-stone-900 disabled:cursor-not-allowed disabled:text-stone-300"
            >
              ↑
            </button>
            <div className="h-4 w-px bg-amber-200" aria-hidden="true" />
            <button
              type="button"
              onClick={(event) => {
                event.stopPropagation();
                onMoveDown?.();
              }}
              disabled={!onMoveDown || disableReorder}
              aria-label="Move card down"
              className="px-2 py-1 text-xs font-semibold text-stone-600 transition hover:text-stone-900 disabled:cursor-not-allowed disabled:text-stone-300"
            >
              ↓
            </button>
          </div>
        )}
      </div>

      {description && (
        <p className="mt-2 text-sm text-stone-600">{description}</p>
      )}

      {(onEdit || onArchive) && (
        <div className="mt-3 flex items-center justify-end gap-3">
          {onArchive && (
            <button
              type="button"
              onClick={(event) => {
                event.stopPropagation();
                onArchive();
              }}
              className="text-xs font-semibold text-red-600 hover:text-red-800"
            >
              Archive
            </button>
          )}
          {onEdit && (
            <button
              type="button"
              onClick={(event) => {
                event.stopPropagation();
                onEdit();
              }}
              className="text-xs font-semibold text-blue-700 hover:text-blue-900"
            >
              Edit
            </button>
          )}
        </div>
      )}
    </div>
  );
}
