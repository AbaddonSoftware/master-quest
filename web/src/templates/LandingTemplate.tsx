import RoundedButton from "../components/RoundedButton";

type LandingTemplateProps = {
  onLoginClick: () => void;
  showAuthSpinner?: boolean;
};

export default function LandingTemplate({
  onLoginClick,
  showAuthSpinner = false,
}: LandingTemplateProps) {
  const loginLabel = "Login";

  return (
    <section className="flex flex-col items-center gap-6 text-center">
      <img
      src="/logo/MasterQuest.svg"
      alt="Master Quest Logo"
      className="w-lg h-auto mx-auto"
      />
      <h1 className="text-4xl font-bold text-stone-900">Welcome Adventurers...</h1>
      <p className="max-w-xl text-lg text-stone-700">
        Step through the gates and rally your party. Sign in to reach your rooms and
        continue the quest.
      </p>
      <RoundedButton
        onClick={onLoginClick}
        className="btn-login w-40"
        size="md"
      >
        {loginLabel}
      </RoundedButton>
      {showAuthSpinner && (
        <p className="text-sm text-stone-500">
          Checking for an existing session… you can still continue.
        </p>
      )}
    </section>
  );
}
