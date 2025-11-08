import React from "react";
import { Button } from "./ui/button";
import { Calendar } from "lucide-react";

const CTASection = () => {
  return (
    <section className="py-20 bg-gradient-to-br from-cyan-500 via-blue-500 to-blue-700 relative overflow-hidden">
      {/* Decorative Elements */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-10 right-20 w-96 h-96 bg-white rounded-full blur-3xl"></div>
        <div className="absolute bottom-10 left-20 w-72 h-72 bg-blue-300 rounded-full blur-3xl"></div>
      </div>

      <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-4xl lg:text-6xl font-bold text-white mb-6">
          Simplify Local Listings with CrossPostMe
        </h2>
        <p className="text-xl text-blue-100 mb-12 max-w-3xl mx-auto">
          CrossPostMe automates multi-platform listings and provides tools for
          consistent lead follow-up so small teams can operate efficiently.
        </p>
        <Button
          className="bg-white text-blue-600 hover:bg-gray-100 font-bold px-12 py-8 text-xl rounded-full shadow-2xl hover:scale-105 transition-all duration-300"
          onClick={() => window.open("tel:623-777-9969", "_self")}
        >
          <Calendar className="w-6 h-6 mr-3" />
          Call 623-777-9969 to Schedule
        </Button>
      </div>
    </section>
  );
};

export default CTASection;
