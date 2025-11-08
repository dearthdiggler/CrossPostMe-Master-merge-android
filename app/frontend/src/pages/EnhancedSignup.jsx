import React, { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Checkbox } from "../components/ui/checkbox";
import { Alert, AlertDescription } from "../components/ui/alert";
import { Loader2, CheckCircle2, TrendingUp, Users, DollarSign } from "lucide-react";
import { api } from "../lib/api";

const EnhancedSignup = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const trial = searchParams.get("trial");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [step, setStep] = useState(1);

  // Form data - collecting valuable business intelligence
  const [formData, setFormData] = useState({
    // Basic info
    email: "",
    password: "",
    fullName: "",
    phone: "",

    // Business intelligence data
    businessName: "",
    businessType: "", // sole proprietor, LLC, corporation, etc.
    industry: "", // electronics, clothing, furniture, etc.

    // Marketplace data
    currentMarketplaces: [], // which marketplaces they currently use
    monthlyListings: "", // how many items per month
    averageItemPrice: "", // typical price range
    monthlyRevenue: "", // current monthly sales

    // Pain points & needs
    biggestChallenge: "", // what's their main problem
    currentTools: [], // what tools they currently use
    teamSize: "", // how many people

    // Goals & expectations
    growthGoal: "", // revenue goal
    listingsGoal: "", // how many listings they want

    // Marketing permissions
    marketingEmails: true,
    dataSharing: true, // anonymized data for market insights
    betaTester: false,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value
    }));
  };

  const handleCheckboxArray = (name, value) => {
    setFormData(prev => ({
      ...prev,
      [name]: prev[name].includes(value)
        ? prev[name].filter(item => item !== value)
        : [...prev[name], value]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Send all data to backend for storage
      const response = await api.post("/api/auth/enhanced-signup", {
        ...formData,
        trialType: trial,
        signupDate: new Date().toISOString(),
        source: "pricing_page",
        // Add UTM parameters if available
        utmSource: searchParams.get("utm_source"),
        utmMedium: searchParams.get("utm_medium"),
        utmCampaign: searchParams.get("utm_campaign"),
      });

      if (response.token) {
        localStorage.setItem("access_token", response.token);

        // Track in analytics
        if (window.gtag) {
          window.gtag('event', 'sign_up', {
            method: 'enhanced_trial',
            trial_type: trial,
            business_type: formData.businessType,
            monthly_revenue: formData.monthlyRevenue,
          });
        }

        // Redirect to onboarding/dashboard
        navigate("/onboarding?trial=active");
      }
    } catch (err) {
      console.error("Signup error:", err);
      setError(err.message || "Signup failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const nextStep = () => {
    setStep(step + 1);
  };

  const prevStep = () => {
    setStep(step - 1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-center">
            {trial === "free" ? "Start Your Free Trial" : "Start Your 7-Day Trial"}
          </CardTitle>
          <CardDescription className="text-center text-lg">
            {trial === "free"
              ? "14 days free access to everything - no credit card required"
              : "7 days free, then only pay if you love it"
            }
          </CardDescription>

          {/* Progress indicator */}
          <div className="flex justify-center gap-2 mt-4">
            {[1, 2, 3].map(s => (
              <div
                key={s}
                className={`h-2 w-16 rounded-full ${
                  step >= s ? "bg-blue-600" : "bg-gray-200"
                }`}
              />
            ))}
          </div>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Step 1: Basic Account Info */}
            {step === 1 && (
              <div className="space-y-4">
                <h3 className="text-xl font-semibold flex items-center gap-2">
                  <CheckCircle2 className="text-green-600" />
                  Account Information
                </h3>

                <div className="space-y-2">
                  <Label htmlFor="fullName">Full Name *</Label>
                  <Input
                    id="fullName"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    placeholder="John Smith"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email Address *</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="john@example.com"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number (optional)</Label>
                  <Input
                    id="phone"
                    name="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={handleChange}
                    placeholder="+1 (555) 123-4567"
                  />
                  <p className="text-xs text-gray-500">
                    We'll only use this for important account updates
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password *</Label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="At least 8 characters"
                    required
                    minLength={8}
                  />
                </div>

                <Button type="button" onClick={nextStep} className="w-full" size="lg">
                  Continue
                </Button>
              </div>
            )}

            {/* Step 2: Business Intelligence */}
            {step === 2 && (
              <div className="space-y-4">
                <h3 className="text-xl font-semibold flex items-center gap-2">
                  <TrendingUp className="text-blue-600" />
                  Tell Us About Your Business
                </h3>
                <p className="text-sm text-gray-600">
                  Help us personalize your experience and show you relevant insights
                </p>

                <div className="space-y-2">
                  <Label htmlFor="businessName">Business Name</Label>
                  <Input
                    id="businessName"
                    name="businessName"
                    value={formData.businessName}
                    onChange={handleChange}
                    placeholder="Your Store Name"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="businessType">Business Type</Label>
                  <select
                    id="businessType"
                    name="businessType"
                    value={formData.businessType}
                    onChange={handleChange}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value="">Select...</option>
                    <option value="individual">Individual Seller</option>
                    <option value="sole_proprietor">Sole Proprietor</option>
                    <option value="llc">LLC</option>
                    <option value="corporation">Corporation</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="industry">What do you sell?</Label>
                  <select
                    id="industry"
                    name="industry"
                    value={formData.industry}
                    onChange={handleChange}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value="">Select...</option>
                    <option value="electronics">Electronics</option>
                    <option value="clothing">Clothing & Fashion</option>
                    <option value="furniture">Furniture & Home</option>
                    <option value="collectibles">Collectibles</option>
                    <option value="vehicles">Vehicles & Parts</option>
                    <option value="sports">Sports & Outdoors</option>
                    <option value="toys">Toys & Games</option>
                    <option value="books">Books & Media</option>
                    <option value="handmade">Handmade/Crafts</option>
                    <option value="multiple">Multiple Categories</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label>Which marketplaces do you currently use?</Label>
                  <div className="grid grid-cols-2 gap-2">
                    {["Facebook Marketplace", "eBay", "OfferUp", "Craigslist", "Mercari", "Poshmark", "Etsy", "Amazon"].map(mp => (
                      <div key={mp} className="flex items-center space-x-2">
                        <Checkbox
                          id={mp}
                          checked={formData.currentMarketplaces.includes(mp)}
                          onCheckedChange={() => handleCheckboxArray("currentMarketplaces", mp)}
                        />
                        <label htmlFor={mp} className="text-sm cursor-pointer">
                          {mp}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button type="button" onClick={prevStep} variant="outline" className="flex-1">
                    Back
                  </Button>
                  <Button type="button" onClick={nextStep} className="flex-1">
                    Continue
                  </Button>
                </div>
              </div>
            )}

            {/* Step 3: Revenue & Goals (High-Value Data) */}
            {step === 3 && (
              <div className="space-y-4">
                <h3 className="text-xl font-semibold flex items-center gap-2">
                  <DollarSign className="text-green-600" />
                  Your Goals & Current Performance
                </h3>
                <p className="text-sm text-gray-600">
                  This helps us show you benchmarks and growth opportunities
                </p>

                <div className="space-y-2">
                  <Label htmlFor="monthlyListings">How many items do you list per month?</Label>
                  <select
                    id="monthlyListings"
                    name="monthlyListings"
                    value={formData.monthlyListings}
                    onChange={handleChange}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value="">Select...</option>
                    <option value="1-10">1-10 items</option>
                    <option value="11-50">11-50 items</option>
                    <option value="51-100">51-100 items</option>
                    <option value="101-500">101-500 items</option>
                    <option value="500+">500+ items</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="averageItemPrice">Average item price</Label>
                  <select
                    id="averageItemPrice"
                    name="averageItemPrice"
                    value={formData.averageItemPrice}
                    onChange={handleChange}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value="">Select...</option>
                    <option value="under-25">Under $25</option>
                    <option value="25-100">$25 - $100</option>
                    <option value="100-500">$100 - $500</option>
                    <option value="500-1000">$500 - $1,000</option>
                    <option value="1000+">$1,000+</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="monthlyRevenue">Current monthly revenue</Label>
                  <select
                    id="monthlyRevenue"
                    name="monthlyRevenue"
                    value={formData.monthlyRevenue}
                    onChange={handleChange}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value="">Select... (optional)</option>
                    <option value="under-1k">Under $1,000</option>
                    <option value="1k-5k">$1,000 - $5,000</option>
                    <option value="5k-10k">$5,000 - $10,000</option>
                    <option value="10k-25k">$10,000 - $25,000</option>
                    <option value="25k-50k">$25,000 - $50,000</option>
                    <option value="50k+">$50,000+</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="biggestChallenge">What's your biggest challenge?</Label>
                  <select
                    id="biggestChallenge"
                    name="biggestChallenge"
                    value={formData.biggestChallenge}
                    onChange={handleChange}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value="">Select...</option>
                    <option value="time">Takes too much time</option>
                    <option value="reach">Not enough visibility</option>
                    <option value="pricing">Hard to price items</option>
                    <option value="communication">Managing buyer messages</option>
                    <option value="inventory">Tracking inventory</option>
                    <option value="scaling">Growing my business</option>
                    <option value="multiple-platforms">Managing multiple platforms</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="teamSize">Team size</Label>
                  <select
                    id="teamSize"
                    name="teamSize"
                    value={formData.teamSize}
                    onChange={handleChange}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value="">Select...</option>
                    <option value="1">Just me</option>
                    <option value="2-5">2-5 people</option>
                    <option value="6-10">6-10 people</option>
                    <option value="11-20">11-20 people</option>
                    <option value="20+">20+ people</option>
                  </select>
                </div>

                {/* Data sharing permissions */}
                <div className="border-t pt-4 space-y-3">
                  <div className="flex items-start space-x-2">
                    <Checkbox
                      id="marketingEmails"
                      name="marketingEmails"
                      checked={formData.marketingEmails}
                      onCheckedChange={(checked) =>
                        setFormData(prev => ({ ...prev, marketingEmails: checked }))
                      }
                    />
                    <label htmlFor="marketingEmails" className="text-sm cursor-pointer">
                      Send me tips, market insights, and special offers
                    </label>
                  </div>

                  <div className="flex items-start space-x-2">
                    <Checkbox
                      id="dataSharing"
                      name="dataSharing"
                      checked={formData.dataSharing}
                      onCheckedChange={(checked) =>
                        setFormData(prev => ({ ...prev, dataSharing: checked }))
                      }
                    />
                    <label htmlFor="dataSharing" className="text-sm cursor-pointer">
                      Share anonymized usage data to help improve CrossPostMe and receive industry benchmarks
                    </label>
                  </div>

                  <div className="flex items-start space-x-2">
                    <Checkbox
                      id="betaTester"
                      name="betaTester"
                      checked={formData.betaTester}
                      onCheckedChange={(checked) =>
                        setFormData(prev => ({ ...prev, betaTester: checked }))
                      }
                    />
                    <label htmlFor="betaTester" className="text-sm cursor-pointer">
                      I want early access to new features (beta tester program)
                    </label>
                  </div>
                </div>

                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <div className="flex gap-2">
                  <Button type="button" onClick={prevStep} variant="outline" className="flex-1">
                    Back
                  </Button>
                  <Button type="submit" disabled={loading} className="flex-1 bg-green-600 hover:bg-green-700">
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating Account...
                      </>
                    ) : (
                      "Start Free Trial"
                    )}
                  </Button>
                </div>

                <p className="text-xs text-center text-gray-500">
                  By signing up, you agree to our Terms of Service and Privacy Policy
                </p>
              </div>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default EnhancedSignup;
