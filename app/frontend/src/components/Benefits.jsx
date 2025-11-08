import React from "react";
import { benefits } from "../mock/data";
import {
  DollarSign,
  ThumbsUp,
  Award,
  Clock,
  Zap,
  TrendingUp,
} from "lucide-react";

const iconMap = {
  0: DollarSign,
  1: ThumbsUp,
  2: Award,
  3: Clock,
  4: Zap,
  5: TrendingUp,
};

const Benefits = () => {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Here's Why <span className="text-blue-600">Organic Marketing</span>{" "}
            Beats Paid Ads
          </h2>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {benefits.map((benefit, index) => {
            const Icon = iconMap[index];
            return (
              <div
                key={benefit.id}
                className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-8 hover:shadow-xl transition-all duration-300 group"
              >
                <div className="w-16 h-16 bg-white rounded-xl flex items-center justify-center mb-6 shadow-md group-hover:scale-110 transition-transform">
                  <Icon className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  {benefit.title}
                </h3>
                <p className="text-gray-700 leading-relaxed">
                  {benefit.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Benefits;
