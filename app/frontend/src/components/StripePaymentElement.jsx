import React, { useState, useEffect } from "react";
import { loadStripe } from "@stripe/stripe-js";
import {
  Elements,
  PaymentElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";
import { Button } from "./ui/button";
import { Alert, AlertDescription } from "./ui/alert";
import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";

// Initialize Stripe with your publishable key
const stripePromise = loadStripe(
  import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || ""
);

/**
 * Payment Form Component (inside Elements provider)
 */
const PaymentForm = ({
  amount,
  planName,
  onSuccess,
  onError,
  returnUrl,
}) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const { error: submitError } = await elements.submit();
      if (submitError) {
        throw new Error(submitError.message);
      }

      // Confirm the payment
      const { error: confirmError } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: returnUrl || `${window.location.origin}/success`,
        },
        redirect: "if_required",
      });

      if (confirmError) {
        throw new Error(confirmError.message);
      }

      // Payment successful
      setMessage("Payment successful!");
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      console.error("Payment error:", err);
      setError(err.message || "Payment failed. Please try again.");
      if (onError) {
        onError(err);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Plan Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-100">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="font-semibold text-gray-900">{planName}</h3>
            <p className="text-sm text-gray-600">
              7-day free trial, then ${amount}/month
            </p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-blue-600">
              ${amount}
              <span className="text-sm text-gray-600">/mo</span>
            </p>
            <p className="text-xs text-green-600 font-medium">
              First 7 days FREE
            </p>
          </div>
        </div>
      </div>

      {/* Payment Element */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <PaymentElement
          options={{
            layout: {
              type: "tabs",
              defaultCollapsed: false,
            },
          }}
        />
      </div>

      {/* Error Message */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Success Message */}
      {message && (
        <Alert className="bg-green-50 border-green-200 text-green-800">
          <CheckCircle2 className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      {/* Submit Button */}
      <Button
        type="submit"
        className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-6 text-lg font-semibold"
        disabled={!stripe || loading}
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Processing...
          </>
        ) : (
          <>Start Free Trial</>
        )}
      </Button>

      {/* Fine Print */}
      <div className="text-center space-y-1">
        <p className="text-xs text-gray-500">
          By confirming, you authorize CrossPostMe to charge your payment method
        </p>
        <p className="text-xs text-gray-500">
          Cancel anytime before trial ends to avoid charges
        </p>
      </div>
    </form>
  );
};

/**
 * Main Stripe Payment Element Component
 */
const StripePaymentElement = ({
  clientSecret,
  amount,
  planName,
  onSuccess,
  onError,
  returnUrl,
}) => {
  const [localClientSecret, setLocalClientSecret] = useState(clientSecret);
  const [loading, setLoading] = useState(!clientSecret);

  useEffect(() => {
    if (!clientSecret) {
      // Fetch client secret from backend
      fetchClientSecret();
    }
  }, [clientSecret]);

  const fetchClientSecret = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/payments/create-setup-intent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      const data = await response.json();
      if (data.clientSecret) {
        setLocalClientSecret(data.clientSecret);
      } else {
        throw new Error("Failed to initialize payment");
      }
    } catch (err) {
      console.error("Error fetching client secret:", err);
      if (onError) {
        onError(err);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600 mb-4" />
        <p className="text-gray-600">Initializing secure payment...</p>
      </div>
    );
  }

  if (!localClientSecret) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Failed to initialize payment. Please try again.
        </AlertDescription>
      </Alert>
    );
  }

  const options = {
    clientSecret: localClientSecret,
    appearance: {
      theme: "stripe",
      variables: {
        colorPrimary: "#2563eb",
        colorBackground: "#ffffff",
        colorText: "#1f2937",
        colorDanger: "#ef4444",
        fontFamily: "system-ui, sans-serif",
        spacingUnit: "4px",
        borderRadius: "8px",
      },
      rules: {
        ".Label": {
          fontWeight: "500",
          marginBottom: "8px",
        },
        ".Input": {
          padding: "12px",
          fontSize: "16px",
        },
        ".Tab": {
          padding: "12px 16px",
          borderRadius: "8px",
        },
      },
    },
  };

  return (
    <Elements stripe={stripePromise} options={options}>
      <PaymentForm
        amount={amount}
        planName={planName}
        onSuccess={onSuccess}
        onError={onError}
        returnUrl={returnUrl}
      />
    </Elements>
  );
};

export default StripePaymentElement;
