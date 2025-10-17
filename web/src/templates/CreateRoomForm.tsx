import TextField from "../components/TextField";
import Button from "../components/Button";

export default function CreateRoomForm(props: {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
  error?: string | null;
}) {
  const { value, onChange, onSubmit, isSubmitting, error } = props;
  return (
    <div style={{ fontFamily: "system-ui, sans-serif", padding: 24, maxWidth: 480 }}>
      <h1>Create a room</h1>
      <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }}>
        <TextField label="Room name" value={value} onChange={onChange} required minLength={2} maxLength={80} />
        <div style={{ height: 12 }} />
        <Button type="submit" disabled={isSubmitting}>{isSubmitting ? "Creating…" : "Create room"}</Button>
      </form>
      {error && <p style={{ color: "crimson" }}>{error}</p>}
    </div>
  );
}
