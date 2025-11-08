import { useState, useEffect } from "react";

/**
 * Hook to manage R.A.D.Ai upsell modal timing
 * Shows modal on day 3 of trial if user hasn't seen it yet
 */
export const useRADAiUpsell = () => {
  const [showModal, setShowModal] = useState(false);
  const [hasShown, setHasShown] = useState(false);

  useEffect(() => {
    // Check if we should show the upsell modal
    const checkUpsellTiming = () => {
      try {
        // Get user data from localStorage or API
        const userData = localStorage.getItem("user_data");
        if (!userData) return;

        const user = JSON.parse(userData);

        // Check if user is on trial
        if (!user.subscription || user.subscription.status !== "trialing") {
          return;
        }

        // Check if user already has R.A.D.Ai
        if (user.subscription.radai_enabled) {
          return;
        }

        // Check if user has already seen the modal
        const hasSeenModal = localStorage.getItem("radai_modal_shown");
        if (hasSeenModal === "true") {
          setHasShown(true);
          return;
        }

        // Calculate days since trial started
        const trialStartDate = new Date(user.subscription.trial_start);
        const now = new Date();
        const daysSinceStart = Math.floor(
          (now - trialStartDate) / (1000 * 60 * 60 * 24)
        );

        // Show modal on day 3 or later
        if (daysSinceStart >= 3) {
          setShowModal(true);
          localStorage.setItem("radai_modal_shown", "true");
          setHasShown(true);
        }
      } catch (error) {
        console.error("Error checking R.A.D.Ai upsell timing:", error);
      }
    };

    // Check immediately
    checkUpsellTiming();

    // Check every hour in case user keeps app open
    const interval = setInterval(checkUpsellTiming, 1000 * 60 * 60);

    return () => clearInterval(interval);
  }, []);

  const dismissModal = () => {
    setShowModal(false);
  };

  const handleSuccess = () => {
    setShowModal(false);
    // Refresh user data or trigger re-fetch
    window.location.reload();
  };

  return {
    showModal,
    hasShown,
    dismissModal,
    handleSuccess,
  };
};
