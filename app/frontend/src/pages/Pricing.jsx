import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";
import {
  Check,
  X,
  Zap,
  Crown,
  Sparkles,
  Loader2,
  CreditCard,
  AlertCircle,
} from "lucide-react";
import { api } from "../lib/api";
import StripePaymentElement from "../components/StripePaymentElement";

const Pricing = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [subscription, setSubscription] = useState(null);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSubscription();
  }, []);

  const fetchSubscription = async () => {
    try {
      const data = await api.get("/api/payments/subscription");
      setSubscription(data);
    } catch (err) {
      console.error("Error fetching subscription:", err);
    }
  };

  const pricingPlans = [
    {
      id: "free",
      name: "Free Trial",
      price: 0,
      priceId: null,
      description: "Try ALL features free for 14 days - No credit card required",
      badge: "START HERE",
      badgeColor: "bg-green-600",
      trial: "14-day free trial",
      features: [
        { text: "Everything in ProSeller", included: true },
        { text: "All 4 platforms", included: true },
        { text: "Unlimited posts", included: true },
        { text: "Advanced analytics", included: true },
        { text: "AI description generator", included: true },
        { text: "Email support", included: true },
        { text: "Full platform access", included: true },
        { text: "No credit card needed", included: true },
      ],
      cta: "Get Started Free",
      popular: false,
    },
    {
      id: "proseller",
      name: "ProSeller",
      price: 24.99,
      priceId: "price_proseller_2499",
      description: "For serious sellers who want unlimited posting",
      badge: "MOST POPULAR",
      badgeColor: "bg-blue-600",
      trial: "7-day free trial",
      features: [
        { text: "Unlimited posts", included: true },
        { text: "All 4 platforms", included: true },
        { text: "Advanced analytics", included: true },
        { text: "AI description generator", included: true },
        { text: "Priority email support", included: true },
        { text: "Bulk CSV import", included: true },
        { text: "Mobile app access", included: true },
        { text: "R.A.D.Ai features", included: false, tooltip: "Available as add-on" },
      ],
      cta: "Start Free Trial",
      popular: true,
    },
    {
      id: "radai",
      name: "ProSeller + R.A.D.Ai",
      price: 30.99,
      priceId: "price_radai_bundle",
      description: "Ultimate automation with AI-powered features",
      badge: "BEST VALUE",
      badgeColor: "bg-purple-600",
      trial: "7-day free trial",
      features: [
        { text: "Everything in ProSeller", included: true },
        { text: "Auto-delisting", included: true },
        { text: "AI Chatbot responses", included: true },
        { text: "Email bot automation", included: true },
        { text: "Market trends notifications", included: true },
        { text: "Dynamic price adjustments", included: true },
        { text: "Smart platform assistance", included: true },
        { text: "24/7 AI support", included: true },
      ],
      cta: "Start Free Trial",
      popular: false,
      highlight: true,
    },
  ];

  const handleSubscribe = async (plan) => {
    // All users go through signup to collect data
    // Free trial users: collect email, name, business info (no payment)
    // Paid plans: collect payment info + all other data

    if (plan.id === "free") {
      // Redirect to enhanced signup that collects business data
      navigate("/signup?trial=free");
      return;
    }

    // For paid plans, show payment dialog after signup
    setSelectedPlan(plan);
    setShowPaymentDialog(true);
  };

  const handlePaymentSuccess = () => {
    setShowPaymentDialog(false);
    navigate("/marketplace/dashboard?payment=success");
  };

  const handlePaymentError = (error) => {
    setError(error.message || "Payment failed. Please try again.");
  };

  const handleManageSubscription = async () => {
    try {
      setLoading(true);
      const response = await api.post("/api/payments/create-portal-session", {
        returnUrl: window.location.href,
      });

      if (response.url) {
        window.location.href = response.url;
      }
    } catch (err) {
      console.error("Error opening customer portal:", err);
      setError("Failed to open subscription management");
    } finally {
      setLoading(false);
    }
  };

  const getCurrentPlan = () => {
    if (!subscription || subscription.status !== "active") return "free";
    if (subscription.radai_enabled) return "radai";
    return "proseller";
  };

  const currentPlan = getCurrentPlan();

  return (
    <div className="flex-1 bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Start with a 7-day free trial. No credit card required.
            Cancel anytime.
          </p>
        </div>

        {error && (
          <Card className="mb-8 border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-red-600">
                <AlertCircle className="h-5 w-5" />
                <span className="font-medium">{error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {pricingPlans.map((plan) => {
            const isCurrentPlan = currentPlan === plan.id;

            return (
              <Card
                key={plan.id}
                className={`relative ${
                  plan.highlight
                    ? "border-2 border-purple-500 shadow-2xl scale-105"
                    : plan.popular
                    ? "border-2 border-blue-500 shadow-xl"
                    : "shadow-lg"
                }`}
              >
                {plan.badge && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <Badge className={`${plan.badgeColor} text-white px-4 py-1`}>
                      {plan.badge}
                    </Badge>
                  </div>
                )}

                <CardHeader className="text-center pb-8 pt-8">
                  <div className="flex justify-center mb-4">
                    {plan.id === "free" && (
                      <Zap className="h-12 w-12 text-gray-400" />
                    )}
                    {plan.id === "proseller" && (
                      <Crown className="h-12 w-12 text-blue-600" />
                    )}
                    {plan.id === "radai" && (
                      <Sparkles className="h-12 w-12 text-purple-600" />
                    )}
                  </div>
                  <CardTitle className="text-2xl mb-2">{plan.name}</CardTitle>
                  <CardDescription className="mb-4">
                    {plan.description}
                  </CardDescription>
                  <div className="text-5xl font-bold text-gray-900">
                    ${plan.price}
                    <span className="text-xl text-gray-600">/mo</span>
                  </div>
                  {plan.trial && (
                    <p className="text-sm text-green-600 font-medium mt-2">
                      {plan.trial}
                    </p>
                  )}
                </CardHeader>

                <CardContent className="space-y-6">
                  <ul className="space-y-3">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        {feature.included ? (
                          <Check className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                        ) : (
                          <X className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
                        )}
                        <span
                          className={
                            feature.included
                              ? "text-gray-700"
                              : "text-gray-400"
                          }
                        >
                          {feature.text}
                        </span>
                      </li>
                    ))}
                  </ul>

                  <Button
                    className={`w-full ${
                      plan.highlight
                        ? "bg-purple-600 hover:bg-purple-700"
                        : plan.popular
                        ? "bg-blue-600 hover:bg-blue-700"
                        : "bg-gray-600 hover:bg-gray-700"
                    }`}
                    onClick={() => handleSubscribe(plan)}
                    disabled={isCurrentPlan || loading}
                  >
                    {isCurrentPlan ? (
                      <>
                        <Check className="mr-2 h-4 w-4" />
                        Current Plan
                      </>
                    ) : (
                      plan.cta
                    )}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Manage Subscription */}
        {subscription && subscription.status === "active" && (
          <div className="text-center">
            <Card className="max-w-2xl mx-auto">
              <CardContent className="pt-6">
                <p className="text-gray-600 mb-4">
                  Want to manage your subscription, update payment method, or
                  view invoices?
                </p>
                <Button
                  variant="outline"
                  onClick={handleManageSubscription}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    <>
                      <CreditCard className="mr-2 h-4 w-4" />
                      Manage Subscription
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {/* FAQ Section */}
        <div className="mt-20">
          <h2 className="text-3xl font-bold text-center mb-12">
            Frequently Asked Questions
          </h2>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div>
              <h3 className="font-semibold text-lg mb-2">
                How does the free trial work?
              </h3>
              <p className="text-gray-600">
                Start your 7-day free trial with full access to ProSeller
                features. No credit card required. After the trial, you can
                continue with 6 free posts per month or upgrade.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">
                Can I cancel anytime?
              </h3>
              <p className="text-gray-600">
                Yes! Cancel anytime from your account settings. You'll retain
                access until the end of your billing period.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">
                What is R.A.D.Ai?
              </h3>
              <p className="text-gray-600">
                Responsive Advertising Delivery AI - our advanced automation
                that handles auto-delisting, chatbot responses, email
                monitoring, and dynamic pricing.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">
                Which platforms are supported?
              </h3>
              <p className="text-gray-600">
                All plans support Facebook Marketplace, eBay, OfferUp, and
                Craigslist with seamless cross-posting.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Payment Dialog with Stripe Payment Element */}
      <Dialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Start Your Free Trial</DialogTitle>
            <DialogDescription>
              Enter your payment details to start your 7-day free trial. You won't be charged until the trial ends.
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <StripePaymentElement
              amount={selectedPlan?.price || 0}
              planName={selectedPlan?.name || ""}
              onSuccess={handlePaymentSuccess}
              onError={handlePaymentError}
              returnUrl={`${window.location.origin}/marketplace/dashboard?payment=success`}
            />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Pricing;
