import React, { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { toast } from "../hooks/use-toast";
import { Rocket } from "lucide-react";

const Hero = () => {
  const [formData, setFormData] = useState({
    companySize: "",
    website: "",
    hearAbout: "",
    goals: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    toast({
      title: "Proposal Request Submitted!",
      description: "We'll get back to you within 24 hours.",
    });
    setFormData({ companySize: "", website: "", hearAbout: "", goals: "" });
  };

  return (
    <section className="relative bg-gradient-to-br from-cyan-400 via-blue-500 to-blue-600 overflow-hidden">
      {/* Decorative Elements */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-20 w-72 h-72 bg-white rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-blue-300 rounded-full blur-3xl"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="text-white space-y-8">
            <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
              Post Once, Sell Everywhere
            </h1>

            <div className="flex items-start space-x-3">
              <Rocket className="w-6 h-6 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-xl font-bold mb-2">
                  Reach More Buyers on OfferUp, Craigslist, Facebook Marketplace
                  & eBay
                </h3>
                <p className="text-blue-100 text-lg">
                  <span className="font-semibold text-white">CrossPostMe</span>{" "}
                  automatically posts your items to multiple marketplaces at
                  once, saving you hours of manual work and maximizing your
                  reach.
                </p>
              </div>
            </div>
          </div>

          {/* Right Form */}
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <div className="text-center mb-6">
              <h2 className="text-3xl font-bold text-blue-600 mb-2">
                START CROSS-POSTING TODAY
              </h2>
              <p className="text-gray-600">Tell us about your selling needs</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Select
                  value={formData.companySize}
                  onValueChange={(value) =>
                    setFormData({ ...formData, companySize: value })
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="How many items do you sell per month?*" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1-10">1-10 items</SelectItem>
                    <SelectItem value="10-50">10-50 items</SelectItem>
                    <SelectItem value="50-100">50-100 items</SelectItem>
                    <SelectItem value="100-200">100-200 items</SelectItem>
                    <SelectItem value="200+">200+ items</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Input
                type="text"
                placeholder="Current online store or shop name? (optional)"
                value={formData.website}
                onChange={(e) =>
                  setFormData({ ...formData, website: e.target.value })
                }
                className="w-full"
              />

              <Input
                type="text"
                placeholder="How did you hear about CrossPostMe?"
                value={formData.hearAbout}
                onChange={(e) =>
                  setFormData({ ...formData, hearAbout: e.target.value })
                }
                className="w-full"
              />

              <Textarea
                placeholder="What do you sell? (e.g., furniture, electronics, collectibles)"
                value={formData.goals}
                onChange={(e) =>
                  setFormData({ ...formData, goals: e.target.value })
                }
                className="w-full min-h-[100px]"
              />

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-6 text-lg"
              >
                Get Started Free
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-600 text-sm mb-2">
                In a hurry? Give us a call now at{" "}
                <a
                  href="tel:623-777-9969"
                  className="text-blue-600 font-semibold hover:underline"
                >
                  623-777-9969
                </a>
              </p>
              <p className="text-gray-500 text-xs">
                By submitting your phone number, you agree to receiving texts
                from CrossPostMe.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
