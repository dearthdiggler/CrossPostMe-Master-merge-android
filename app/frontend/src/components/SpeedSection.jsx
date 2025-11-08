import React from "react";
import { Zap } from "lucide-react";

const SpeedSection = () => {
  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-4xl lg:text-5xl font-bold text-blue-600 mb-4">
            24/7 AI That Posts, Responds, and Books Appointments — So You Don't
            Have To
          </h2>
        </div>

        <div className="bg-gradient-to-r from-gray-900 to-blue-900 rounded-2xl p-12 text-center relative overflow-hidden">
          {/* Lightning Effect */}
          <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-blue-500 to-transparent opacity-30"></div>

          <div className="relative z-10">
            <div className="flex items-center justify-center mb-6">
              <Zap className="w-16 h-16 text-yellow-400" />
            </div>
            <h3 className="text-4xl lg:text-6xl font-bold text-white mb-4">
              SPEED TO LEAD
            </h3>
            <div className="text-3xl lg:text-5xl font-bold text-white mb-4">
              =
            </div>
            <h3 className="text-4xl lg:text-6xl font-bold text-yellow-400">
              SPEED TO CASHFLOW
            </h3>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SpeedSection;
