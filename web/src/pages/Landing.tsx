import { useState } from "react";
import LandingTemplate from "../templates/LandingTemplate";
import { useAuth } from "../app/providers/AuthProvider";
import Modal from "../components/Modal";
import RoundedButton from "../components/RoundedButton";

export default function HomePage() {
  const { currentUser, isLoading, beginGoogleOAuth, signOut } = useAuth();
  const [isLoginModalOpen, setLoginModalOpen] = useState(false);

  if (isLoading) return null;

  const hasName = currentUser?.display_name !== null;

  const openLoginModal = () => setLoginModalOpen(true);
  const closeLoginModal = () => setLoginModalOpen(false);
  const handleGoogleLogin = () => {
    closeLoginModal();
    beginGoogleOAuth();
  };

  return (
    <>
      <LandingTemplate
        signedInName={
          currentUser ? currentUser.display_name || currentUser.email : undefined
        }
        onLoginClick={openLoginModal}
        onLogoutClick={currentUser ? signOut : undefined}
        nextHref={
          currentUser ? (hasName ? "/rooms/new" : "/onboarding") : undefined
        }
        nextLabel={
          currentUser ? (hasName ? "Create a room" : "Finish setup") : undefined
        }
      />

      <Modal open={isLoginModalOpen} onClose={closeLoginModal} title="Sign in">
        <p className="mb-4 text-stone-700">
          Choose how you would like to continue. More providers are on the way.
        </p>
        <RoundedButton
          type="button"
          className="btn-login w-full justify-center"
          size="md"
          onClick={handleGoogleLogin}
        >
          Continue with Google
        </RoundedButton>
      </Modal>
    </>
  );
}
