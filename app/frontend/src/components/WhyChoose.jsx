import React from "react";
import {
  TrendingUp,
  Zap,
  Clock,
  MapPin,
  BarChart3,
  DollarSign,
  Globe,
  Shield,
} from "lucide-react";

const WhyChoose = () => {
  const features = [
    {
      icon: TrendingUp,
      title: "Improve return on ad spend",
      description:
        "CrossPostMe helps optimize listings and outreach to reduce wasted spend and improve campaign efficiency.",
    },
    {
      icon: Zap,
      title: "Effortless Automated Ad Posting",
      description:
        "Ensure your ads reach the right audience across major platforms like Google, Facebook Marketplace, Craigslist, and Offerup without being flagged.",
    },
    {
      icon: Clock,
      title: "24/7 Lead Response System",
      description:
        "Never miss a lead with our round-the-clock responder system. Engage customers, collect data, and provide personalized responses anytime.",
    },
    {
      icon: MapPin,
      title: "Dominant Google Maps SEO",
      description:
        "Improve your search engine rankings on Google Maps with our tailored SEO strategies. Drive more organic traffic and dominate local searches.",
    },
    {
      icon: Globe,
      title: "Comprehensive marketing support",
      description:
        "CrossPostMe integrates with common marketing tools and provides services to help list, promote, and follow up with leads.",
    },
    {
      icon: BarChart3,
      title: "In-Depth Data Analytics",
      description:
        "Gain real-time insights into your ad performance with our detailed analytics and reports. Make informed decisions to continually optimize your strategy.",
    },
    {
      icon: DollarSign,
      title: "Lower Ad Spend, Higher Performance",
      description:
        "Experience unparalleled efficiency and watch your marketing expenses plummet as your results soar with our advanced optimization.",
    },
    {
      icon: Shield,
      title: "Transparent Pricing",
      description:
        "No hidden fees or surprise charges. Monthly billing with no yearly contracts. We believe in getting paid based on performance only.",
    },
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            Improve Local Visibility | Why Choose CrossPostMe?
          </h2>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="bg-white rounded-xl p-6 shadow-sm hover:shadow-lg transition-all duration-300 group"
              >
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-600 transition-colors">
                  <Icon className="w-6 h-6 text-blue-600 group-hover:text-white transition-colors" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default WhyChoose;
