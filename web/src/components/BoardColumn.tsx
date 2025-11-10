import { useState, useEffect, useRef } from "react";
import BoardCard from "./BoardCard";

type BoardColumnProps = {
  id: number;
  title: string;
  wipLimit?: number | null;
  cards: { id: string; title: string; description?: string | null; columnId: number }[];
  onEditColumn?: (columnId: number, title: string, wipLimit: number | null) => void;
  onEditCard?: (
    cardId: string,
    columnId: number,
    initial: { title: string; description: string | null }
  ) => void;
  onAddCard?: (columnId: number) => void;
  onColumnDoubleClick?: (columnId: number) => void;
  onArchiveColumn?: (columnId: number) => void;
  onArchiveCard?: (cardId: string, columnId: number) => void;
  onMoveLeft?: () => void;
  onMoveRight?: () => void;
  isReordering?: boolean;
  onReorderCard?: (columnId: number, cardId: string, targetIndex: number) => void;
  cardReorderDisabled?: boolean;
};

export default function BoardColumn({
  id,
  title,
  wipLimit,
  cards,
  onEditColumn,
  onEditCard,
  onAddCard,
  onColumnDoubleClick,
  onArchiveColumn,
  onArchiveCard,
  onMoveLeft,
  onMoveRight,
  isReordering = false,
  onReorderCard,
  cardReorderDisabled = false,
}: BoardColumnProps) {
  const [isMenuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!isMenuOpen) return;
    function handleClick(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [isMenuOpen]);

  const showMenu = Boolean(onEditColumn || onArchiveColumn);
  const showReorderButtons = Boolean(onMoveLeft || onMoveRight);
  const showHeaderActions = showMenu || showReorderButtons;
  const reorderDisabled = isReordering;

  return (
    <div className="flex w-full flex-shrink-0 flex-col gap-3 rounded-2xl border border-amber-200 bg-white/70 p-4 shadow-md backdrop-blur sm:w-full md:w-52 lg:w-56 xl:w-60">
      <header className="relative flex items-start justify-between gap-3">
        <div
          onDoubleClick={() => onColumnDoubleClick?.(id)}
          role={onColumnDoubleClick ? "button" : undefined}
          tabIndex={onColumnDoubleClick ? 0 : undefined}
          onKeyDown={(event) => {
            if (!onColumnDoubleClick) return;
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              onColumnDoubleClick(id);
            }
          }}
          className="max-w-[80%]"
        >
          <p className="text-lg font-semibold text-stone-900 break-words">{title}</p>
          {wipLimit != null && (
            <span className="text-xs uppercase tracking-wide text-stone-500">
              WIP limit: {wipLimit}
            </span>
          )}
        </div>
        {showHeaderActions && (
          <div className="flex items-start gap-2">
            {showReorderButtons && (
              <div className="flex items-center rounded-full border border-amber-200 bg-white/90 shadow-sm">
                <button
                  type="button"
                  onClick={() => onMoveLeft?.()}
                  disabled={!onMoveLeft || reorderDisabled}
                  aria-label="Move column left"
                  className="px-2 py-1 text-lg leading-none text-stone-600 transition hover:text-stone-900 disabled:cursor-not-allowed disabled:text-stone-300"
                >
                  ←
                </button>
                <div className="h-5 w-px bg-amber-200" />
                <button
                  type="button"
                  onClick={() => onMoveRight?.()}
                  disabled={!onMoveRight || reorderDisabled}
                  aria-label="Move column right"
                  className="px-2 py-1 text-lg leading-none text-stone-600 transition hover:text-stone-900 disabled:cursor-not-allowed disabled:text-stone-300"
                >
                  →
                </button>
              </div>
            )}
            {showMenu && (
              <div className="relative" ref={menuRef}>
                <button
                  type="button"
                  aria-haspopup="menu"
                  aria-expanded={isMenuOpen}
                  onClick={(event) => {
                    event.stopPropagation();
                    setMenuOpen((prev) => !prev);
                  }}
                  className="flex h-8 w-8 items-center justify-center rounded-full border border-amber-300 bg-amber-50 text-amber-700 transition hover:bg-amber-100"
                  title="Column actions"
                >
                  ⚔️
                </button>
                {isMenuOpen && (
                  <div className="absolute right-0 z-20 mt-2 w-36 rounded-lg border border-amber-200 bg-white/95 p-2 shadow-lg">
                    {onEditColumn && (
                      <button
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation();
                          setMenuOpen(false);
                          onEditColumn(id, title, wipLimit ?? null);
                        }}
                        className="flex w-full items-center gap-2 rounded-md px-2 py-1 text-sm font-medium text-stone-700 hover:bg-amber-50 hover:text-amber-800"
                      >
                        🖋️ Edit Column
                      </button>
                    )}
                    {onArchiveColumn && (
                      <button
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation();
                          setMenuOpen(false);
                          onArchiveColumn(id);
                        }}
                        className="flex w-full items-center gap-2 rounded-md px-2 py-1 text-sm font-medium text-red-600 hover:bg-red-50 hover:text-red-700"
                      >
                        🛡️ Archive Column
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </header>

      <div
        className="flex flex-1 flex-col gap-3 overflow-y-auto pr-1 max-h-[60vh] min-h-0"
        onClick={(event) => {
          if (event.target === event.currentTarget) {
            onAddCard?.(id);
          }
        }}
      >
        {cards.length ? (
          cards.map((card, index) => (
            <BoardCard
              key={card.id}
              title={card.title}
              description={card.description}
              onDoubleClick={
                onEditCard
                  ? () =>
                      onEditCard(card.id, card.columnId, {
                        title: card.title,
                        description: card.description ?? null,
                      })
                  : undefined
              }
              onEdit={
                onEditCard
                  ? () =>
                      onEditCard(card.id, card.columnId, {
                        title: card.title,
                        description: card.description ?? null,
                      })
                  : undefined
              }
              onArchive={
                onArchiveCard
                  ? () => onArchiveCard(card.id, card.columnId)
                  : undefined
              }
              onMoveUp={
                index === 0
                  ? undefined
                  : () => onReorderCard?.(id, card.id, index - 1)
              }
              onMoveDown={
                index === cards.length - 1
                  ? undefined
                  : () => onReorderCard?.(id, card.id, index + 1)
              }
              disableReorder={cardReorderDisabled}
            />
          ))
        ) : (
          <div className="rounded-lg border border-dashed border-stone-300 bg-stone-100/60 p-3 text-center text-sm text-stone-500">
            No cards yet
          </div>
        )}
      </div>
      {onAddCard && (
        <button
          type="button"
          onClick={() => onAddCard(id)}
          className="rounded-lg border border-dashed border-blue-300 bg-blue-50/60 px-3 py-2 text-sm font-semibold text-blue-700 transition hover:border-blue-500 hover:bg-blue-100"
        >
          + Add card
        </button>
      )}
    </div>
  );
}
