import { useMemo, useState } from "react";
import { Navigate } from "react-router-dom";
import LandingTemplate from "../templates/LandingTemplate";
import { useAuth } from "../app/providers/AuthProvider";
import Modal from "../components/Modal";
import RoundedButton from "../components/RoundedButton";
import { isEmbeddedBrowser } from "../utils/browser";
import CopyUrlButton from "../components/CopyUrlButton";

export default function HomePage() {
  const { currentUser, isLoading, beginGoogleOAuth } = useAuth();
  const [isLoginModalOpen, setLoginModalOpen] = useState(false);

  const isUnsupportedBrowser = useMemo(() => isEmbeddedBrowser(), []);

  if (currentUser) {
    return <Navigate to="/rooms" replace />;
  }

  const openLoginModal = () => {
    if (isLoading) return;
    setLoginModalOpen(true);
  };
  const closeLoginModal = () => setLoginModalOpen(false);
  const handleGoogleLogin = () => {
    if (isUnsupportedBrowser) return;
    closeLoginModal();
    beginGoogleOAuth();
  };

  return (
    <>
      <LandingTemplate
        onLoginClick={openLoginModal}
        isLoginDisabled={isLoading}
      />

      <Modal open={isLoginModalOpen} onClose={closeLoginModal} title="Sign in">
        {isUnsupportedBrowser && (
          <div className="mb-4 rounded-md bg-amber-100 p-3 text-sm text-red-700">
            Google Sign-In is blocked when opened inside embedded in-app
            browsers (Acrobat, ). Please open this link in your regular browser
            and try again.
            <CopyUrlButton/>
          </div>
        )}
        <p className="mb-4 text-stone-700">
          Choose how you would like to continue. More providers are on the way.
        </p>
        <RoundedButton
          type="button"
          className="btn-login w-full justify-center"
          size="md"
          onClick={handleGoogleLogin}
          disabled={isUnsupportedBrowser}
        >
          Continue with Google
        </RoundedButton>
      </Modal>
    </>
  );
}
