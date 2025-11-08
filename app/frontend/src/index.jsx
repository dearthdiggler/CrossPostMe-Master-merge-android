import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App.jsx"; // <-- Corrected file extension
// import * as Sentry from "@sentry/react";
// import "./sentry";

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <React.StrictMode>
    {/* <Sentry.ErrorBoundary fallback={<p>An error occurred</p>} showDialog> */}
      <App />
    {/* </Sentry.ErrorBoundary> */}
  </React.StrictMode>,
);

// Remove splash screen after React renders (use the global function)
setTimeout(() => {
  if (window.removeSplashScreen) {
    window.removeSplashScreen();
  }
}, 100);
