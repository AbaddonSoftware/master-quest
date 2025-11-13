import { useEffect, useMemo, useState } from "react";
import RoundedButton from "./RoundedButton";
import type { BoardArchiveResponse } from "../services/boardService";

export type ArchiveItemSelection = {
  columns: BoardArchiveResponse["columns"];
  cards: BoardArchiveResponse["cards"];
};

interface ArchivePanelProps {
  archive: BoardArchiveResponse;
  isOpen: boolean;
  isLoading: boolean;
  notice: string | null;
  error: string | null;
  onToggle: () => void;
  onRestore: (selection: ArchiveItemSelection) => Promise<void>;
  onHardDelete: (selection: ArchiveItemSelection) => Promise<void>;
}

export default function ArchivePanel({
  archive,
  isOpen,
  isLoading,
  notice,
  error,
  onToggle,
  onRestore,
  onHardDelete,
}: ArchivePanelProps) {
  const totalArchived = archive.columns.length + archive.cards.length;
  const [selectedColumnIds, setSelectedColumnIds] = useState<Set<number>>(new Set());
  const [selectedCardIds, setSelectedCardIds] = useState<Set<string>>(new Set());
  const [activeAction, setActiveAction] = useState<"restore" | "delete" | null>(null);

  const selectedColumns = useMemo(
    () => archive.columns.filter((column) => selectedColumnIds.has(column.id)),
    [archive.columns, selectedColumnIds]
  );
  const selectedCards = useMemo(
    () => archive.cards.filter((card) => selectedCardIds.has(card.public_id)),
    [archive.cards, selectedCardIds]
  );
  const selectedCount = selectedColumns.length + selectedCards.length;
  const hasSelection = selectedCount > 0;

  useEffect(() => {
    if (!isOpen) {
      clearSelection();
      setActiveAction(null);
    }
  }, [isOpen]);

  function clearSelection() {
    setSelectedColumnIds(new Set());
    setSelectedCardIds(new Set());
  }

  function toggleColumn(id: number) {
    setSelectedColumnIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  function toggleCard(id: string) {
    setSelectedCardIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  async function handleRestoreSelected() {
    if (!hasSelection || activeAction) return;
    setActiveAction("restore");
    try {
      await onRestore({ columns: selectedColumns, cards: selectedCards });
      clearSelection();
    } catch {
      // Parent handles error messaging;
    } finally {
      setActiveAction(null);
    }
  }

  async function handleHardDeleteSelected() {
    if (!hasSelection || activeAction) return;
    const columnsWithCards = selectedColumns.filter((column) =>
      archive.cards.some((card) => card.column_id === column.id)
    );
    let warningMessage = "";
    if (columnsWithCards.length) {
      warningMessage +=
        `WARNING: ${columnsWithCards.length} selected column${
          columnsWithCards.length === 1 ? "" : "s"
        } still ${columnsWithCards.length === 1 ? "has" : "have"} archived cards. ` +
        "Those cards will be moved to the first active column if one exists.\n\n";
    }
    warningMessage +=
      "Type DELETE to permanently remove the selected archived items. This action cannot be undone.";
    const confirmation = window.prompt(warningMessage, "");
    if (confirmation !== "DELETE") {
      return;
    }

    setActiveAction("delete");
    try {
      await onHardDelete({ columns: selectedColumns, cards: selectedCards });
      clearSelection();
    } catch {
      // Parent handles error messaging;
      setActiveAction(null);
    }
  }

  return (
    <div className="fixed bottom-6 right-6 flex flex-col items-end gap-2">
      <RoundedButton size="sm" className="btn-sort" onClick={onToggle}>
        {isOpen ? "Hide archived" : `Archived (${totalArchived})`}
      </RoundedButton>
      {isOpen && (
        <div className="w-96 max-h-[28rem] overflow-y-auto rounded-2xl border border-amber-200 bg-white/95 p-4 shadow-xl">
          <div className="flex flex-col gap-1">
            <h3 className="text-lg font-semibold text-stone-900">Archived items</h3>
            <p className="text-xs text-stone-500">
              {hasSelection ? `${selectedCount} selected` : "Select items to restore or remove"}
            </p>
          </div>
          {notice && <p className="mt-1 text-xs text-green-700">{notice}</p>}
          {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
          <div className="mt-3 flex flex-wrap gap-2">
            <RoundedButton
              size="sm"
              className="btn-login"
              disabled={!hasSelection || activeAction === "delete"}
              onClick={handleRestoreSelected}
            >
              {activeAction === "restore" ? "Restoring…" : "Restore selected"}
            </RoundedButton>
            <RoundedButton
              size="sm"
              className="btn-sort text-red-700 hover:text-red-900"
              disabled={!hasSelection || activeAction === "restore"}
              onClick={handleHardDeleteSelected}
            >
              {activeAction === "delete" ? "Deleting…" : "Hard delete"}
            </RoundedButton>
          </div>
          {isLoading ? (
            <p className="mt-3 text-sm text-stone-600">Loading…</p>
          ) : (
            <div className="mt-3 flex flex-col gap-4 text-sm text-stone-700">
              <div>
                <p className="text-xs uppercase tracking-wide text-stone-500">Columns</p>
                {archive.columns.length ? (
                  <ul className="mt-1 flex flex-col gap-2">
                    {archive.columns.map((column) => (
                      <li key={column.id} className="rounded-xl border border-stone-200 bg-white/80 p-2">
                        <label className="flex items-center gap-2.5">
                          <input
                            type="checkbox"
                            className="h-4 w-4 rounded border-stone-300 text-blue-600 focus:ring-blue-500"
                            checked={selectedColumnIds.has(column.id)}
                            onChange={() => toggleColumn(column.id)}
                          />
                          <div className="flex flex-col">
                            <span className="line-clamp-2 break-words font-medium">{column.title}</span>
                            {column.deleted_at && (
                              <span className="text-xs text-stone-500">
                                Archived {new Date(column.deleted_at).toLocaleString()}
                              </span>
                            )}
                          </div>
                        </label>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-stone-500">No archived columns.</p>
                )}
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-stone-500">Cards</p>
                {archive.cards.length ? (
                  <ul className="mt-1 flex flex-col gap-2">
                    {archive.cards.map((card) => (
                      <li key={card.public_id} className="rounded-xl border border-stone-200 bg-white/80 p-2">
                        <label className="flex items-center gap-2.5">
                          <input
                            type="checkbox"
                            className="h-4 w-4 rounded border-stone-300 text-blue-600 focus:ring-blue-500"
                            checked={selectedCardIds.has(card.public_id)}
                            onChange={() => toggleCard(card.public_id)}
                          />
                          <div className="flex flex-col">
                            <span className="line-clamp-2 break-words font-medium">{card.title}</span>
                            <span className="text-xs text-stone-500">
                              Column #{card.column_id}
                              {card.deleted_at ? ` · Archived ${new Date(card.deleted_at).toLocaleString()}` : ""}
                            </span>
                          </div>
                        </label>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-stone-500">No archived cards.</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
