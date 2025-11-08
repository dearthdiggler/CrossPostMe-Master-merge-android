import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Badge } from "./ui/badge";
import {
  CheckCircle2,
  XCircle,
  Loader2,
  ExternalLink,
  AlertCircle,
  Zap,
  Link as LinkIcon,
} from "lucide-react";
import { api } from "../lib/api";

const PlatformConnections = () => {
  const [platforms, setPlatforms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(null);
  const [showCredentialDialog, setShowCredentialDialog] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [credentials, setCredentials] = useState({
    username: "",
    password: "",
  });
  const [error, setError] = useState(null);

  const platformInfo = [
    {
      id: "facebook",
      name: "Facebook Marketplace",
      icon: "📘",
      method: "oauth",
      description: "Connect via OAuth for secure access",
      color: "bg-blue-100 text-blue-800",
      features: ["Auto-posting", "Message management", "Analytics"],
    },
    {
      id: "ebay",
      name: "eBay",
      icon: "🛒",
      method: "oauth",
      description: "Connect via OAuth for secure access",
      color: "bg-yellow-100 text-yellow-800",
      features: ["Auction listings", "Buy It Now", "Inventory sync"],
    },
    {
      id: "offerup",
      name: "OfferUp",
      icon: "📱",
      method: "credentials",
      description: "Secure credential storage",
      color: "bg-green-100 text-green-800",
      features: ["Local listings", "Auto-posting", "Message tracking"],
    },
    {
      id: "craigslist",
      name: "Craigslist",
      icon: "📝",
      method: "credentials",
      description: "Secure credential storage",
      color: "bg-purple-100 text-purple-800",
      features: ["Multi-city posting", "Auto-renew", "Bulk actions"],
    },
  ];

  useEffect(() => {
    fetchPlatforms();
  }, []);

  const fetchPlatforms = async () => {
    try {
      setLoading(true);
      const data = await api.get("/api/platform-oauth/status");
      setPlatforms(data.platforms || []);
    } catch (err) {
      console.error("Error fetching platforms:", err);
      setError("Failed to load platform status");
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (platform) => {
    setError(null);
    setConnecting(platform.id);

    try {
      if (platform.method === "oauth") {
        // OAuth flow
        const response = await api.post("/api/platform-oauth/init", {
          platform: platform.id,
          redirect_uri: `${window.location.origin}/oauth/callback`,
        });

        if (response.auth_url) {
          // Redirect to OAuth provider
          window.location.href = response.auth_url;
        }
      } else {
        // Credential-based
        setSelectedPlatform(platform);
        setShowCredentialDialog(true);
        setConnecting(null);
      }
    } catch (err) {
      console.error("Error connecting platform:", err);
      setError(err.message || `Failed to connect to ${platform.name}`);
      setConnecting(null);
    }
  };

  const handleCredentialSubmit = async () => {
    if (!credentials.username || !credentials.password) {
      setError("Please enter both username and password");
      return;
    }

    try {
      setConnecting(selectedPlatform.id);

      await api.post("/api/platform-oauth/credentials", {
        platform: selectedPlatform.id,
        credentials: {
          username: credentials.username,
          password: credentials.password,
        },
      });

      setShowCredentialDialog(false);
      setCredentials({ username: "", password: "" });
      setSelectedPlatform(null);

      // Refresh platform status
      await fetchPlatforms();

    } catch (err) {
      console.error("Error saving credentials:", err);
      setError(err.message || "Failed to save credentials");
    } finally {
      setConnecting(null);
    }
  };

  const handleDisconnect = async (platformId) => {
    if (!confirm("Are you sure you want to disconnect this platform?")) {
      return;
    }

    try {
      setConnecting(platformId);
      await api.delete(`/api/platform-oauth/${platformId}`);
      await fetchPlatforms();
    } catch (err) {
      console.error("Error disconnecting platform:", err);
      setError(err.message || "Failed to disconnect platform");
    } finally {
      setConnecting(null);
    }
  };

  const isPlatformConnected = (platformId) => {
    return platforms.some((p) => p.platform === platformId && p.connected);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight mb-2">
          Platform Connections
        </h2>
        <p className="text-gray-600">
          Connect your marketplace accounts to start cross-posting
        </p>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <span className="font-medium">{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Platform Cards */}
      <div className="grid gap-6 md:grid-cols-2">
        {platformInfo.map((platform) => {
          const isConnected = isPlatformConnected(platform.id);
          const isConnectingThis = connecting === platform.id;

          return (
            <Card key={platform.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-4xl">{platform.icon}</span>
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {platform.name}
                        {isConnected && (
                          <CheckCircle2 className="h-5 w-5 text-green-600" />
                        )}
                      </CardTitle>
                      <CardDescription className="mt-1">
                        {platform.description}
                      </CardDescription>
                    </div>
                  </div>
                  <Badge className={platform.color}>
                    {platform.method === "oauth" ? "OAuth" : "Credentials"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Features */}
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Features:
                  </p>
                  <ul className="space-y-1">
                    {platform.features.map((feature, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-sm text-gray-600">
                        <Zap className="h-3 w-3 text-blue-600" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Status */}
                <div className="pt-4 border-t">
                  {isConnected ? (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-green-600">
                        <CheckCircle2 className="h-5 w-5" />
                        <span className="font-medium">Connected</span>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDisconnect(platform.id)}
                        disabled={isConnectingThis}
                        className="text-red-600 hover:text-red-700"
                      >
                        {isConnectingThis ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Disconnecting...
                          </>
                        ) : (
                          <>
                            <XCircle className="mr-2 h-4 w-4" />
                            Disconnect
                          </>
                        )}
                      </Button>
                    </div>
                  ) : (
                    <Button
                      className="w-full bg-blue-600 hover:bg-blue-700"
                      onClick={() => handleConnect(platform)}
                      disabled={isConnectingThis}
                    >
                      {isConnectingThis ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Connecting...
                        </>
                      ) : (
                        <>
                          <LinkIcon className="mr-2 h-4 w-4" />
                          Connect {platform.name}
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Help Card */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="space-y-2">
              <p className="font-medium text-blue-900">
                Need help connecting platforms?
              </p>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• <strong>OAuth platforms</strong> (Facebook, eBay): Click "Connect" to authorize securely</li>
                <li>• <strong>Credential platforms</strong> (OfferUp, Craigslist): Enter your login details securely</li>
                <li>• All credentials are encrypted and stored securely</li>
                <li>• You can disconnect at any time</li>
              </ul>
              <a
                href="/help/platform-connections"
                className="inline-flex items-center text-sm text-blue-600 hover:text-blue-700 font-medium mt-2"
              >
                Learn more
                <ExternalLink className="ml-1 h-4 w-4" />
              </a>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Credential Dialog */}
      <Dialog open={showCredentialDialog} onOpenChange={setShowCredentialDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <span className="text-2xl">{selectedPlatform?.icon}</span>
              Connect {selectedPlatform?.name}
            </DialogTitle>
            <DialogDescription>
              Enter your {selectedPlatform?.name} account credentials. Your information is encrypted and stored securely.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="username">Email or Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="your@email.com"
                value={credentials.username}
                onChange={(e) =>
                  setCredentials((prev) => ({
                    ...prev,
                    username: e.target.value,
                  }))
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={credentials.password}
                onChange={(e) =>
                  setCredentials((prev) => ({
                    ...prev,
                    password: e.target.value,
                  }))
                }
              />
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-sm text-yellow-800">
                <strong>Security Note:</strong> Your credentials are encrypted using industry-standard encryption before storage. We never store passwords in plain text.
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowCredentialDialog(false);
                setCredentials({ username: "", password: "" });
                setSelectedPlatform(null);
              }}
              disabled={connecting}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCredentialSubmit}
              disabled={connecting || !credentials.username || !credentials.password}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {connecting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Connecting...
                </>
              ) : (
                <>
                  <LinkIcon className="mr-2 h-4 w-4" />
                  Connect Account
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PlatformConnections;
