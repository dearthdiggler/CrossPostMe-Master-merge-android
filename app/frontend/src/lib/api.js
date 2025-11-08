// Custom error for authentication failures
export class AuthorizationError extends Error {
  constructor(message = "Authentication required") {
    super(message);
    this.name = "AuthorizationError";
  }
}

// Module-level refresh state management
let refreshPromise = null;
let refreshInProgress = false;

// Reset refresh state (for testing or error recovery)
export const resetRefreshState = () => {
  refreshPromise = null;
  refreshInProgress = false;
};

// Perform token refresh with proper locking
const performRefresh = async () => {
  // If refresh is already in progress, wait for it
  if (refreshPromise) {
    return refreshPromise;
  }

  // Create and store the refresh promise
  refreshPromise = (async () => {
    try {
      refreshInProgress = true;

      const refreshResponse = await fetch("/api/auth/refresh", {
        method: "POST",
        credentials: "include",
      });

      if (refreshResponse.ok) {
        return { success: true };
      } else {
        return { success: false, error: "Refresh failed" };
      }
    } catch (error) {
      return { success: false, error: error.message };
    } finally {
      // Reset state after completion
      refreshInProgress = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
};

// API utility functions with cookie-based authentication

/**
 * Get authentication headers (deprecated).
 *
 * @deprecated Cookie-based auth is now used. Callers should rely on automatic cookies with `credentials: 'include'` or use the `apiCall` helper.
 * @returns {object} Empty headers object for backward compatibility
 * @example
 * // Use apiCall helper or fetch with credentials: 'include'
 * fetch('/api/endpoint', { credentials: 'include' })
 */
export const getAuthHeaders = () => {
  // No longer needed with cookie-based auth, but kept for backward compatibility
  return {};
};

export const apiCall = async (url, options = {}, navigate = null) => {
  // Check if this request has already attempted refresh
  const isRefreshAttempted = options._refreshAttempted === true;

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const config = {
    ...options,
    headers,
    credentials: "include", // Include cookies in all requests
  };

  let response;

  try {
    response = await fetch(url, config);
  } catch (error) {
    // Network error
    throw new Error("Network error: " + error.message);
  }

  // Handle unauthorized responses
  if (response.status === 401) {
    // Check if this is a refresh request using precise URL parsing
    let isRefreshRequest = false;
    try {
      // Handle both absolute and relative URLs
      const urlObj = new URL(url, window.location.origin);
      isRefreshRequest = urlObj.pathname === "/api/auth/refresh";
    } catch (e) {
      // Precise fallback: strip query/hash and check exact path
      const cleanUrl = url.split("?")[0].split("#")[0];
      // Match exact path segments to avoid false positives
      isRefreshRequest = /\/api\/auth\/refresh(?:\/|$)/.test(cleanUrl);
    }

    // Check for explicit flag in options
    const isRefreshAttempt = options.isRefreshAttempt === true;

    // Only attempt refresh if:
    // 1. This isn't already a refresh request (by URL or flag)
    // 2. We haven't already attempted refresh for this request
    // 3. No refresh is currently in progress or we can wait for it
    if (!isRefreshRequest && !isRefreshAttempt && !isRefreshAttempted) {
      try {
        const refreshResult = await performRefresh();

        if (refreshResult.success) {
          // Mark this request as having attempted refresh to prevent infinite recursion
          const retryOptions = {
            ...options,
            _refreshAttempted: true,
          };

          // Token refreshed, retry original request ONCE
          return apiCall(url, retryOptions, navigate);
        } else {
          console.error("Token refresh failed:", refreshResult.error);
        }
      } catch (refreshError) {
        console.error("Token refresh error:", refreshError);
      }
    }

    // Refresh failed, not applicable, or already attempted - redirect to login
    if (navigate) {
      navigate("/login");
    } else {
      window.location.href = "/login";
    }

    throw new AuthorizationError("Authentication required");
  }

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Request failed" }));
    throw new Error(
      error.detail || `HTTP ${response.status}: ${response.statusText}`,
    );
  }

  // Handle responses based on status and content type
  if (response.status === 204 || response.status === 205) {
    // No content expected
    return null;
  }

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return response.json();
  } else {
    // For non-JSON responses, return text or null
    const text = await response.text();
    return text || null;
  }
};

// Convenience methods - all include credentials for cookie-based auth
export const api = {
  get: (url, options = {}, navigate = null) =>
    apiCall(url, { method: "GET", ...options }, navigate),
  post: (url, data, options = {}, navigate = null) =>
    apiCall(
      url,
      { method: "POST", body: JSON.stringify(data), ...options },
      navigate,
    ),
  put: (url, data, options = {}, navigate = null) =>
    apiCall(
      url,
      { method: "PUT", body: JSON.stringify(data), ...options },
      navigate,
    ),
  delete: (url, options = {}, navigate = null) =>
    apiCall(url, { method: "DELETE", ...options }, navigate),
  patch: (url, data, options = {}, navigate = null) =>
    apiCall(
      url,
      { method: "PATCH", body: JSON.stringify(data), ...options },
      navigate,
    ),
};
