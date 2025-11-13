import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { reportWebVitals, deferExecution } from "./lib/performance";

// Report Web Vitals for performance monitoring (optional, for analytics)
// Uncomment if using Google Analytics or similar
// import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';
// getCLS(reportWebVitals);
// getFID(reportWebVitals);
// getFCP(reportWebVitals);
// getLCP(reportWebVitals);
// getTTFB(reportWebVitals);

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

// Remove splash screen after React renders (use the global function)
// Deferred to avoid blocking main thread
deferExecution(() => {
  if (window.removeSplashScreen) {
    window.removeSplashScreen();
  }
}, 100);

// Defer non-critical initialization
deferExecution(() => {
  // Prefetch commonly visited routes after page load
  if (typeof window !== 'undefined') {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = '/pricing';
    document.head.appendChild(link);
  }
}, 2000);

