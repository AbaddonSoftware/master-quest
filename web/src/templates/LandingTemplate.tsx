import RoundedButton from "../components/RoundedButton";

type LandingTemplateProps = {
  onLoginClick: () => void;
};

export default function LandingTemplate({ onLoginClick }: LandingTemplateProps) {
  return (
    <section className="flex flex-col items-center gap-6 text-center">
      <img
      src="/logo/Master-Quest.svg"
      alt="Master Quest Logo"
      className="w-lg h-auto mx-auto"
      />
      <h1 className="text-4xl font-bold text-stone-900">Welcome adventurers...</h1>
      <p className="max-w-xl text-lg text-stone-700">
        Step through the gates and rally your party. Sign in to reach your rooms and
        continue the quest.
      </p>
      <RoundedButton
        label="Login"
        onClick={onLoginClick}
        className="btn-login"
        size="md"
      />
    </section>
  );
}
