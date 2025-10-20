import TextField from "../components/TextField";
import RoundedButton from "../components/RoundedButton";

export default function CreateRoomForm(props: {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
  error?: string | null;
}) {
  const { value, onChange, onSubmit, isSubmitting, error } = props;
  return (
    <div>
      <h1>Create a room</h1>
      <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }}>
        <TextField label="Room name" value={value} onChange={onChange} required minLength={2} maxLength={80} />
        <div/>
        <RoundedButton type="submit" disabled={isSubmitting} className="btn-primary" size="md">
          {isSubmitting ? "Creating…" : "Create room"}
        </RoundedButton>
      </form>
      {error && <p style={{ color: "crimson" }}>{error}</p>}
    </div>
  );
}
