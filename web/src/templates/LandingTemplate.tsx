export default function HomeTemplate(props: {
  signedInName?: string;
  onGoogleClick: () => void;
  onLogoutClick?: () => void;
  nextHref?: string;
  nextLabel?: string;
}) {
  const { signedInName, onGoogleClick, onLogoutClick, nextHref, nextLabel } = props;
  return (
    <div>
      <h1>Welcome</h1>
      {signedInName ? (
        <>
          <p>Signed in as <b>{signedInName}</b></p>
          {nextHref && nextLabel && (
            <p><a href={nextHref}>{nextLabel} →</a></p>
          )}
          {onLogoutClick && <button onClick={onLogoutClick}>Log out</button>}
        </>
      ) : (
        <>
          <button onClick={onGoogleClick}>Continue with Google</button>
        </>
      )}
    </div>
  );
}
