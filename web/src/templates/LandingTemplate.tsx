import RoundedButton from "../components/RoundedButton";

export default function LandingTemplate(props: {
  signedInName?: string;
  onGoogleClick: () => void;
  onLogoutClick?: () => void;
  nextHref?: string;
  nextLabel?: string;
}) {
  const { signedInName, onGoogleClick, onLogoutClick, nextHref, nextLabel } = props;

  return (
    <div>
      <h1 className="text-2xl font-bold">Welcome</h1>

      {signedInName ? (
        <>
          <p>
            Signed in as <b>{signedInName}</b>
          </p>

          {nextHref && nextLabel && (
            <p>
              <RoundedButton
                label={`${nextLabel} →`}
                href={nextHref}
                className="btn-primary"
                size="md"
              />
            </p>
          )}

          {onLogoutClick && (
            <RoundedButton
              label="Logout"
              onClick={onLogoutClick}
              className="btn-sort"
              size="md"
            />
          )}
        </>
      ) : (
        <RoundedButton
          label="Login"
          onClick={onGoogleClick}
          className="btn-login"
          size="md"
        />
      )}
    </div>
  );
}

