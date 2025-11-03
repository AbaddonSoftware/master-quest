import TextField from "../components/TextField";
import RoundedButton from "../components/RoundedButton";

type Props = {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
  error?: string | null;
};

export default function CreateRoomForm({
  value,
  onChange,
  onSubmit,
  isSubmitting,
  error,
}: Props) {
  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-2xl font-bold text-stone-900">Create a room</h1>
        <p className="mt-1 text-sm text-stone-600">
          Pick a name for your new masterquest kanban board. You can always rename it later. Must be 3 to 32 letters or numbers (optional underscores or dashes allowed in between).
        </p>
      </div>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit();
        }}
        className="flex flex-col gap-4"
      >
        <TextField
          label="Room name"
          value={value}
          onChange={onChange}
          required
          minLength={3}
          maxLength={32}
        />
        <RoundedButton type="submit" disabled={isSubmitting} className="btn-primary" size="md">
          {isSubmitting ? "Creating…" : "Create room"}
        </RoundedButton>
      </form>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
