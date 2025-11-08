import React, { useEffect, useRef } from "react";
import FocusTrap from "focus-trap-react";

// Common selector for focusable elements. Extracted to improve readability
// and to provide a single source of truth if the selector needs to change.
export const FOCUSABLE_SELECTORS =
  'a[href], area[href], input:not([disabled]):not([type=hidden]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex]:not([tabindex="-1"]), [contenteditable]';

export default function AuthPromptModal({
  open,
  onClose,
  onLogin,
  onRegister,
}) {
  const dialogRef = useRef(null);
  const previouslyFocusedElement = useRef(null);
  // Keep a ref to the latest onClose so we can call it from
  // event handlers without forcing effects to re-run if the
  // parent passes a new function identity.
  const onCloseRef = useRef(onClose);
  const titleId = "auth-prompt-title";
  const descriptionId = `${titleId}-description`;

  // Keep the ref updated whenever the prop changes. This is a tiny
  // effect and intentionally depends on `onClose` so the ref always
  // points to the latest function without causing the larger modal
  // open-effect to tear down and re-run.
  useEffect(() => {
    onCloseRef.current = onClose;
  }, [onClose]);

  // Main effect: only responds to `open` changes. Handlers reference
  // `onCloseRef.current` to call the latest onClose without forcing
  // the effect to re-run when parent provides a new function identity.
  useEffect(() => {
    if (!open) return;

    // Save previously focused element so we can restore focus on close
    previouslyFocusedElement.current = document.activeElement;

    // Move focus into the dialog container
    const el = dialogRef.current;
    if (el && typeof el.focus === "function") {
      el.focus();
    }

    // Close on Escape: still handle Escape ourselves so we can call onCloseRef
    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onCloseRef.current && onCloseRef.current();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      // Restore focus to the element that had focus before the dialog opened
      try {
        const prev = previouslyFocusedElement.current;
        if (prev && typeof prev.focus === "function") prev.focus();
      } catch (err) {
        // Ignore focus restore errors
      }
    };
  }, [open]);

  if (!open) return null;

  const handleBackdropClick = (e) => {
    // Only close when clicking the backdrop (outer div), not when clicking inside
    if (e.target === e.currentTarget) {
      onCloseRef.current && onCloseRef.current();
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={handleBackdropClick}
    >
      <FocusTrap
        focusTrapOptions={{
          fallbackFocus: () => dialogRef.current || document.body,
          clickOutsideDeactivates: true,
          escapeDeactivates: false, // we handle Escape manually to call onCloseRef
        }}
      >
        <div
          ref={dialogRef}
          role="dialog"
          aria-modal="true"
          aria-labelledby={titleId}
          aria-describedby={descriptionId}
          tabIndex={-1}
          className="bg-white p-6 rounded shadow-lg max-w-md w-full"
          onClick={(e) => e.stopPropagation()}
        >
          <h2 id={titleId} className="text-xl font-semibold mb-2">
            Please sign in to continue
          </h2>
          <p id={descriptionId} className="text-sm text-gray-600 mb-4">
            Create an account or log in to access this feature.
          </p>
          <div className="flex space-x-2 justify-end">
            <button
              type="button"
              onClick={() => onCloseRef.current && onCloseRef.current()}
              className="px-4 py-2 border rounded"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={onLogin}
              className="px-4 py-2 bg-blue-600 text-white rounded"
            >
              Log in
            </button>
            <button
              type="button"
              onClick={onRegister}
              className="px-4 py-2 bg-green-600 text-white rounded"
            >
              Register
            </button>
          </div>
        </div>
      </FocusTrap>
    </div>
  );
}
