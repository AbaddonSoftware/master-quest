import TextField from "../components/TextField";
import RoundedButton from "../components/RoundedButton";

export default function SetDisplayNameForm(props: {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
  error?: string | null;
}) {
  const { value, onChange, onSubmit, isSubmitting, error } = props;
  return (
    <div>
      <h1>Choose your display name</h1>
      <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }}>
        <TextField label="Display name" value={value} onChange={onChange} required minLength={3} maxLength={32} />
        <div/>
        <RoundedButton type="submit" disabled={isSubmitting} className="btn-primary" size="md">
          {isSubmitting ? "Saving…" : "Continue"}
        </RoundedButton>
      </form>
      {error && <p style={{ color: "crimson" }}>{error}</p>}
    </div>
  );
}
