import React from "react";
import { testimonials } from "../mock/data";
import { Star, Quote } from "lucide-react";

const Testimonial = () => {
  return (
    <section className="py-20 bg-gradient-to-br from-blue-600 to-blue-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-white mb-4">
            Customer Stories with CrossPostMe
          </h2>
          <p className="text-xl text-blue-100">
            Real results from customers using our tools
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {testimonials.map((testimonial) => (
            <div
              key={testimonial.id}
              className="bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300"
            >
              <Quote className="w-12 h-12 text-blue-200 mb-4" />
              <p className="text-gray-700 text-lg mb-6 leading-relaxed italic">
                "{testimonial.content}"
              </p>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-bold text-gray-900">{testimonial.name}</p>
                  <p className="text-gray-600 text-sm">{testimonial.role}</p>
                </div>
                <div className="flex space-x-1">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star
                      key={i}
                      className="w-5 h-5 fill-yellow-400 text-yellow-400"
                    />
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Case Study Section */}
        <div className="mt-16 bg-white rounded-2xl p-8 md:p-12">
          <div className="flex items-start space-x-4 mb-6">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <TrendingUp className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Case Study: Local Business Results
              </h3>
            </div>
          </div>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start space-x-3">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
              <span>
                A local real estate agent used CrossPostMe to post listings
                across multiple marketplaces.
              </span>
            </li>
            <li className="flex items-start space-x-3">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
              <span>
                <span className="font-semibold">Outcome:</span> The agent
                reported significantly more inquiries and faster responses from
                prospective buyers.
              </span>
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
};

// Import missing icons
import { TrendingUp, CheckCircle } from "lucide-react";

export default Testimonial;
