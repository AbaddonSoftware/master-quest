import LandingTemplate from "../templates/LandingTemplate";
import { useAuth } from "../app/providers/AuthProvider";

export default function HomePage() {
  const { currentUser, isLoading, beginGoogleOAuth, signOut } = useAuth();
  if (isLoading) return null;

  const hasName = (currentUser?.display_name !== null)
  return (
    <LandingTemplate
      signedInName={currentUser ? (currentUser.display_name || currentUser.email) : undefined}
      onGoogleClick={beginGoogleOAuth}
      onLogoutClick={currentUser ? signOut : undefined}
      nextHref={currentUser ? (hasName ? "/rooms/new" : "/onboarding") : undefined}
      nextLabel={currentUser ? (hasName ? "Create a room" : "Finish setup") : undefined}
    />
  );
}
