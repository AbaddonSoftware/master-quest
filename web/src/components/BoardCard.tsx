type BoardCardProps = {
  title: string;
  description?: string | null;
  onEdit?: () => void;
  onDoubleClick?: () => void;
  onArchive?: () => void;
};

export default function BoardCard({
  title,
  description,
  onEdit,
  onDoubleClick,
  onArchive,
}: BoardCardProps) {
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
      <h4 className="text-base font-semibold text-stone-800 break-words">{title}</h4>

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
