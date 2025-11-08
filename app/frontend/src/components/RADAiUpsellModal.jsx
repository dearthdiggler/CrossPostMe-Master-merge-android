import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import {
  Sparkles,
  Zap,
  TrendingUp,
  MessageSquare,
  Mail,
  Bot,
  DollarSign,
  Check,
  X,
  Loader2,
} from "lucide-react";
import { api } from "../lib/api";

const RADAiUpsellModal = ({ isOpen, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const features = [
    {
      icon: <Zap className="h-6 w-6 text-yellow-500" />,
      title: "Auto-Delisting",
      description: "Mark sold → instantly removed from ALL platforms. No more double-sells!",
    },
    {
      icon: <Bot className="h-6 w-6 text-blue-500" />,
      title: "AI Chatbot",
      description: "Auto-respond to buyer questions 24/7 with intelligent, context-aware answers.",
    },
    {
      icon: <Mail className="h-6 w-6 text-green-500" />,
      title: "Email Bot",
      description: "Monitor and respond to platform emails automatically. Never miss a lead!",
    },
    {
      icon: <TrendingUp className="h-6 w-6 text-purple-500" />,
      title: "Market Trends",
      description: "Real-time notifications about pricing trends and optimal posting times.",
    },
    {
      icon: <DollarSign className="h-6 w-6 text-emerald-500" />,
      title: "Dynamic Pricing",
      description: "AI adjusts prices based on market data to maximize sales and revenue.",
    },
    {
      icon: <MessageSquare className="h-6 w-6 text-pink-500" />,
      title: "Smart Assistance",
      description: "AI analyzes your listings and suggests improvements for better results.",
    },
  ];

  const handleStartTrial = async () => {
    try {
      setLoading(true);
      setError(null);

      // Add R.A.D.Ai to subscription
      const response = await api.post("/api/payments/add-radai-trial", {
        trial_days: 3,
      });

      if (response.success) {
        onSuccess?.();
        onClose();
      }
    } catch (err) {
      console.error("Error starting R.A.D.Ai trial:", err);
      setError(err.message || "Failed to start trial");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-center mb-4">
            <div className="relative">
              <Sparkles className="h-16 w-16 text-purple-600 animate-pulse" />
              <div className="absolute -top-2 -right-2">
                <Badge className="bg-gradient-to-r from-purple-600 to-pink-600 text-white">
                  NEW
                </Badge>
              </div>
            </div>
          </div>
          <DialogTitle className="text-3xl text-center">
            Unlock R.A.D.Ai Superpowers! 🚀
          </DialogTitle>
          <DialogDescription className="text-center text-lg">
            <span className="font-semibold text-purple-600">
              Responsive Advertising Delivery AI
            </span>
            <br />
            The ultimate automation suite to 10x your marketplace success
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-6">
          {/* Special Offer Banner */}
          <div className="bg-gradient-to-r from-purple-100 to-pink-100 border-2 border-purple-300 rounded-lg p-6 text-center">
            <p className="text-2xl font-bold text-purple-900 mb-2">
              🎉 Special Launch Offer! 🎉
            </p>
            <p className="text-lg text-purple-800 mb-3">
              Try R.A.D.Ai <span className="font-bold">FREE for 3 days</span>
            </p>
            <div className="flex items-center justify-center gap-4">
              <div className="text-3xl font-bold text-purple-600">
                $7.99<span className="text-sm">/mo</span>
              </div>
              <div className="text-gray-500 line-through text-xl">
                $19.99
              </div>
              <Badge className="bg-red-500 text-white">60% OFF</Badge>
            </div>
            <p className="text-sm text-purple-700 mt-2">
              No commitment during trial • Cancel anytime
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 gap-4">
            {features.map((feature, idx) => (
              <div
                key={idx}
                className="flex gap-4 p-4 border rounded-lg hover:shadow-md transition-shadow bg-white"
              >
                <div className="flex-shrink-0">{feature.icon}</div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">
                    {feature.title}
                  </h4>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Comparison Table */}
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                    Feature
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-900">
                    ProSeller
                  </th>
                  <th className="px-4 py-3 text-center text-sm font-semibold bg-purple-50 text-purple-900">
                    ProSeller + R.A.D.Ai
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                <tr>
                  <td className="px-4 py-3 text-sm">Unlimited Posts</td>
                  <td className="px-4 py-3 text-center">
                    <Check className="h-5 w-5 text-green-600 mx-auto" />
                  </td>
                  <td className="px-4 py-3 text-center bg-purple-50">
                    <Check className="h-5 w-5 text-green-600 mx-auto" />
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-sm">All 4 Platforms</td>
                  <td className="px-4 py-3 text-center">
                    <Check className="h-5 w-5 text-green-600 mx-auto" />
                  </td>
                  <td className="px-4 py-3 text-center bg-purple-50">
                    <Check className="h-5 w-5 text-green-600 mx-auto" />
                  </td>
                </tr>
                <tr>
                  <td className="px-4 py-3 text-sm">Analytics Dashboard</td>
                  <td className="px-4 py-3 text-center">
                    <Check className="h-5 w-5 text-green-600 mx-auto" />
                  </td>
                  <td className="px-4 py-3 text-center bg-purple-50">
                    <Check className="h-5 w-5 text-green-600 mx-auto" />
                  </td>
                </tr>
                <tr className="bg-yellow-50">
                  <td className="px-4 py-3 text-sm font-semibold">
                    Auto-Delisting
                  </td>
                  <td className="px-4 py-3 text-center">
                    <X className="h-5 w-5 text-gray-400 mx-auto" />
                  </td>
                  <td className="px-4 py-3 text-center bg-purple-100">
                    <Check className="h-5 w-5 text-purple-600 mx-auto" />
                  </td>
                </tr>
                <tr className="bg-yellow-50">
                  <td className="px-4 py-3 text-sm font-semibold">AI Chatbot</td>
                  <td className="px-4 py-3 text-center">
                    <X className="h-5 w-5 text-gray-400 mx-auto" />
                  </td>
                  <td className="px-4 py-3 text-center bg-purple-100">
                    <Check className="h-5 w-5 text-purple-600 mx-auto" />
                  </td>
                </tr>
                <tr className="bg-yellow-50">
                  <td className="px-4 py-3 text-sm font-semibold">
                    Dynamic Pricing
                  </td>
                  <td className="px-4 py-3 text-center">
                    <X className="h-5 w-5 text-gray-400 mx-auto" />
                  </td>
                  <td className="px-4 py-3 text-center bg-purple-100">
                    <Check className="h-5 w-5 text-purple-600 mx-auto" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Social Proof */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm font-semibold text-blue-900 mb-2">
              💡 Why R.A.D.Ai Users Sell 3x Faster:
            </p>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>✓ Instant responses = more engaged buyers</li>
              <li>✓ Optimal pricing = faster sales at better margins</li>
              <li>✓ Auto-delisting = zero double-sells or angry customers</li>
              <li>✓ 24/7 automation = sell while you sleep</li>
            </ul>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-3">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={loading}
            className="w-full sm:w-auto"
          >
            Maybe Later
          </Button>
          <Button
            onClick={handleStartTrial}
            disabled={loading}
            className="w-full sm:w-auto bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Starting Trial...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Start 3-Day FREE Trial
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default RADAiUpsellModal;
