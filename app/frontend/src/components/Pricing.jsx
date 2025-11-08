import React from "react";
import { pricingPlans } from "../mock/data";
import { Button } from "./ui/button";
import { Check } from "lucide-react";

const Pricing = () => {
  return (
    <section id="pricing" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Choose Your Growth Plan
          </h2>
          <p className="text-xl text-gray-600">
            No contracts. Cancel anytime. Results guaranteed.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {pricingPlans.map((plan, index) => (
            <div
              key={plan.id}
              className={`rounded-2xl p-8 transition-all duration-300 hover:scale-105 ${
                plan.popular
                  ? "bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-2xl ring-4 ring-blue-300"
                  : "bg-gray-50 text-gray-900 shadow-lg"
              }`}
            >
              {plan.popular && (
                <div className="bg-yellow-500 text-black text-sm font-bold px-4 py-2 rounded-full inline-block mb-4">
                  MOST POPULAR
                </div>
              )}

              <h3
                className={`text-2xl font-bold mb-2 ${
                  plan.popular ? "text-white" : "text-gray-900"
                }`}
              >
                {plan.name}
              </h3>

              <div className="mb-6">
                {typeof plan.price === "number" ? (
                  <>
                    <span className="text-5xl font-bold">${plan.price}</span>
                    <span
                      className={`text-lg ml-2 ${
                        plan.popular ? "text-blue-200" : "text-gray-600"
                      }`}
                    >
                      /{plan.period}
                    </span>
                  </>
                ) : (
                  <span className="text-5xl font-bold">{plan.price}</span>
                )}
                <p
                  className={`mt-2 text-sm ${
                    plan.popular ? "text-blue-200" : "text-gray-600"
                  }`}
                >
                  {plan.description}
                </p>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-start space-x-3">
                    <Check
                      className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                        plan.popular ? "text-green-300" : "text-green-600"
                      }`}
                    />
                    <span
                      className={`text-sm ${
                        plan.popular ? "text-blue-100" : "text-gray-700"
                      }`}
                    >
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              <Button
                className={`w-full font-semibold py-6 text-lg ${
                  plan.popular
                    ? "bg-white text-blue-600 hover:bg-gray-100"
                    : "bg-blue-600 text-white hover:bg-blue-700"
                }`}
              >
                {typeof plan.price === "number"
                  ? "Get Started"
                  : "Request Pricing"}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Pricing;
