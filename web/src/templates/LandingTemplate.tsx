import RoundedButton from "../components/RoundedButton";

type LandingTemplateProps = {
  signedInName?: string;
  onLoginClick: () => void;
  onLogoutClick?: () => void;
  nextHref?: string;
  nextLabel?: string;
  roomsHref?: string;
};

export default function LandingTemplate({
  signedInName,
  onLoginClick,
  onLogoutClick,
  nextHref,
  nextLabel,
  roomsHref,
}: LandingTemplateProps) {

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

          {roomsHref && (
            <p>
              <RoundedButton
                label="View your rooms"
                href={roomsHref}
                className="btn-login"
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
          onClick={onLoginClick}
          className="btn-login"
          size="md"
        />
      )}
    </div>
  );
}
