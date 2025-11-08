import React, { useState, useContext, createContext, useEffect } from "react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Alert, AlertDescription } from "../components/ui/alert";

// Authentication Context
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Validate authentication on mount using cookies
  useEffect(() => {
    const validateAuth = async () => {
      setIsLoading(true);
      try {
        const response = await fetch("/api/auth/me", {
          method: "GET",
          credentials: "include", // Include cookies in request
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          // No valid authentication
          setUser(null);
        }
      } catch (error) {
        console.error("Auth validation error:", error);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    validateAuth();
  }, []); // Run once on mount

  const login = async (username, password) => {
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // Include cookies in request
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Login failed");
      }

      const data = await response.json();

      // Validate response structure
      if (!data || typeof data !== "object" || !data.user) {
        console.error("Invalid server response:", data);
        return { success: false, error: "Invalid server response" };
      }

      // Cookies are now set by the server, just update user state
      setUser(data.user);

      return { success: true, user: data.user };
    } catch (error) {
      console.error("Login error:", error);
      return { success: false, error: error.message };
    }
  };

  const loginDemo = async () => {
    try {
      const response = await fetch("/api/auth/demo-login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // Include cookies
      });

      if (!response.ok) {
        throw new Error("Demo login failed");
      }

      const data = await response.json();

      // Validate response structure
      if (!data || typeof data !== "object" || !data.user) {
        console.error("Invalid server response:", data);
        return { success: false, error: "Invalid server response" };
      }

      // Cookies are set by server, update user state
      setUser(data.user);

      return { success: true, user: data.user };
    } catch (error) {
      console.error("Demo login error:", error);
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    try {
      // Call logout endpoint to clear cookies
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout error:", error);
    }

    // Clear user state
    setUser(null);
  };

  const value = {
    user,
    login,
    loginDemo,
    logout,
    isAuthenticated: !!user,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

const Login = ({ mode }) => {
  const [isLogin, setIsLogin] = useState(mode !== "register");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const { login, loginDemo } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      if (isLogin) {
        // Login
        const result = await login(username, password);
        if (result.success) {
          setSuccess("Login successful!");
          // Redirect will be handled by parent component
        } else {
          setError(result.error);
        }
      } else {
        // Register
        const response = await fetch("/api/auth/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, email, password }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Registration failed");
        }

        // Auto-login after successful registration
        const loginResult = await login(username, password);
        if (loginResult.success) {
          setSuccess("Registration successful! Logging you in...");
        } else {
          // Registration succeeded but login failed - should not happen normally
          setSuccess("Registration successful! Please log in.");
          setIsLogin(true);
        }
        setUsername("");
        setEmail("");
        setPassword("");
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setLoading(true);
    setError("");

    const result = await loginDemo();
    if (result.success) {
      setSuccess("Demo login successful!");
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {isLogin ? "Sign in to your account" : "Create your account"}
          </h2>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{isLogin ? "Login" : "Register"}</CardTitle>
            <CardDescription>
              {isLogin
                ? "Enter your credentials to access CrossPostMe"
                : "Create a new account to get started"}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {success && (
              <Alert>
                <AlertDescription>{success}</AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label
                  htmlFor="username"
                  className="block text-sm font-medium text-gray-700"
                >
                  Username
                </label>
                <Input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className="mt-1"
                  placeholder="Enter your username"
                />
              </div>

              {!isLogin && (
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Email
                  </label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="mt-1"
                    placeholder="Enter your email"
                  />
                </div>
              )}

              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-gray-700"
                >
                  Password
                </label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="mt-1"
                  placeholder="Enter your password"
                />
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? "Please wait..." : isLogin ? "Sign In" : "Register"}
              </Button>
            </form>

            <div className="text-center">
              <Button
                variant="link"
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError("");
                  setSuccess("");
                }}
                className="text-sm"
              >
                {isLogin
                  ? "Don't have an account? Register"
                  : "Already have an account? Sign in"}
              </Button>
            </div>

            <div className="border-t pt-4">
              <Button
                variant="outline"
                onClick={handleDemoLogin}
                disabled={loading}
                className="w-full"
              >
                {loading ? "Please wait..." : "Try Demo Mode"}
              </Button>
              <p className="text-xs text-gray-500 text-center mt-2">
                Demo mode allows you to explore all features without creating an
                account
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;
