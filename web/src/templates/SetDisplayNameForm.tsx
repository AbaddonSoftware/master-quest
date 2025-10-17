import TextField from "../components/TextField";
import Button from "../components/Button";

export default function SetDisplayNameForm(props: {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
  error?: string | null;
}) {
  const { value, onChange, onSubmit, isSubmitting, error } = props;
  return (
    <div style={{ fontFamily: "system-ui, sans-serif", padding: 24, maxWidth: 420 }}>
      <h1>Choose your display name</h1>
      <p>It must be unique.</p>
      <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }}>
        <TextField label="Display name" value={value} onChange={onChange} required minLength={3} maxLength={32} />
        <div style={{ height: 12 }} />
        <Button type="submit" disabled={isSubmitting}>{isSubmitting ? "Saving…" : "Continue"}</Button>
      </form>
      {error && <p style={{ color: "crimson" }}>{error}</p>}
    </div>
  );
}
