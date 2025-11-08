import React from "react";
import { comparisonData } from "../mock/data";
import { Check, X } from "lucide-react";

const Comparison = () => {
  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Side-by-Side Comparison
          </h2>
          <p className="text-xl text-gray-600">
            See why businesses choose CrossPostMe over traditional ads
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gradient-to-r from-blue-600 to-blue-700">
                  <th className="px-6 py-4 text-left text-white font-bold text-lg">
                    Feature
                  </th>
                  <th className="px-6 py-4 text-center text-white font-bold text-lg">
                    CrossPostMe.com (Organic)
                  </th>
                  <th className="px-6 py-4 text-center text-white font-bold text-lg">
                    Traditional Paid Ads
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {comparisonData.map((row, index) => (
                  <tr
                    key={index}
                    className={`hover:bg-blue-50 transition-colors ${
                      index % 2 === 0 ? "bg-gray-50" : "bg-white"
                    }`}
                  >
                    <td className="px-6 py-4 font-semibold text-gray-900">
                      {row.feature}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center space-x-2">
                        <Check className="w-5 h-5 text-green-600" />
                        <span className="font-semibold text-green-700">
                          {row.crossPostMe}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center space-x-2">
                        <X className="w-5 h-5 text-red-600" />
                        <span className="text-gray-600">
                          {row.traditionalAds}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="mt-8 text-center">
          <p className="text-lg text-gray-600">
            Join businesses improving local visibility and lead quality with
            CrossPostMe
          </p>
        </div>
      </div>
    </section>
  );
};

export default Comparison;
